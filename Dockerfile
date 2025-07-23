FROM python:3.11-slim   # you can keep 3.9 if you want

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# (Optional) system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better caching
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of your code (including app.py)
COPY . .

# Streamlit default port on HF Spaces is 7860, but 8501 is fine too
EXPOSE 8501

# Healthcheck (optional, but needs full syntax)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
