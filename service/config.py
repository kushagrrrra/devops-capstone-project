"""Application configuration, read from environment variables."""
import os

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)

SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Never ship the real key in code; override with an environment variable or a Kubernetes secret.
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

# HTTPS redirect, HSTS and secure cookies. Off by default so local HTTP, tests and
# in-cluster health probes work; set FORCE_HTTPS=true when the service is served over TLS.
FORCE_HTTPS = os.getenv("FORCE_HTTPS", "false").lower() == "true"

# Browser origins allowed to call the API (comma-separated). Never "*".
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
    if origin.strip()
]
