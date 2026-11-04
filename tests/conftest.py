"""Shared pytest fixtures.

Uses DATABASE_URI when set (PostgreSQL in CI and Tekton), otherwise an in-memory SQLite DB.
"""
import os

import pytest

from service import create_app
from service.models import db


@pytest.fixture(scope="session")
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URI", "sqlite://"),
    })
    yield app


@pytest.fixture(autouse=True)
def clean_db(app):
    """Start every test with empty tables."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield
        db.session.remove()


@pytest.fixture
def client(app):
    return app.test_client()
