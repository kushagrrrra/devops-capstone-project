"""HTTP security headers (Flask-Talisman) and CORS policy (Flask-CORS)."""
from flask_cors import CORS
from flask_talisman import Talisman

# A JSON API serves no scripts, styles or frames, so lock everything to our own origin.
CONTENT_SECURITY_POLICY = {
    "default-src": "'self'",
    "object-src": "'none'",
}


def init_security(app):
    """Attach security headers and the CORS policy to every response."""
    force_https = app.config["FORCE_HTTPS"]

    Talisman(
        app,
        force_https=force_https,                       # redirect http -> https only behind TLS
        strict_transport_security=force_https,         # HSTS is meaningless over plain HTTP
        session_cookie_secure=force_https,
        content_security_policy=CONTENT_SECURITY_POLICY,
        frame_options="SAMEORIGIN",                    # X-Frame-Options: blocks clickjacking
        referrer_policy="strict-origin-when-cross-origin",
        # X-Content-Type-Options: nosniff is sent by Talisman by default
    )

    CORS(
        app,
        resources={r"/accounts*": {"origins": app.config["CORS_ORIGINS"]}},
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
        supports_credentials=False,                    # no cookies/auth sent cross-origin
        max_age=600,
    )
