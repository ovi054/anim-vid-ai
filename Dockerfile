FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
# ADDED: texlive-latex-recommended, cm-super (Crucial for preventing hangs)
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libpango1.0-dev \
    ffmpeg \
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    cm-super \
    dvipng \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Create media directory and fix permissions
RUN mkdir -p media && chmod -R 777 /app

# Set Manim to use a temporary directory for caching to avoid locks
ENV MANIM_CACHE_DIR="/tmp/manim_cache"

EXPOSE 7860

CMD ["python", "app.py"]
