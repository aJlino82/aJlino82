#!/usr/bin/env python3
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

OWNER = "aJlino82"
COMMIT_MESSAGE = "chore: portfolio organization and README improvements"

ARCHIVE_REPOS = [
    "angular-spring-course",
    "pos-web-java-spring-mongodb",
    "dio-cognizant-java",
    "curso-spring",
    "react-dev-media",
    "sds-dsmeta",
    "dsmovie",
    "Java-avancado-sd-admin-2",
    "DIO-Santander-Sala-Reunioes",
    "diorhapi",
    "PHPOO",
    "Aula-bootstrap-DIO",
    "Clone-Instagram",
    "Aula-Netflix",
    "NLW-2021",
    "Bancos_Nao_Convencionais",
    "Java-Basico-Unipe-Pos-2020.1",
    "Digital-Inovattion-One",
    "42Basecamp",
    "posMobile",
    "unipe-mobile-2020",
    "Pos-Javaweb-Configuracao",
    "Pos-Unipe-phonebook",
    "JSPDF",
    "Desafio-web-site",
    "verificador",
    "books",
    "Semana-Dev-Superior-fork-",
    "sds4",
]

PORTFOLIO_METADATA = {
    "dio-product-catalog": {
        "description": "Distributed microservices architecture with Spring Cloud, API Gateway and Service Discovery",
        "topics": ["java", "spring-cloud", "microservices", "spring-boot", "api-gateway"],
    },
    "Projeto-DIO-Santander": {
        "description": "REST API with full audit trail using Spring Boot, Hibernate Envers, Lombok and Swagger",
        "topics": ["java", "spring-boot", "rest-api", "swagger", "hibernate", "audit"],
    },
    "go-scaffolding-project-model": {
        "description": "Production-ready Go project template with clean architecture",
        "topics": ["go", "golang", "architecture", "template", "clean-architecture"],
    },
    "demo-quarkus": {
        "description": "Cloud Native Java with Quarkus and GraalVM native image",
        "topics": ["java", "quarkus", "graalvm", "cloud-native", "microservices"],
    },
    "helm_curso": {
        "description": "Infrastructure as Code with Helm charts for Kubernetes",
        "topics": ["kubernetes", "helm", "devops", "infrastructure", "k8s"],
    },
    "api-bb": {
        "description": "Java Spring Boot REST API integration",
        "topics": ["java", "spring-boot", "rest-api"],
    },
    "BooksChallenge": {
        "description": "Technical challenge - Books REST API in Java",
        "topics": ["java", "spring-boot", "challenge", "rest-api"],
    },
    "desafio-BeHoh": {
        "description": "Java Web technical challenge",
        "topics": ["java", "spring-boot", "challenge"],
    },
    "Desafio-Calcme": {
        "description": "Frontend technical challenge built with TypeScript",
        "topics": ["typescript", "frontend", "challenge"],
    },
}

README_CONTENTS = {
    "dio-product-catalog": """# Product Catalog Microservices

Distributed microservices architecture built with Spring Cloud.

## Architecture

- **API Gateway** — Single entry point for all services
- **Service Discovery (Eureka)** — Dynamic service registration
- **Config Server** — Centralized configuration management
- **Product Service** — Core product catalog REST API

## Tech Stack

- Java · Spring Boot · Spring Cloud Netflix
- Eureka Server · Zuul API Gateway
- REST APIs · Maven

## Running locally

```bash
# Start Eureka Server first
cd eureka-server && mvn spring-boot:run

# Start Config Server
cd config-server && mvn spring-boot:run

# Start Product Service
cd product-catalog && mvn spring-boot:run
```
""",
    "Projeto-DIO-Santander": """# Access Control REST API

REST API for user access and time tracking control, built with Spring Boot.

## Features

- Complete CRUD for users and access records
- Full audit trail with **Hibernate Envers** (tracks every change)
- Interactive API documentation via **Swagger UI**
- Reduced boilerplate with **Lombok**

## Tech Stack

- Java · Spring Boot · Spring Data JPA
- Hibernate Envers · Lombok · Swagger/OpenAPI
- H2 (dev) · PostgreSQL (prod)

## Running locally

```bash
mvn spring-boot:run
# Swagger UI: http://localhost:8080/swagger-ui.html
```
""",
    "go-scaffolding-project-model": """# Go Scaffolding Project Model

Production-ready Go project template following clean architecture principles.

## Structure

```
.
├── cmd/          # Application entrypoints
├── internal/     # Private application code
│   ├── domain/   # Business entities and rules
│   ├── usecase/  # Application use cases
│   └── infra/    # External concerns (DB, HTTP, etc.)
├── pkg/          # Public shared packages
└── configs/      # Configuration files
```

## Purpose

Opinionated template to bootstrap Go projects with:
- Clear separation of concerns
- Testable architecture
- Standard project layout

## Tech Stack

Go · Chi Router · Clean Architecture
""",
}


