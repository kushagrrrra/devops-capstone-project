"""Unit tests for the Account model."""
import pytest

from service.models import Account, DataValidationError
from tests.factories import AccountFactory


def test_create_account():
    account = AccountFactory()
    account.create()
    assert account.id is not None
    assert len(Account.all()) == 1


def test_repr():
    account = Account(name="Foo", id=7)
    assert repr(account) == "<Account Foo id=[7]>"


def test_serialize_and_deserialize_round_trip():
    account = AccountFactory()
    data = account.serialize()
    copy = Account().deserialize(data)
    assert copy.name == account.name
    assert copy.email == account.email
    assert copy.date_joined == account.date_joined


def test_deserialize_defaults_date_joined():
    account = Account().deserialize({"name": "A", "email": "a@x.io", "address": "1 St"})
    assert account.date_joined is not None


@pytest.mark.parametrize("bad", [
    None,
    "not a dict",
    {"email": "a@x.io", "address": "1 St"},
    {"name": "", "email": "a@x.io", "address": "1 St"},
    {"name": "A", "email": "a@x.io", "address": "1 St", "date_joined": "not-a-date"},
])
def test_deserialize_rejects_bad_data(bad):
    with pytest.raises(DataValidationError):
        Account().deserialize(bad)


def test_update_and_find():
    account = AccountFactory()
    account.create()
    account.name = "Renamed"
    account.update()
    assert Account.find(account.id).name == "Renamed"
    assert Account.find_by_name("Renamed")[0].id == account.id


def test_update_without_id_fails():
    account = AccountFactory()
    account.id = None
    with pytest.raises(DataValidationError):
        account.update()


def test_delete():
    account = AccountFactory()
    account.create()
    account.delete()
    assert Account.all() == []
