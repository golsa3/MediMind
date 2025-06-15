# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the orchestrator via Flask or other WSGI if needed
CMD ["python", "test_orchestrator.py"]
