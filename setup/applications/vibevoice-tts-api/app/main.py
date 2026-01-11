from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import torch
import copy
import io
import os
import wave
import numpy as np
import soundfile as sf
import logging

# processor
from vibevoice.processor.vibevoice_streaming_processor import VibeVoiceStreamingProcessor
# model loader for inference
from vibevoice.modular.modeling_vibevoice_streaming_inference import VibeVoiceStreamingForConditionalGenerationInference

app = FastAPI(title="VibeVoice TTS API")

# Global variables for model (loaded once at startup)
model = None
processor = None
all_prefilled_outputs = None
voice_path = os.environ.get('VOICE_PATH', '/opt/VibeVoice/demo/voices/streaming_model')
model_path = os.environ.get('MODEL_PATH', '/opt/app/model/VibeVoice-Realtime-0.5B')

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-Emma_woman"  # default voice

@app.on_event("startup")
async def load_model():
    """Load model once at startup"""
    global model, processor, all_prefilled_outputs
    
    # model_id = "microsoft/VibeVoice-Realtime-0.5B"
    model_id = model_path
    voice_sample = f"{voice_path}/en-Emma_woman.pt"
    
    print("Loading VibeVoice model...")
    processor = VibeVoiceStreamingProcessor.from_pretrained(model_id)
    model = VibeVoiceStreamingForConditionalGenerationInference.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="cuda",
    )
    
    # Load default voice
    all_prefilled_outputs = torch.load(voice_sample, map_location="cuda", weights_only=False)
    print("Model loaded successfully!")

def generate_audio(text: str) -> bytes:
    """Generate audio from text and return WAV bytes"""
    
    try:
        logger.info(f"Processing text: {text}")
        
        inputs = processor.process_input_with_cached_prompt(
            text=text,
            cached_prompt=all_prefilled_outputs,
            padding=True,
            return_tensors="pt",
            return_attention_mask=True,
        )

        for k, v in inputs.items():
            if torch.is_tensor(v):
                inputs[k] = v.to("cuda")

        logger.info("Generating audio...")
        # Generate audio
        outputs = model.generate(
            **inputs,
            max_new_tokens=None,
            cfg_scale=1.0,
            tokenizer=processor.tokenizer,
            generation_config={'do_sample': False},
            verbose=False,
            all_prefilled_outputs=copy.deepcopy(all_prefilled_outputs) if all_prefilled_outputs is not None else None,
        )

        logger.info(f"Output type: {type(outputs)}")
        logger.info(f"Output attributes: {dir(outputs)}")
        
        # Convert tensor to numpy array
        audio_array = outputs.speech_outputs[0].cpu().numpy()
        logger.info(f"Audio array shape: {audio_array.shape}, dtype: {audio_array.dtype}")
        
        # Get sample rate from processor (usually 24000)
        sample_rate = processor.feature_extractor.sampling_rate
        logger.info(f"Sample rate: {sample_rate}")
        
        # VibeVoice outputs float32 in range [-1, 1], normalize and convert to int16
        audio_array = np.clip(audio_array, -1.0, 1.0)
        audio_array = (audio_array * 32767).astype(np.int16)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        
        # Write WAV file using wave module
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 2 bytes per sample (int16)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_array.tobytes())
        
        wav_buffer.seek(0)
        logger.info(f"WAV file size: {len(wav_buffer.getvalue())} bytes")
        return wav_buffer.read()
        
    except Exception as e:
        logger.error(f"Error in generate_audio: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return WAV audio stream
    
    Example usage:
    curl -X POST "http://localhost:8000/tts" \
         -H "Content-Type: application/json" \
         -d '{"text":"Hello world"}' \
         --output output.wav
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        logger.info(f"Received TTS request: {request.text}")
        audio_bytes = generate_audio(request.text)
        logger.info("Audio generated successfully")
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=output.wav"
            }
        )
    except Exception as e:
        logger.error(f"Error in text_to_speech endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")

@app.get("/health")
async def health_check():
    """Check if the service is running"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "cuda_available": torch.cuda.is_available()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
