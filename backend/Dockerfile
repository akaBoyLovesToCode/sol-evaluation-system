# Use the recommended modern, slim Python image
FROM python:3.11-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
# This layer is cached by Docker, speeding up subsequent builds if requirements don't change
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the application will run on
EXPOSE 8000

# Command to run the application using Gunicorn for production
# Gunicorn is a robust WSGI server for running Python web applications
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
