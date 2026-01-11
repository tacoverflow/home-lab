FROM nvidia/cuda:12.8.0-devel-ubuntu24.04
RUN apt update
RUN apt install -y curl git
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv python install 3.12
RUN uv venv /opt/venv/ --seed
RUN . /opt/venv/bin/activate && uv pip install torch transformers==4.51.3 soundfile accelerate peft diffusers fastapi pydantic uvicorn
RUN . /opt/venv/bin/activate && uv pip install flash-attn --no-build-isolation
WORKDIR /opt/
RUN git clone https://github.com/microsoft/VibeVoice.git
WORKDIR /opt/VibeVoice
RUN . /opt/venv/bin/activate && uv pip install -e .
COPY /app /opt/app
WORKDIR /opt/app/model
RUN . /opt/venv/bin/activate && python -c \
    'from huggingface_hub import snapshot_download; snapshot_download("microsoft/VibeVoice-Realtime-0.5B", local_dir="VibeVoice-Realtime-0.5B")'
WORKDIR /opt/app
ENV VOICE_PATH="/opt/VibeVoice/demo/voices/streaming_model"
ENV MODEL_PATH="/opt/app/model/VibeVoice-Realtime-0.5B"
CMD . /opt/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000
