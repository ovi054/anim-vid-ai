FROM manimcommunity/manim:v0.19.0

USER root
WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Permissions for writing video files
RUN chmod -R 777 /app

# Run the app
CMD ["python", "app.py"]