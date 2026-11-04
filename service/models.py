"""Account model and persistence helpers."""
import logging
from datetime import date

from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

db = SQLAlchemy()


class DataValidationError(Exception):
    """Raised when incoming data is missing or malformed."""


def init_db(app):
    """Bind the database to the app and create tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()


class Account(db.Model):
    """A customer account."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(32), nullable=True)
    date_joined = db.Column(db.Date(), nullable=False, default=date.today)

    def __repr__(self):
        return f"<Account {self.name} id=[{self.id}]>"

    # ---------- persistence ----------
    def create(self):
        """Insert this account into the database."""
        logger.info("Creating %s", self.name)
        self.id = None  # let the database assign the id
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Save changes to an existing account."""
        logger.info("Updating %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Remove this account from the database."""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    # ---------- serialisation ----------
    def serialize(self):
        """Return the account as a dict."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "address": self.address,
            "phone_number": self.phone_number,
            "date_joined": self.date_joined.isoformat(),
        }

    def deserialize(self, data):
        """Load the account from a dict, validating required fields."""
        if not isinstance(data, dict):
            raise DataValidationError("Invalid Account: body of request contained bad or no data")
        try:
            self.name = data["name"]
            self.email = data["email"]
            self.address = data["address"]
            self.phone_number = data.get("phone_number")
            joined = data.get("date_joined")
            self.date_joined = date.fromisoformat(joined) if joined else date.today()
        except KeyError as error:
            raise DataValidationError(f"Invalid Account: missing {error.args[0]}") from error
        except (TypeError, ValueError) as error:
            raise DataValidationError(f"Invalid Account: {error}") from error
        for field in ("name", "email", "address"):
            if not isinstance(getattr(self, field), str) or not getattr(self, field).strip():
                raise DataValidationError(f"Invalid Account: {field} must be a non-empty string")
        return self

    # ---------- queries ----------
    @classmethod
    def all(cls):
        """Return every account."""
        return cls.query.all()

    @classmethod
    def find(cls, account_id):
        """Return the account with this id, or None."""
        return db.session.get(cls, account_id)

    @classmethod
    def find_by_name(cls, name):
        """Return accounts with this name."""
        return cls.query.filter(cls.name == name).all()
