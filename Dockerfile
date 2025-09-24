FROM python:3.13-slim

# Set working directory to /app inside the container
# This creates the container's project root where all our code will live
# Local structure: lang-app/
# Container structure: /app/
# 
# Before WORKDIR: Container has no project folder
# After WORKDIR:  Container has /app/ as the working directory
# 
# All subsequent COPY commands will copy files TO /app/
# All subsequent RUN commands will execute FROM /app/
# All docker-compose paths reference /app/ as the container's project root
WORKDIR /app

# NOTE: PYTHONPATH, PYTHONUNBUFFERED, PYTHONPYCACHEPREFIX, PYTHONDONTWRITEBYTECODE are also defined
# in our docker-compose files for environment-specific configuration. This Dockerfile provides fallback
# defaults in case someone runs the container directly without docker-compose (e.g., docker run lang-app).

# Set Python environment variables
# PYTHONPATH: Set the Python module search path to /app so Python can find our modules
# from anywhere in the container without needing sys.path.append() or relative imports
ENV PYTHONPATH=/app

# PYTHONUNBUFFERED: Ensure Python output is sent straight to terminal without buffering
# This is crucial for Docker logging - without it, logs might be delayed or lost
ENV PYTHONUNBUFFERED=1

# PYTHONPYCACHEPREFIX: Set default location for .pyc bytecode files
# This is the fallback behavior - allows .pyc files in development for faster startup
# Production environments will override this to "" (disable) or use different settings
ENV PYTHONPYCACHEPREFIX=/app/__pycache__

# PYTHONDONTWRITEBYTECODE: Default to allowing .pyc file creation (0 = allow, 1 = disable)
# This provides a development-friendly default that can be overridden per environment
# Production will override this to 1 to prevent .pyc files for cleaner deployments
ENV PYTHONDONTWRITEBYTECODE=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements .

# Install Python dependencies (this layer will be cached if requirements doesn't change)
RUN pip install --no-cache-dir -r requirements

# Download and cache German models during build
RUN python -m spacy download de_core_news_lg
RUN python -c "import stanza; stanza.download('de')"

# # Copy custom models
# COPY models/ /app/models/

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]