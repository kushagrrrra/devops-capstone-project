"""Tests for security headers (Talisman) and the CORS policy."""
from http import HTTPStatus

import pytest

from service import create_app

ALLOWED_ORIGIN = "http://localhost:8080"


class TestSecurityHeaders:
    def test_security_headers(self, client):
        resp = client.get("/", environ_overrides={"HTTP_HOST": "localhost"})
        assert resp.status_code == HTTPStatus.OK
        expected = {
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'self'; object-src 'none'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }
        for header, value in expected.items():
            assert resp.headers.get(header) == value

    def test_headers_on_api_and_error_responses(self, client):
        for url in ("/accounts", "/accounts/0"):
            assert client.get(url).headers.get("X-Frame-Options") == "SAMEORIGIN"

    def test_no_hsts_or_redirect_over_plain_http(self, client):
        resp = client.get("/")
        assert resp.status_code == HTTPStatus.OK
        assert "Strict-Transport-Security" not in resp.headers


class TestForcedHttps:
    @pytest.fixture
    def https_client(self):
        app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://", "FORCE_HTTPS": True})
        return app.test_client()

    def test_http_redirects_to_https(self, https_client):
        resp = https_client.get("/")
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.headers["Location"].startswith("https://")

    def test_hsts_over_https(self, https_client):
        resp = https_client.get("/", base_url="https://localhost")
        assert resp.status_code == HTTPStatus.OK
        assert "max-age=" in resp.headers["Strict-Transport-Security"]


class TestCors:
    def test_allowed_origin(self, client):
        resp = client.get("/accounts", headers={"Origin": ALLOWED_ORIGIN})
        assert resp.headers.get("Access-Control-Allow-Origin") == ALLOWED_ORIGIN
        assert "Access-Control-Allow-Credentials" not in resp.headers

    def test_disallowed_origin_gets_no_cors_headers(self, client):
        resp = client.get("/accounts", headers={"Origin": "https://evil.example"})
        assert "Access-Control-Allow-Origin" not in resp.headers

    def test_preflight_lists_only_api_methods(self, client):
        resp = client.options("/accounts", headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "DELETE",
            "Access-Control-Request-Headers": "Content-Type",
        })
        allowed = {m.strip() for m in resp.headers["Access-Control-Allow-Methods"].split(",")}
        assert allowed == {"GET", "POST", "PUT", "DELETE"}

    def test_non_api_routes_have_no_cors(self, client):
        resp = client.get("/", headers={"Origin": ALLOWED_ORIGIN})
        assert "Access-Control-Allow-Origin" not in resp.headers
