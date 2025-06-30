FROM python:3.10-slim

# Install curl and unzip for Temporal CLI
RUN apt-get update && \
    apt-get install -y curl unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Temporal CLI (auto-detect arch)
RUN uname -m
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then \
        CLI_URL="https://github.com/temporalio/cli/releases/latest/download/temporal-linux-amd64"; \
    elif [ "$ARCH" = "aarch64" ]; then \
        CLI_URL="https://github.com/temporalio/cli/releases/latest/download/temporal-linux-arm64"; \
    else \
        echo "Unsupported architecture: $ARCH"; exit 1; \
    fi && \
    curl -L $CLI_URL -o /usr/local/bin/temporal && \
    chmod +x /usr/local/bin/temporal

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8000 7233

CMD ["python", "run_all.py"] 