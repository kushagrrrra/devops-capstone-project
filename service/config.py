"""Application configuration, read from environment variables."""
import os

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)

SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Never ship the real key in code; override with an environment variable or a Kubernetes secret.
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
