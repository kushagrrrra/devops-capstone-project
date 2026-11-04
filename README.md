# Accounts Microservice — DevOps Capstone

A RESTful microservice for managing customer accounts, built with Python and Flask, and delivered through a full DevOps workflow: agile planning, test-driven development, continuous integration with GitHub Actions, security hardening, containerization with Docker, deployment to Kubernetes, and a continuous delivery pipeline with Tekton.

## Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/accounts` | Create an account |
| `GET` | `/accounts` | List all accounts |
| `GET` | `/accounts/{id}` | Read a single account |
| `PUT` | `/accounts/{id}` | Update an account |
| `DELETE` | `/accounts/{id}` | Delete an account |

## Tech stack

- **Language / framework:** Python 3, Flask, Flask-SQLAlchemy
- **Database:** PostgreSQL
- **Testing / linting:** pytest (with coverage), flake8
- **Security:** Flask-Talisman (security headers), Flask-CORS
- **CI:** GitHub Actions
- **Containers / orchestration:** Docker, Kubernetes
- **CD:** Tekton Pipelines

## Project planning

Work is tracked as user stories in GitHub Issues, using the **User Story** issue template, and managed on a Kanban board with the columns **Backlog → Ready → In Progress → In Review → Done**.

## Getting started

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

### Run the tests and linter

```bash
flake8 service tests
pytest                # uses in-memory SQLite unless DATABASE_URI is set
```

### Run the service

```bash
# Uses PostgreSQL by default; for a quick local run, point it at SQLite:
set DATABASE_URI=sqlite:///dev.db                    # Windows cmd
gunicorn --bind 0.0.0.0:8080 service.wsgi:app        # Linux/macOS/containers
flask --app service.wsgi run --port 8080             # Windows (gunicorn is Unix-only)
```

### Example requests

```bash
curl -i -X POST http://localhost:8080/accounts -H "Content-Type: application/json" \
     -d '{"name":"Test User","email":"test@example.com","address":"VIT Vellore","phone_number":"9999999999"}'
curl -i http://localhost:8080/accounts/1             # read one
curl -i http://localhost:8080/accounts               # list all
curl -i -X PUT http://localhost:8080/accounts/1 -H "Content-Type: application/json" \
     -d '{"name":"Updated User","email":"test@example.com","address":"VIT Vellore"}'
curl -i -X DELETE http://localhost:8080/accounts/1
```

| Status | When |
|--------|------|
| 201 Created | account created (with `Location` header) |
| 200 OK | read, list, update succeeded |
| 204 No Content | delete (also if the account was already gone) |
| 400 Bad Request | missing or invalid fields |
| 404 Not Found | no account with that id |
| 405 Method Not Allowed | unsupported method on a route |
| 415 Unsupported Media Type | body is not `application/json` |

## Author

Kushagra Singhal — MTech CSE, VIT Vellore
