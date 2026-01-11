FROM nvidia/cuda:12.8.0-devel-ubuntu24.04
RUN apt update
RUN apt install -y curl git
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv python install 3.12
RUN uv venv /opt/venv/ --seed
RUN --mount=type=cache,target=/opt/venv . /opt/venv/bin/activate && uv pip install faster-whisper uvicorn python-multipart pydantic
COPY ./app /opt/app
WORKDIR /opt/app
CMD . /opt/venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000
