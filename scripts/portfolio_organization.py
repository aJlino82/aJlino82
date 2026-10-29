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
    "42Basecamp",
    "Aula-bootstrap-DIO",
    "Aula-Netflix",
    "Bancos_Nao_Convencionais",
    "books",
    "Clone-Instagram",
    "crud-php-mysql-procedural",
    "Desafio-web-site",
    "Digital-Inovattion-One",
    "dio-cognizant-java",
    "dio-lab-open-source",
    "free-programming-books",
    "GitHubGraduation-2022",
    "Java-Basico-Unipe-Pos-2020.1",
    "Livro-de-Receitas-Aula",
    "Meuapp",
    "minicurso-streamlit",
    "mysqlbook",
    "NLW-2021",
    "numero-por-extenso",
    "PHPOO",
    "Pos-Javaweb-Configuracao",
    "Pos-Unipe-phonebook",
    "posMobile",
    "projeto-app",
    "react-dev-media",
    "tasks-tracker",
    "this-week-in-rust",
    "unipe-mobile-2020",
    "verificador",
]

PORTFOLIO_METADATA = {
    "api-bb": {
        "description": "Java Spring Boot REST API integration project",
        "topics": ["java", "spring-boot", "rest-api", "backend"],
    },
    "BooksChallenge": {
        "description": "Technical challenge - Books REST API built with Java and Spring Boot",
        "topics": ["java", "spring-boot", "rest-api", "challenge", "backend"],
    },
    "dio-product-catalog": {
        "description": "Distributed microservices architecture with Spring Cloud, API Gateway and Service Discovery",
        "topics": ["java", "spring-cloud", "microservices", "spring-boot", "api-gateway"],
    },
    "demo-quarkus": {
        "description": "Cloud Native Java with Quarkus and GraalVM native image",
        "topics": ["java", "quarkus", "graalvm", "cloud-native", "microservices"],
    },
    "DIO-Santander-Sala-Reunioes": {
        "description": "Meeting room management system built with Java and Spring Boot",
        "topics": ["java", "spring-boot", "crud", "backend", "fullstack"],
    },
    "dsmovie": {
        "description": "Movie rating application with frontend and backend integration",
        "topics": ["java", "spring-boot", "react", "fullstack", "portfolio"],
    },
    "go-scaffolding-project-model": {
        "description": "Production-ready Go project template with clean architecture",
        "topics": ["go", "golang", "architecture", "template", "clean-architecture"],
    },
    "helm_curso": {
        "description": "Infrastructure as Code with Helm charts for Kubernetes",
        "topics": ["kubernetes", "helm", "devops", "infrastructure", "k8s"],
    },
    "Projeto-DIO-Santander": {
        "description": "REST API with full audit trail using Spring Boot, Hibernate Envers, Lombok and Swagger",
        "topics": ["java", "spring-boot", "rest-api", "swagger", "hibernate", "audit"],
    },
    "sds-dsmeta": {
        "description": "Full-stack sales dashboard built with Spring Boot and React",
        "topics": ["java", "spring-boot", "react", "fullstack", "dashboard"],
    },
    "Alga-MSR-2023": {
        "description": "Java backend study project using enterprise-oriented patterns and APIs",
        "topics": ["java", "backend", "spring", "api", "study"],
    },
}

README_CONTENTS = {
    "api-bb": """# API BB

Java Spring Boot REST API integration project focused on backend services and data processing.

## Stack

- Java
- Spring Boot
- REST API
- Maven

## Objective

Provide a practical backend structure to integrate business rules and API consumption in a clean way.

## Run locally

```bash
mvn spring-boot:run
```
""",
    "BooksChallenge": """# Books Challenge

Technical challenge focused on building a books management REST API.

## Stack

- Java
- Spring Boot
- JPA
- H2

## Features

- Create, list, update and delete books
- Data persistence with JPA
- REST endpoints

## Run locally

```bash
mvn spring-boot:run
```
""",
    "dio-product-catalog": """# Product Catalog Microservices

Distributed microservices architecture built with Spring Cloud.

## Architecture

- API Gateway
- Service Discovery (Eureka)
- Config Server
- Product Service

## Stack

- Java
- Spring Boot
- Spring Cloud
- Eureka
- Maven

## Run locally

```bash
# Start Eureka first
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

- CRUD for users and access records
- Full audit trail with Hibernate Envers
- API documentation with Swagger UI

## Stack

- Java
- Spring Boot
- Hibernate Envers
- Lombok
- Swagger

## Run locally

```bash
mvn spring-boot:run
```
""",
    "sds-dsmeta": """# DSMeta

Full-stack sales dashboard built with Spring Boot and React.

## Stack

- Java
- Spring Boot
- React
- TypeScript
- REST API

## Objective

Show an end-to-end portfolio project with backend, frontend, dashboard and data presentation.

## Run locally

```bash
# backend
cd backend && mvn spring-boot:run

# frontend
cd frontend && npm install && npm run dev
```
""",
    "go-scaffolding-project-model": """# Go Scaffolding Project Model

Production-ready Go project template following clean architecture principles.

## Purpose

Bootstrap new services with:

- clear separation of concerns
- testable architecture
- clean project structure

## Stack

- Go
- Clean Architecture
- HTTP router

## Run locally

```bash
go run ./cmd/app
```
""",
    "demo-quarkus": """# Demo Quarkus

Cloud-native Java application using Quarkus and GraalVM-inspired build practices.

## Stack

- Java
- Quarkus
- GraalVM
- REST API

## Run locally

```bash
mvn quarkus:dev
```
""",
    "helm_curso": """# Helm Course

Infrastructure as Code project using Helm charts for Kubernetes deployment.

## Stack

- Kubernetes
- Helm
- YAML
- DevOps

## Objective

Practice deployment automation and environment configuration through Helm releases.
""",
    "dsmovie": """# DSMovie

Movie rating demo project with frontend and backend integration.

## Stack

- Java
- Spring Boot
- React
- REST API

## Objective

Create a simple, real portfolio project with user interaction and API data consumption.
""",
    "DIO-Santander-Sala-Reunioes": """# Meeting Room Management

Project to manage meeting rooms and reservations.

## Stack

- Java
- Spring Boot
- JPA
- REST API

## Objective

Practice CRUD flows, validation and service logic in a real backend project.
""",
    "Alga-MSR-2023": """# AlgaWorks MSR 2023

Study project focused on backend and practical application of Java enterprise patterns.

## Stack

- Java
- Spring
- API
- Backend

## Objective

Build experience with enterprise Java patterns and real backend flows.
""",
}


def github_request(method, path, token, payload=None):
    if not token:
        raise RuntimeError("Missing GITHUB_TOKEN for live GitHub API requests.")
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
        description="Automate GitHub portfolio organization using the GitHub REST API.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print all operations without calling the GitHub API.",
    )
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN", "")
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
