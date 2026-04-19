# Use an official Python runtime as a parent image
FROM python:3.14-slim

# Set environment variables
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We use a simple pip install for deployment compatibility
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
# We use 0.0.0.0 to allow external connections to the container
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]
