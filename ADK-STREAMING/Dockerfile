FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent folder into /workspace/app/
# ADK web will scan /workspace/ and find the 'app' agent package
COPY app/ ./app/

# Cloud Run listens on port 8080
EXPOSE 8080

# Run from /workspace so ADK finds the 'app' agent inside it
CMD ["adk", "web", ".", "--host", "0.0.0.0", "--port", "8080"]
