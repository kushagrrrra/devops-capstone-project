"""Accounts microservice package: builds and configures the Flask app."""
import logging
import sys

from flask import Flask

from service import config
from service.models import init_db


def create_app(test_config=None):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config)
    if test_config:
        app.config.update(test_config)

    # Import inside the factory so blueprints bind to this app instance
    from service.routes import api
    from service.common.error_handlers import register_error_handlers

    app.register_blueprint(api)
    register_error_handlers(app)

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    )

    try:
        init_db(app)
    except Exception as error:  # pragma: no cover - only hit when the DB is down
        app.logger.critical("%s: Cannot continue", error)
        sys.exit(4)

    app.logger.info("Accounts service initialised")
    return app
