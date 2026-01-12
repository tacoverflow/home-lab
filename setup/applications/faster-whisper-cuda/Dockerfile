FROM nvidia/cuda:12.8.0-devel-ubuntu24.04
RUN apt update
RUN apt install -y curl git
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv python install 3.12
RUN uv venv /opt/venv/ --seed
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install torch faster-whisper uvicorn fastapi python-multipart pydantic
COPY ./app /opt/app
WORKDIR /opt/app/model
RUN --mount=type=cache,target=/root/.cache/huggingface . /opt/venv/bin/activate && python -c \
    'from huggingface_hub import snapshot_download; snapshot_download("Systran/faster-distil-whisper-large-v3", local_dir="distil-large-v3")'
ENV MODEL_PATH=/opt/app/model/distil-large-v3
WORKDIR /opt/app
CMD . /opt/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 11435
