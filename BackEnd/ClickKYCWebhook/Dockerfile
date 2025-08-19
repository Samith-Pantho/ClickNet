FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    gcc \
    libc-dev \
    python3-dev \
    build-essential \
    libffi-dev \
    wget \
    unzip \
    curl \
    jq \
    dos2unix \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip

# Install Ngrok
RUN wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -O ngrok.tgz && \
    tar xvzf ngrok.tgz && \
    rm ngrok.tgz && \
    chmod +x ngrok

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NGROK_AUTH_TOKEN="" 

EXPOSE 8888

CMD ["uvicorn", "BackEnd.ClickKYCWebhook.index:app", "--host", "0.0.0.0", "--port", "8888"]