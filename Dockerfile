# Accounts microservice image
FROM python:3.12-slim

# No .pyc files, unbuffered logs, smaller layers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy only the application package (tests, docs and local data stay out)
COPY service/ ./service/

# Run as an unprivileged user
RUN useradd --uid 1000 --no-create-home --shell /usr/sbin/nologin theia
USER theia

EXPOSE ${PORT}

# DATABASE_URI, SECRET_KEY etc. are supplied at runtime, never baked into the image
CMD ["gunicorn", "--bind=0.0.0.0:8080", "--workers=1", "--log-level=info", "service.wsgi:app"]
