"""Integration tests for the Account REST API."""
from http import HTTPStatus

from tests.factories import AccountFactory

BASE_URL = "/accounts"


def _create_accounts(client, count):
    accounts = []
    for _ in range(count):
        account = AccountFactory()
        resp = client.post(BASE_URL, json=account.serialize())
        assert resp.status_code == HTTPStatus.CREATED
        account.id = resp.get_json()["id"]
        accounts.append(account)
    return accounts


class TestServiceBasics:
    def test_index(self, client):
        resp = client.get("/")
        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json()["name"] == "Account REST API Service"

    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json() == {"status": "OK"}


class TestCreateAccount:
    def test_create_account(self, client):
        account = AccountFactory()
        resp = client.post(BASE_URL, json=account.serialize())
        assert resp.status_code == HTTPStatus.CREATED
        assert resp.headers.get("Location")
        body = resp.get_json()
        assert body["name"] == account.name
        assert body["email"] == account.email

    def test_create_bad_data(self, client):
        resp = client.post(BASE_URL, json={"name": "missing fields"})
        assert resp.status_code == HTTPStatus.BAD_REQUEST

    def test_create_wrong_content_type(self, client):
        resp = client.post(BASE_URL, data="hello", content_type="text/html")
        assert resp.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE


class TestReadAccount:
    def test_read_an_account(self, client):
        account = _create_accounts(client, 1)[0]
        resp = client.get(f"{BASE_URL}/{account.id}")
        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json()["name"] == account.name

    def test_account_not_found(self, client):
        resp = client.get(f"{BASE_URL}/0")
        assert resp.status_code == HTTPStatus.NOT_FOUND


class TestListAccounts:
    def test_list_accounts(self, client):
        _create_accounts(client, 5)
        resp = client.get(BASE_URL)
        assert resp.status_code == HTTPStatus.OK
        assert len(resp.get_json()) == 5

    def test_list_empty(self, client):
        resp = client.get(BASE_URL)
        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json() == []


class TestUpdateAccount:
    def test_update_account(self, client):
        account = _create_accounts(client, 1)[0]
        new_data = account.serialize()
        new_data["name"] = "Updated Name"
        resp = client.put(f"{BASE_URL}/{account.id}", json=new_data)
        assert resp.status_code == HTTPStatus.OK
        assert resp.get_json()["name"] == "Updated Name"

    def test_update_not_found(self, client):
        resp = client.put(f"{BASE_URL}/0", json=AccountFactory().serialize())
        assert resp.status_code == HTTPStatus.NOT_FOUND

    def test_update_bad_data(self, client):
        account = _create_accounts(client, 1)[0]
        resp = client.put(f"{BASE_URL}/{account.id}", json={"name": ""})
        assert resp.status_code == HTTPStatus.BAD_REQUEST


class TestDeleteAccount:
    def test_delete_account(self, client):
        account = _create_accounts(client, 1)[0]
        resp = client.delete(f"{BASE_URL}/{account.id}")
        assert resp.status_code == HTTPStatus.NO_CONTENT
        assert resp.data == b""
        assert client.get(f"{BASE_URL}/{account.id}").status_code == HTTPStatus.NOT_FOUND

    def test_delete_missing_account_is_idempotent(self, client):
        resp = client.delete(f"{BASE_URL}/0")
        assert resp.status_code == HTTPStatus.NO_CONTENT


class TestErrorHandling:
    def test_method_not_allowed(self, client):
        resp = client.delete(BASE_URL)
        assert resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED
        assert resp.get_json()["error"] == "Method Not Allowed"
