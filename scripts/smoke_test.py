"""Smoke test a running accounts service: health, CRUD and security headers.

Usage:  python scripts/smoke_test.py http://localhost:8080
Uses only the standard library, so it runs without installing anything.
"""
import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8080"
REQUIRED_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; object-src 'none'",
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}
failures = 0


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            return resp.status, dict(resp.headers), json.loads(raw) if raw else None
    except urllib.error.HTTPError as err:
        raw = err.read()
        return err.code, dict(err.headers), json.loads(raw) if raw else None


def check(label, ok, detail=""):
    global failures
    failures += 0 if ok else 1
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{'  ' + detail if detail else ''}")


print(f"Smoke testing {BASE}\n")

status, headers, body = call("GET", "/health")
check("GET /health -> 200", status == 200 and body == {"status": "OK"}, f"{status} {body}")

for name, value in REQUIRED_HEADERS.items():
    check(f"header {name}", headers.get(name) == value, headers.get(name, "<missing>"))

new = {"name": "Smoke Test", "email": "smoke@example.com",
       "address": "VIT Vellore", "phone_number": "9999999999"}
status, _, created = call("POST", "/accounts", new)
check("POST /accounts -> 201",
      status == 201 and created and created["name"] == new["name"], f"{status} {created}")
acc_id = created["id"] if created else 0

status, _, body = call("GET", f"/accounts/{acc_id}")
check(f"GET /accounts/{acc_id} -> 200", status == 200 and body["email"] == new["email"], f"{status} {body}")

status, _, body = call("GET", "/accounts")
check("GET /accounts -> 200 list",
      status == 200 and any(a["id"] == acc_id for a in body), f"{status} {len(body or [])} account(s)")

status, _, body = call("PUT", f"/accounts/{acc_id}", dict(new, name="Smoke Test Updated"))
check(f"PUT /accounts/{acc_id} -> 200", status == 200 and body["name"] == "Smoke Test Updated", f"{status} {body}")

status, _, body = call("DELETE", f"/accounts/{acc_id}")
check(f"DELETE /accounts/{acc_id} -> 204", status == 204, str(status))

status, _, body = call("GET", f"/accounts/{acc_id}")
check(f"GET /accounts/{acc_id} after delete -> 404", status == 404, str(status))

print(f"\n{'ALL CHECKS PASSED' if failures == 0 else f'{failures} CHECK(S) FAILED'}")
sys.exit(1 if failures else 0)
