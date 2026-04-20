# --- STAGE 1: Build the React Frontend ---
FROM node:18-slim AS build-stage
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# --- STAGE 2: Build the FastAPI Backend ---
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy the rest of the backend code
COPY . .

# Copy the pre-built React frontend from Stage 1
# We copy it into static/dist since FastAPI is configured to serve from there.
COPY --from=build-stage /app/static/dist ./static/dist

EXPOSE 8000

# Command to run the application using Gunicorn
CMD ["gunicorn", "app.app:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
