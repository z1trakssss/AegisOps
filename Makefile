.PHONY: install run test lint format image cluster-up cluster-down deploy

install:
	python -m pip install -e ".[dev]"

run:
	python -m uvicorn orders_api.main:app --reload --port 8080

test:
	python -m pytest

lint:
	python -m ruff check app tests
	python -m ruff format --check app tests

format:
	python -m ruff check --fix app tests
	python -m ruff format app tests

image:
	docker build --tag aegisops/orders-api:dev .

cluster-up:
	kind create cluster --config infrastructure/kind/cluster.yaml

cluster-down:
	kind delete cluster --name aegisops

deploy: image
	kind load docker-image aegisops/orders-api:dev --name aegisops
	helm upgrade --install aegisops deploy/helm/aegisops --namespace aegisops --create-namespace --set image.repository=aegisops/orders-api --set image.tag=dev
