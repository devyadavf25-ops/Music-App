FROM python:3.11-slim

# Install system dependencies including ffmpeg for audio processing and curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY . .

# Ensure start.sh has executable permissions
RUN chmod +x start.sh

# Render injects PORT environment variable (default fallback 8001)
ENV PORT=8001
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["./start.sh"]
