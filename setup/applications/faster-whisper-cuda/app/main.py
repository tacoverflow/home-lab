"""
Faster Whisper Streaming API
A simple FastAPI wrapper for faster-whisper with audio and text streaming support.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel
from pydantic import BaseModel
from typing import Optional, Literal
import tempfile
import os
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Faster Whisper API",
    description="Simple API for audio transcription with streaming support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model instance
model: Optional[WhisperModel] = None

# Configuration
class ModelConfig(BaseModel):
    model_size: Literal["tiny", "base", "small", "medium", "large-v2", "large-v3", "distil-large-v3"] = "distil-large-v3"
    device: Literal["cpu", "cuda"] = "cuda"
    compute_type: Literal["int8", "int8_float16", "float16", "float32"] = "float16"

class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    segments: list = []

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Load the model on startup"""
    global model
    config = ModelConfig()
    logger.info(f"Loading Whisper model: {config.model_size} on {config.device}")
    try:
        model = WhisperModel(
            config.model_size,
            device=config.device,
            compute_type=config.compute_type
        )
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global model
    model = None
    logger.info("Model unloaded")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the API and model are ready"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

# Model info endpoint
@app.get("/model-info")
async def model_info():
    """Get current model information"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    import ctranslate2
    return {
        "device": model.device,
        "compute_type": model.compute_type,
        "cuda_available": ctranslate2.get_cuda_device_count() > 0,
        "cuda_device_count": ctranslate2.get_cuda_device_count()
    }

# Standard transcription endpoint
@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Query(None, description="Language code (e.g., 'en', 'es')"),
    task: Literal["transcribe", "translate"] = Query("transcribe", description="Task type"),
    beam_size: int = Query(5, ge=1, le=10, description="Beam size for decoding"),
    vad_filter: bool = Query(True, description="Enable VAD filter")
):
    """
    Transcribe an audio file and return the complete result.
    
    Supports various audio formats: mp3, mp4, wav, flac, ogg, etc.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Save uploaded file to temporary location
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info(f"Processing file: {file.filename}")
        
        # Transcribe
        segments, info = model.transcribe(
            tmp_path,
            language=language,
            task=task,
            beam_size=beam_size,
            vad_filter=vad_filter
        )
        
        # Collect all segments
        segment_list = []
        full_text = []
        
        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            }
            segment_list.append(segment_data)
            full_text.append(segment.text)
        
        result = {
            "text": " ".join(full_text),
            "language": info.language,
            "segments": segment_list
        }
        
        logger.info(f"Transcription complete. Language: {info.language}")
        return result
        
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# Streaming transcription endpoint
@app.post("/transcribe/stream")
async def transcribe_stream(
    file: UploadFile = File(...),
    language: Optional[str] = Query(None, description="Language code"),
    task: Literal["transcribe", "translate"] = Query("transcribe"),
    beam_size: int = Query(5, ge=1, le=10),
    vad_filter: bool = Query(True)
):
    """
    Transcribe an audio file and stream segments as they are processed.
    
    Returns an SSE (Server-Sent Events) stream with real-time transcription results.
    Each event contains a JSON object with segment information.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Save uploaded file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {e}")
    
    async def generate_stream():
        """Generator function for streaming segments"""
        try:
            logger.info(f"Starting streaming transcription for: {file.filename}")
            
            segments, info = model.transcribe(
                tmp_path,
                language=language,
                task=task,
                beam_size=beam_size,
                vad_filter=vad_filter
            )
            
            # Send language info first
            language_event = {
                "type": "language",
                "language": info.language,
                "language_probability": info.language_probability
            }
            yield f"data: {json.dumps(language_event)}\n\n"
            
            # Stream each segment as it's processed
            for segment in segments:
                segment_data = {
                    "type": "segment",
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text
                }
                yield f"data: {json.dumps(segment_data)}\n\n"
            
            # Send completion event
            completion_event = {"type": "complete"}
            yield f"data: {json.dumps(completion_event)}\n\n"
            
            logger.info("Streaming transcription complete")
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_event = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"
        
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Language detection endpoint
@app.post("/detect-language")
async def detect_language(
    file: UploadFile = File(...)
):
    """
    Detect the language of an audio file without transcribing.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info(f"Detecting language for: {file.filename}")
        
        # Transcribe just the first few seconds to detect language
        segments, info = model.transcribe(tmp_path, beam_size=1)
        
        return {
            "language": info.language,
            "language_probability": info.language_probability
        }
        
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# Root endpoint
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Faster Whisper API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "model_info": "/model-info",
            "transcribe": "/transcribe",
            "transcribe_stream": "/transcribe/stream",
            "detect_language": "/detect-language",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11435)
