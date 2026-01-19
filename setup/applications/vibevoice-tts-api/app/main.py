import asyncio
import os
import threading
from pathlib import Path
from typing import Iterator, Optional

import numpy as np
import torch
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketState

from vibevoice.modular.modeling_vibevoice_streaming_inference import (
    VibeVoiceStreamingForConditionalGenerationInference,
)
from vibevoice.processor.vibevoice_streaming_processor import (
    VibeVoiceStreamingProcessor,
)
from vibevoice.modular.streamer import AudioStreamer

import copy

import json
import base64
from allosaurus.app import read_recognizer

import tempfile
import io
import scipy.io.wavfile as wavfile

import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)
model_path = os.environ.get('MODEL_PATH', '/opt/app/model/VibeVoice-Realtime-0.5B')
voice_path = os.environ.get('VOICE_PATH', '/opt/VibeVoice/demo/voices/streaming_model')
voice_file = os.environ.get('VOICE_FILE', 'en-Emma_woman.pt')
SAMPLE_RATE = 24_000

# Comprehensive map for Allosaurus English symbols
IPA_MAP = {
    # aa (Open Mouth)
    'a': 'aa', 'ɑ': 'aa', 'æ': 'aa', 'ʌ': 'aa', 'ə': 'aa', 
    'ŋ': 'aa', 'k': 'aa', 'ɡ': 'aa', 'ɹ': 'aa', 'ɻ': 'aa', 'ɻ̩': 'aa',
    
    # ih (Teeth/Smile)
    'i': 'ih', 'ɪ': 'ih', 'j': 'ih', 'θ': 'ih', 'ð': 'ih',
    's': 'ih', 'z': 'ih', 't': 'ih', 'd': 'ih', 'n': 'ih', 'l': 'ih',
    
    # ou (Pursed Lips)
    'u': 'ou', 'ʊ': 'ou', 'w': 'ou', 'p': 'ou', 'b': 'ou', 'm': 'ou',
    
    # ee (Mid-Open Smile)
    'e': 'ee', 'ɛ': 'ee',
    
    # oh (Rounded Open)
    'o': 'oh', 'ɔ': 'oh'
}


