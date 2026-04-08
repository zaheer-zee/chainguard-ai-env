FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for Hugging Face Spaces / Web Server
EXPOSE 8000

# Start Uvicorn to serve the API
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
