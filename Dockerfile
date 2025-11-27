FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
      PYTHONDONTWRITEBYTECODE=1

# Create application directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      && rm -rf /var/lib/apt/lists/*

# Create SQLite data directory (writable for user 1001)
RUN mkdir -p /app/db && chown -R 1001:1001 /app/db
RUN chmod -R 775 /app

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Expose Django/Gunicorn port
EXPOSE 14009

# Set default user — matches docker-compose
USER 1001:1001