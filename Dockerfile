# Use a lightweight Ubuntu-like image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt .
# Install python packages for linting and security scanning
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Add non-root user
RUN useradd -m appuser
USER appuser

WORKDIR /app

COPY mcp_tool.py /app/mcp_tool.py
ENV PYTHONUNBUFFERED=1
# entrypoint
ENTRYPOINT ["python", "/app/mcp_tool.py"]
