# Use the official sglang image
FROM lmsysorg/sglang:v0.4.7.post1-cu124

# Install libgl for opencv support & Noto fonts for Chinese characters
RUN apt-get update && \
    apt-get install -y \
        fonts-noto-core \
        fonts-noto-cjk \
        fontconfig \
        libgl1 && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install mineru latest
RUN python3 -m pip install -U 'mineru[core]' --break-system-packages && \
    python3 -m pip cache purge

# Install COS SDK for Tencent Cloud storage
RUN python3 -m pip install cos-python-sdk-v5 --break-system-packages

# Download models and update the configuration file
RUN /bin/bash -c "mineru-models-download -s huggingface -m all"

# Copy COS integration files
COPY mineru/cli/common.py /usr/local/lib/python3.12/dist-packages/mineru/cli/common.py
COPY mineru/data/data_reader_writer/__init__.py /usr/local/lib/python3.12/dist-packages/mineru/data/data_reader_writer/__init__.py
COPY mineru/data/data_reader_writer/cos_writer.py /usr/local/lib/python3.12/dist-packages/mineru/data/data_reader_writer/cos_writer.py

# Set working directory
WORKDIR /app

# Set the entry point to activate the virtual environment and run the command line tool
ENTRYPOINT ["/bin/bash", "-c", "export MINERU_MODEL_SOURCE=local && exec \"$@\"", "--"]