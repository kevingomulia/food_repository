.PHONY: dev run test check clean db
.DEFAULT: help
-include .env

PYTHON=python3.11

help: ## Display this help message
	@echo "Please use \`make <target>\` where <target> is one of"
	@awk -F ':.*?## ' '/^[a-zA-Z]/ && NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Remove general artifact files
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	find . -name '__pycache__' -type d | xargs rm -rf

venv: ## Create virtual environment if venv directory not present
	`which ${PYTHON}` -m venv venv
	venv/bin/pip install -U pip pip-tools wheel --no-cache-dir

requirements.txt: venv requirements.in ## Generate requirements for release
	venv/bin/pip-compile -o requirements.txt requirements.in

update-req: venv requirements.in  ## Update requirements to fulfil dependencies minimally
	venv/bin/pip-compile -o requirements.txt requirements.in

install: venv requirements.txt ## Install dependencies for dev
	venv/bin/pip-sync requirements.txt

db: ## Run a Postgres database with env vars that matches the DATABASE_URL env var
	docker run -d --rm \
	-p 5432:5432 \
	--name food_db  \
	-v "$(PWD)/db:/var/lib/postgresql/data" \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_PASSWORD=postgres \
	-e POSTGRES_DB=postgres \
	-e TZ=UTC \
	postgres:17


run: install ## Run with dev dependencies
	venv/bin/python -m streamlit run src/main.py

