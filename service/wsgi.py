"""WSGI entry point: `gunicorn service.wsgi:app`."""
from service import create_app

app = create_app()
