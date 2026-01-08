FROM public.ecr.aws/deep-learning-containers/pytorch-inference-arm64:2.6.0-gpu-py312-cu124-ubuntu22.04-ec2-v1.42 as base

FROM public.ecr.aws/amazonlinux/amazonlinux:2023
RUN yum update
RUN yum install -y tar gzip
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH=/root/.local/bin/:$PATH
ENV VIRTUAL_ENV=/opt/venv
ENV CUDA_PATH=/opt/cuda/lib64
ENV LD_LIBRARY_PATH="$CUDA_PATH:$LD_LIBRARY_PATH"
RUN uv python install 3.12 --default
RUN uv venv $VIRTUAL_ENV
RUN . $VIRTUAL_ENV/bin/activate && \
    uv pip install awscli && \
    python -m awscli s3 cp s3://persistent-data-ef4ba2/develop/python/libs/ctranslate2-arm64-cuda-v4.6.3.tar.gz /tmp/
WORKDIR /tmp/
RUN tar -xvf ctranslate2-arm64-cuda-v4.6.3.tar.gz
WORKDIR /tmp/ctranslate2-arm64-cuda
RUN . /opt/venv/bin/activate && \
    uv pip install numpy pyyaml && \
    ./install.sh
COPY --from=base /usr/lib/aarch64-linux-gnu/libcudnn.so.9.1.0 $CUDA_PATH/libcudnn.so.9
COPY --from=base /usr/local/cuda-12.4/targets/sbsa-linux/lib/libcublas.so.12.4.5.8 $CUDA_PATH/libcublas.so.12
COPY --from=base /usr/local/cuda-12.4/targets/sbsa-linux/lib/libcublasLt.so.12.4.5.8 $CUDA_PATH/libcublasLt.so.12
