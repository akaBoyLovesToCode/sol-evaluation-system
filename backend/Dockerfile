# Simple Railway-compatible Dockerfile
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements file (fallback to pip)
COPY requirements.txt .

# Install dependencies with pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH="/app"
ENV FLASK_ENV=production

# Expose port (Railway will set $PORT)
EXPOSE 5001

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "run:app"]