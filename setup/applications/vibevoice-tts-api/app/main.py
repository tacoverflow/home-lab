from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import torch
import copy
import io
import wave
import numpy as np

# processor
from vibevoice.processor.vibevoice_streaming_processor import VibeVoiceStreamingProcessor
# model loader for inference
from vibevoice.modular.modeling_vibevoice_streaming_inference import VibeVoiceStreamingForConditionalGenerationInference

app = FastAPI(title="VibeVoice TTS API")

# Global variables for model (loaded once at startup)
model = None
processor = None
all_prefilled_outputs = None

class TTSRequest(BaseModel):
    text: str
    voice: str = "en-Emma_woman"  # default voice

@app.on_event("startup")
async def load_model():
    """Load model once at startup"""
    global model, processor, all_prefilled_outputs
    
    model_id = "microsoft/VibeVoice-Realtime-0.5B"
    voice_sample = "$VOICE_PATH/en-Emma_woman.pt"
    
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

    # Convert tensor to numpy array
    audio_array = outputs.speech_outputs[0].cpu().numpy()
    
    # Create WAV file in memory
    wav_buffer = io.BytesIO()
    
    # Get sample rate from processor (usually 24000)
    sample_rate = processor.feature_extractor.sampling_rate
    
    # Ensure audio is in the right format (int16)
    if audio_array.dtype != np.int16:
        # Assuming audio is in float format [-1, 1], convert to int16
        audio_array = (audio_array * 32767).astype(np.int16)
    
    # Write WAV file
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes for int16
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_array.tobytes())
    
    wav_buffer.seek(0)
    return wav_buffer.read()

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
        audio_bytes = generate_audio(request.text)
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=output.wav"
            }
        )
    except Exception as e:
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
