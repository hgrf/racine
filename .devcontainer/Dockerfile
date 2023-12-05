FROM ubuntu:22.04

RUN apt update && apt install -y \
    ca-certificates \
    curl \
    default-jre \
    gnupg \
    npm \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python-is-python3 \
    watchman \
    wget \
    && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt update \
    && apt install -y docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g n && \
    n stable

ENTRYPOINT [ "/bin/bash" ]
