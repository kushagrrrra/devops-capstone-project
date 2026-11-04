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

Setup, run and test instructions are added as each sprint is completed.

## Author

Kushagra Singhal — MTech CSE, VIT Vellore
