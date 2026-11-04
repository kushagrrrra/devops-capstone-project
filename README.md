# Accounts Microservice — DevOps Capstone

[![CI Build](https://github.com/kushagrrrra/devops-capstone-project/actions/workflows/ci-build.yaml/badge.svg)](https://github.com/kushagrrrra/devops-capstone-project/actions/workflows/ci-build.yaml)

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

## Security

Every response carries these headers, set by Flask-Talisman in `service/common/security.py`:

| Header | Value | Protects against |
|--------|-------|------------------|
| Content-Security-Policy | `default-src 'self'; object-src 'none'` | injected scripts and plugins |
| X-Frame-Options | `SAMEORIGIN` | clickjacking |
| X-Content-Type-Options | `nosniff` | MIME-type sniffing |
| Referrer-Policy | `strict-origin-when-cross-origin` | leaking URLs to other sites |

CORS is allowed only on `/accounts*`, only from the origins in `CORS_ORIGINS` (default `http://localhost:8080`, never `*`), only for GET/POST/PUT/DELETE, and without credentials.

| Variable | Default | Purpose |
|----------|---------|---------|
| `FORCE_HTTPS` | `false` | `true` redirects HTTP to HTTPS and sends HSTS. Leave off for local HTTP, tests and in-cluster health probes; turn on when TLS terminates at the app. |
| `CORS_ORIGINS` | `http://localhost:8080` | comma-separated list of browser origins allowed to call the API |
| `SECRET_KEY` | placeholder | set from an environment variable or Kubernetes secret in any real deployment |

CI also runs **bandit** (static analysis of the code) and **pip-audit** (known vulnerabilities in dependencies) on every push.

```bash
curl -I http://localhost:8080      # check the headers yourself
```

## Docker

The [`Dockerfile`](Dockerfile) builds on `python:3.12-slim`, installs `requirements.txt`, copies only the `service/` package, runs as the non-root user `theia`, and starts gunicorn on `0.0.0.0:8080`. Configuration and secrets (`DATABASE_URI`, `SECRET_KEY`) are passed at runtime and are never baked into the image. `.dockerignore` keeps `.git`, virtual environments, tests, evidence and local data out of the build context.

```bash
docker build -t accounts:1 .
docker images accounts
```

Run it against a throwaway PostgreSQL container on a private network (PowerShell shown; the password is generated, not typed):

```powershell
$pw = -join ((48..57)+(97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
docker network create accounts-net
docker run -d --name accounts-db --network accounts-net -e POSTGRES_PASSWORD=$pw -e POSTGRES_DB=accounts postgres:15-alpine
docker run -d --name accounts-app --network accounts-net -p 18080:8080 `
  -e DATABASE_URI="postgresql+psycopg2://postgres:$pw@accounts-db:5432/accounts" accounts:1
python scripts/smoke_test.py http://localhost:18080     # health, CRUD and security headers
docker rm -f accounts-app accounts-db; docker network rm accounts-net
```

## Kubernetes

Tested on Docker Desktop's built-in single-node cluster (context `docker-desktop`). Because that cluster uses the same Docker engine, the locally built `accounts:1` image is used directly (`imagePullPolicy: IfNotPresent`); no registry push is needed.

| Manifest | Contents |
|----------|----------|
| [`k8s/postgres.yaml`](k8s/postgres.yaml) | PostgreSQL 15 Deployment, 1Gi PersistentVolumeClaim, internal `ClusterIP` Service |
| [`k8s/configmap.yaml`](k8s/configmap.yaml) | Non-secret settings (`FORCE_HTTPS`, `CORS_ORIGINS`, database host and name) |
| [`k8s/deployment.yaml`](k8s/deployment.yaml) | `accounts` Deployment, 2 replicas, `/health` readiness and liveness probes, init container that waits for PostgreSQL, non-root security context |
| [`k8s/service.yaml`](k8s/service.yaml) | `LoadBalancer` Service on port 8080 (Docker Desktop publishes it on `localhost`) |

Credentials live in a Secret created from generated values, never in a file:

```powershell
$pw = -join ((48..57)+(97..122) | Get-Random -Count 24 | ForEach-Object {[char]$_})
$sk = -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 40 | ForEach-Object {[char]$_})
kubectl create secret generic postgres-creds --from-literal=password=$pw --from-literal=secret-key=$sk
```

Deploy and check:

```bash
kubectl apply -f k8s/
kubectl rollout status deployment/postgres
kubectl rollout status deployment/accounts
kubectl get all -l 'app in (accounts,postgres)'
python scripts/smoke_test.py http://localhost:8080
```

If something else on your machine already uses port 8080, test through a port-forward instead:
`kubectl port-forward service/accounts 18081:8080` and `python scripts/smoke_test.py http://localhost:18081`.

Logs and troubleshooting:

```bash
kubectl logs deployment/accounts                       # app logs
kubectl logs deployment/accounts -c wait-for-postgres  # init container
kubectl describe pod -l app=accounts
```

Clean up everything created for this section:

```bash
kubectl delete -f k8s/
kubectl delete secret postgres-creds
```

## Author

Kushagra Singhal — MTech CSE, VIT Vellore