class StreamingTTSService:
    def __init__(self, inference_steps: int = 5):
        self.model_path = model_path
        self.inference_steps = inference_steps
        self.device = torch.device("cuda")
        self.processor: Optional[VibeVoiceStreamingProcessor] = None
        self.model: Optional[VibeVoiceStreamingForConditionalGenerationInference] = None
        self.default_voice = None
        self.allo_model = None
        self.state = None

    def load(self):
        self.processor = VibeVoiceStreamingProcessor.from_pretrained(self.model_path)
        
        self.model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
            self.model_path,
            torch_dtype=torch.bfloat16,
            device_map='cuda',
            attn_implementation="flash_attention_2",
        )
        self.model.eval()
        
        self.model.model.noise_scheduler = self.model.model.noise_scheduler.from_config(
            self.model.model.noise_scheduler.config,
            algorithm_type="sde-dpmsolver++",
            beta_schedule="squaredcos_cap_v2",
        )
        self.model.set_ddpm_inference_steps(num_steps=self.inference_steps)
        
        # Load default voice preset
        self.default_voice = torch.load(f"{voice_path}/{voice_file}", map_location=self.device, weights_only=False)
        
        self.allo_model = read_recognizer()

    def stream(self, text: str, cfg_scale: float = 1.5) -> Iterator[np.ndarray]:
        # Prepare inputs
        processed = self.processor.process_input_with_cached_prompt(
            text=text.strip(),
            cached_prompt=self.default_voice,
            padding=True,
            return_tensors="pt",
            return_attention_mask=True,
        )
        inputs = {k: v.to(self.device) if hasattr(v, "to") else v for k, v in processed.items()}
        
        # Setup streaming
        audio_streamer = AudioStreamer(batch_size=1, stop_signal=None, timeout=None)
        stop_event = threading.Event()
        
        # Run generation in thread
        def generate():
            self.model.generate(
                **inputs,
                max_new_tokens=None,
                cfg_scale=cfg_scale,
                tokenizer=self.processor.tokenizer,
                generation_config={"do_sample": False, "temperature": 1.0, "top_p": 1.0},
                audio_streamer=audio_streamer,
                stop_check_fn=stop_event.is_set,
                verbose=False,
                refresh_negative=True,
                all_prefilled_outputs=copy.deepcopy(self.default_voice),
            )
        
        thread = threading.Thread(target=generate, daemon=True)
        thread.start()
        
        # Yield audio chunks
        for audio_chunk in audio_streamer.get_stream(0):
            if torch.is_tensor(audio_chunk):
                audio_chunk = audio_chunk.detach().cpu().to(torch.float32).numpy()
            else:
                audio_chunk = np.asarray(audio_chunk, dtype=np.float32)
            
            audio_chunk = audio_chunk.reshape(-1)
            peak = np.max(np.abs(audio_chunk)) if audio_chunk.size else 0.0
            if peak > 1.0:
                audio_chunk = audio_chunk / peak
            
            yield audio_chunk.astype(np.float32, copy=False)
        
        stop_event.set()
        thread.join()

    def chunk_to_pcm16(self, chunk: np.ndarray) -> bytes:
        chunk = np.clip(chunk, -1.0, 1.0)
        pcm = (chunk * 32767.0).astype(np.int16)
        return pcm.tobytes()

    def get_visemes_with_context(self, current_chunk):
        pcm16_audio = (current_chunk * 32767).astype(np.int16)
        with tempfile.NamedTemporaryFile(suffix=".wav", dir="/dev/shm", delete=True) as temp_wav:
            wavfile.write(temp_wav.name, 16000, pcm16_audio)
            raw_str = self.allo_model.recognize(temp_wav.name, timestamp=True)
        current_visemes = []
        lines = raw_str.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 3:
                start_time = float(parts[0])
                # Only keep phonemes that actually belong to the NEW part of the audio
                if start_time >= 0.100:
                    adjusted_time = start_time - 0.100 # Normalize back to 0.0
                    symbol = parts[2][0]

                    # get phoneme audio level
                    duration = float(parts[1])
                    audio_start = int(start_time * 16000)
                    audio_end = int((start_time + duration) * 16000)
                    audio_slice = current_chunk[audio_start:audio_end]
                    level = 0.0
                    if len(audio_slice) > 0:
                        # Root Mean Square calculation
                        rms = np.sqrt(np.mean(np.square(audio_slice)))
                        # 3. Normalize to 0.0 - 1.0
                        # Note: Speech RMS rarely hits 1.0. 
                        # A value of 0.2 is usually quite loud.
                        level = np.clip(rms, 0.0, 1.0)

                    current_visemes.append({
                        "t": round(adjusted_time, 3),
                        "d": duration,
                        "l": level,
                        "v": IPA_MAP.get(symbol, 'aa')
                    })
        return current_visemes

    def get_visemes_from_chunk(self, audio_bytes):
        pcm16_audio = (audio_bytes * 32767).astype(np.int16)
        # Convert PCM16 bytes to float32 numpy (Allosaurus requirement)
        visemes = []
        with tempfile.NamedTemporaryFile(suffix=".wav", dir="/dev/shm", delete=True) as temp_wav:
            wavfile.write(temp_wav.name, 16000, pcm16_audio)
    
            # Run inference (Allosaurus expects 16kHz)
            # Output format: "start_time duration phoneme"
            results = self.allo_model.recognize(temp_wav.name, timestamp=True)
    
            for line in results.split('\n'):
                parts = line.split()
                if len(parts) >= 3:
                    start_time = float(parts[0])
                    end_time = float(parts[1])
                    phoneme = parts[2]
                    v_shape = IPA_MAP.get(phoneme, IPA_MAP.get(phoneme[0], 'aa'))
                    visemes.append({
                        "t1": start_time,
                        "t2": end_time,
                        "v": v_shape
                    })
        return visemes


app = FastAPI()



@app.on_event("startup")
async def _startup():
    service = StreamingTTSService()
    service.load()
    app.state.tts_service = service


@app.get("/health")
async def health_check():
    """Check if the API and model are ready"""
    if app.state.tts_service.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}


@app.websocket("/stream")
async def websocket_stream(ws: WebSocket):
    await ws.accept()
    text = ws.query_params.get("text", "")
    
    service: StreamingTTSService = app.state.tts_service
    iterator = service.stream(text)

    service.state = {
        "last_100ms": np.zeros(1600, dtype=np.int16), # 100ms at 16kHz
        "global_time_offset": 0.0
    }
    
    try:
        while ws.client_state == WebSocketState.CONNECTED:
            chunk = await asyncio.to_thread(next, iterator, None)
            if chunk is None:
                break
            # chunk_visemes = service.get_visemes_with_context(chunk)
            # pcm16_chunk = service.chunk_to_pcm16(chunk)
            payload = service.chunk_to_pcm16(chunk)
            await ws.send_bytes(payload)
            combined_audio = np.concatenate([service.state["last_100ms"], chunk])
            service.state["last_100ms"] = chunk[-1600:]
            asyncio.create_task(process_and_send_visemes(ws, combined_audio, service))
            # chunk_visemes = service.get_visemes_with_context(chunk)
            # payload = json.dumps({
            #     "audio": base64.b64encode(pcm16_chunk).decode('utf-8'),
            #     "visemes": chunk_visemes
            # })
            # await ws.send_text(payload)
    finally:
        if ws.client_state == WebSocketState.CONNECTED:
            await ws.close()

async def process_and_send_visemes(websocket, chunk, service):
    loop = asyncio.get_event_loop()
    # This runs your existing Allosaurus logic in the thread pool
    visemes = await loop.run_in_executor(executor, service.get_visemes_with_context, chunk)
    # Send the visemes as soon as they are ready
    await websocket.send_json({
        "visemes": visemes
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
