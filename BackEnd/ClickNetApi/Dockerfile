FROM python:3.11-slim

WORKDIR /app

# Preinstall system libraries needed for building and WeasyPrint
RUN apt-get update && apt-get install -y \
    apt-utils \
    gcc \
    libc-dev \
    python3-dev \
    build-essential \
    libffi-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libglib2.0-dev \
    shared-mime-info \
    fonts-liberation \
    default-libmysqlclient-dev \
    curl \
    wget \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose HTTPS port
EXPOSE 8443

CMD ["uvicorn", "BackEnd.ClickNetApi.index:app", "--host", "0.0.0.0", "--port", "8443"]
