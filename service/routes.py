"""REST API routes for the Account resource.

POST   /accounts        create
GET    /accounts        list
GET    /accounts/<id>   read
PUT    /accounts/<id>   update
DELETE /accounts/<id>   delete
"""
from http import HTTPStatus

from flask import Blueprint, abort, current_app, jsonify, request, url_for

from service.models import Account

api = Blueprint("api", __name__)


def check_content_type(media_type):
    """Abort with 415 unless the request has the expected Content-Type."""
    content_type = request.headers.get("Content-Type", "")
    if content_type.split(";")[0].strip() != media_type:
        abort(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {media_type}")


def get_account_or_404(account_id):
    account = Account.find(account_id)
    if not account:
        abort(HTTPStatus.NOT_FOUND, f"Account with id [{account_id}] could not be found.")
    return account


@api.route("/health")
def health():
    """Liveness/readiness probe for Kubernetes."""
    return jsonify(status="OK"), HTTPStatus.OK


@api.route("/")
def index():
    """Service metadata."""
    return jsonify(
        name="Account REST API Service",
        version="1.0",
        paths=url_for("api.list_accounts", _external=True),
    ), HTTPStatus.OK


@api.route("/accounts", methods=["POST"])
def create_accounts():
    """Create an account from the JSON body."""
    current_app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json(silent=True))
    account.create()
    location = url_for("api.read_account", account_id=account.id, _external=True)
    return jsonify(account.serialize()), HTTPStatus.CREATED, {"Location": location}


@api.route("/accounts", methods=["GET"])
def list_accounts():
    """List every account (empty list when there are none)."""
    current_app.logger.info("Request to list Accounts")
    return jsonify([account.serialize() for account in Account.all()]), HTTPStatus.OK


@api.route("/accounts/<int:account_id>", methods=["GET"])
def read_account(account_id):
    """Read a single account by id."""
    current_app.logger.info("Request to read Account %s", account_id)
    return jsonify(get_account_or_404(account_id).serialize()), HTTPStatus.OK


@api.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):
    """Replace an account's fields with the JSON body."""
    current_app.logger.info("Request to update Account %s", account_id)
    check_content_type("application/json")
    account = get_account_or_404(account_id)
    account.deserialize(request.get_json(silent=True))
    account.id = account_id
    account.update()
    return jsonify(account.serialize()), HTTPStatus.OK


@api.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):
    """Delete an account; succeeds even if it is already gone."""
    current_app.logger.info("Request to delete Account %s", account_id)
    account = Account.find(account_id)
    if account:
        account.delete()
    return "", HTTPStatus.NO_CONTENT
