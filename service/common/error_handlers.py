"""Return every error as JSON instead of an HTML page."""
from http import HTTPStatus

from flask import jsonify

from service.models import DataValidationError


def _error(status, message):
    return jsonify(status=status.value, error=status.phrase, message=str(message)), status


def register_error_handlers(app):
    """Attach JSON error handlers to the app."""

    @app.errorhandler(DataValidationError)
    def request_validation_error(error):
        return _error(HTTPStatus.BAD_REQUEST, error)

    @app.errorhandler(HTTPStatus.BAD_REQUEST)
    def bad_request(error):
        return _error(HTTPStatus.BAD_REQUEST, error)

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def not_found(error):
        return _error(HTTPStatus.NOT_FOUND, error)

    @app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
    def method_not_supported(error):
        return _error(HTTPStatus.METHOD_NOT_ALLOWED, error)

    @app.errorhandler(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    def mediatype_not_supported(error):
        return _error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, error)

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_server_error(error):  # pragma: no cover
        app.logger.error(str(error))
        return _error(HTTPStatus.INTERNAL_SERVER_ERROR, "An internal error occurred")
