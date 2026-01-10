FROM nvidia/cuda:12.8.0-devel-ubuntu24.04
RUN apt update
RUN apt install -y curl git
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN . $HOME/.local/bin/env && uv python install 3.12
RUN uv venv /opt/venv/ --seed
RUN . /opt/venv/bin/activate && uv pip install torch transformers==4.51.3 soundfile accelerate peft diffusers fastapi pydantic 
RUN . /opt/venv/bin/activate && uv pip install flash-attn --no-build-isolation
WORKDIR /opt/
RUN git clone https://github.com/microsoft/VibeVoice.git
WORKDIR /opt/VibeVoice
RUN pip install -e .
COPY /app /opt/app
WORKDIR /opt/app
