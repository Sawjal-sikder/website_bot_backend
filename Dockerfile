# FROM python:3.12-slim
# ENV PYTHONUNBUFFERED=1
# WORKDIR /app
# RUN apt-get update && apt-get install -y \
#       build-essential \
#       libpq-dev \
#       && rm -rf /var/lib/apt/lists/*
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# EXPOSE 14009



FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
      build-essential \
      libpq-dev \
      && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose Django port
EXPOSE 14009

# migrations and collectstatic commands
RUN python manage.py migrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput