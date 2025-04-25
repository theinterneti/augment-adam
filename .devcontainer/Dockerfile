FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH=/usr/local/cuda/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Configure apt caching for faster builds
RUN rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install system dependencies and Python in a single layer to reduce image size
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # Essential build tools
    build-essential \
    # Python and development tools
    python3.10 \
    python3-pip \
    python3-dev \
    python3-venv \
    # Networking tools
    curl \
    wget \
    net-tools \
    iproute2 \
    # Version control
    git \
    # Image processing
    ffmpeg \
    libsm6 \
    libxext6 \
    # System utilities
    software-properties-common \
    procps \
    psmisc \
    htop \
    # Editors
    vim \
    nano \
    # Terminal multiplexer
    tmux \
    # Security and certificates
    openssh-client \
    ca-certificates \
    gnupg \
    lsb-release \
    # Create Python symlinks
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/python3.10 /usr/bin/python3

# Install Docker CLI
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    curl -fsSL https://get.docker.com | sh

# Install Node.js LTS (if needed)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install Python packages for ML and development
# Use a requirements file to leverage build cache better
# Note: requirements.txt will be mounted from the workspace
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install --upgrade pip \
    && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Create a non-root user with sudo access
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Add user to docker group (with checks to avoid errors if group/user already exists)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    if getent group $USER_GID > /dev/null 2>&1; then \
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
