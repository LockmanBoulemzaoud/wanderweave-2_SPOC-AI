FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps: build tools for Python packages, nginx and supervisor
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         build-essential \
         gcc \
         g++ \
         libpq-dev \
         libopenblas-dev \
         liblapack-dev \
         gfortran \
         python3-dev \
         libffi-dev \
         libssl-dev \
         nginx \
         supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies (full set for the app)
COPY requirements-full.txt ./
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements-full.txt

# Copy application code
COPY . /app

# Nginx and supervisor configuration (we'll copy configs into image)
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/app.conf

# Expose the single public port the container will listen on (nginx)
EXPOSE 8080

# Run supervisord in foreground (it will manage nginx, uvicorn and streamlit)
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
