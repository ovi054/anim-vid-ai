FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies (same as before)
RUN apt-get update && apt-get install -y \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libpango1.0-dev \
    ffmpeg \
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    dvipng \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Upgrade pip just in case, then install requirements
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Permissions
RUN mkdir -p media && chmod -R 777 /app

EXPOSE 7860

CMD ["python", "app.py"]
