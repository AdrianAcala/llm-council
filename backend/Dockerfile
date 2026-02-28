# Backend Dockerfile for LLM Council
FROM python:3.12-slim

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock ./
COPY backend/ ./backend/

# Install uv
RUN pip install uv

# Install dependencies using uv
RUN uv pip install --system -e "."

# Create data directory
RUN mkdir -p /app/data/conversations

# Expose the backend port
EXPOSE 8001

# Run the FastAPI server
CMD ["python", "-m", "backend.main"]