def github_request(method, path, token, payload=None):
    url = f"https://api.github.com{path}"
    data = None
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    headers["Authorization"] = "Bearer " + token
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode("utf-8")
            return resp.status, json.loads(text) if text else {}
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8")
        raise RuntimeError(f"{method} {path} failed: {err.code} {body}") from err


def ensure_allowed_repository(token, repo, dry_run=False):
    if OWNER.lower() == "sms-sistemas":
        raise RuntimeError("Operation blocked: repositories from sms-sistemas cannot be changed.")
    if "/" in repo:
        raise RuntimeError(f"Invalid repository name '{repo}'. Use only repository names without owner.")
    if dry_run:
        return

    _, repo_data = github_request("GET", f"/repos/{OWNER}/{repo}", token)
    owner_login = str(repo_data.get("owner", {}).get("login", "")).lower()
    full_name = str(repo_data.get("full_name", "")).lower()
    if owner_login == "sms-sistemas" or full_name.startswith("sms-sistemas/"):
        raise RuntimeError(f"Operation blocked for client repository: {full_name or repo}")


def archive_repositories(token, dry_run=False):
    for repo in ARCHIVE_REPOS:
        ensure_allowed_repository(token, repo, dry_run=dry_run)
        if dry_run:
            print(f"[dry-run][archive] {OWNER}/{repo}")
            continue
        status, _ = github_request("PATCH", f"/repos/{OWNER}/{repo}", token, {"archived": True})
        print(f"[archive] {repo}: HTTP {status}")


def update_metadata(token, dry_run=False):
    for repo, config in PORTFOLIO_METADATA.items():
        ensure_allowed_repository(token, repo, dry_run=dry_run)
        if dry_run:
            print(f"[dry-run][description] {OWNER}/{repo} -> {config['description']}")
            print(f"[dry-run][topics] {OWNER}/{repo} -> {', '.join(config['topics'])}")
            continue
        status, _ = github_request(
            "PATCH",
            f"/repos/{OWNER}/{repo}",
            token,
            {"description": config["description"]},
        )
        print(f"[description] {repo}: HTTP {status}")
        status, _ = github_request(
            "PUT",
            f"/repos/{OWNER}/{repo}/topics",
            token,
            {"names": config["topics"]},
        )
        print(f"[topics] {repo}: HTTP {status}")


def upsert_readme(token, repo, content, dry_run=False):
    ensure_allowed_repository(token, repo, dry_run=dry_run)
    if dry_run:
        print(f"[dry-run][readme] {OWNER}/{repo} -> README.md")
        return

    sha = None
    try:
        _, readme = github_request("GET", f"/repos/{OWNER}/{repo}/readme", token)
        sha = readme.get("sha")
    except RuntimeError as err:
        if "404" not in str(err):
            raise

    payload = {
        "message": COMMIT_MESSAGE,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha

    status, _ = github_request("PUT", f"/repos/{OWNER}/{repo}/contents/README.md", token, payload)
    print(f"[readme] {repo}: HTTP {status}")


def update_readmes(token, dry_run=False):
    for repo, content in README_CONTENTS.items():
        upsert_readme(token, repo, content, dry_run=dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="Automate GitHub portfolio organization using the GitHub REST API."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print all operations without calling the GitHub API.",
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token and not args.dry_run:
        print("Missing GITHUB_TOKEN environment variable.", file=sys.stderr)
        return 1

    archive_repositories(token, dry_run=args.dry_run)
    update_metadata(token, dry_run=args.dry_run)
    update_readmes(token, dry_run=args.dry_run)
    print("Portfolio organization finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
