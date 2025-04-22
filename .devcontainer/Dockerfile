FROM mcr.microsoft.com/devcontainers/python:3.10

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    wget \
    ffmpeg \
    libsm6 \
    libxext6 \
    software-properties-common \
    procps \
    psmisc \
    net-tools \
    iproute2 \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://get.docker.com | sh

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install CUDA dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    nvidia-cuda-toolkit \
    nvidia-cuda-toolkit-gcc \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for ML and development with CUDA support
RUN pip install --upgrade pip \
    && pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    transformers \
    datasets \
    accelerate \
    huggingface_hub \
    langchain \
    pytest \
    black \
    isort \
    pylint \
    jupyter \
    jupyterlab \
    ipywidgets

# Create a non-root user with sudo access
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Add user to docker group (with checks to avoid errors if group/user already exists)
RUN if getent group $USER_GID > /dev/null 2>&1; then \
        echo "Group with GID $USER_GID already exists"; \
    elif getent group $USERNAME > /dev/null 2>&1; then \
        echo "Group $USERNAME already exists"; \
    else \
        groupadd --gid $USER_GID $USERNAME; \
    fi \
    && if id -u $USERNAME > /dev/null 2>&1; then \
        echo "User $USERNAME already exists"; \
    else \
        useradd --uid $USER_UID --gid $(getent group $USER_GID | cut -d: -f1 || echo $USER_GID) -m $USERNAME; \
    fi \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && usermod -aG docker $USERNAME

# Set up working directory
WORKDIR /workspace

# Set up entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sleep", "infinity"]
