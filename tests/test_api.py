from fastapi.testclient import TestClient
from orders_api.config import Settings
from orders_api.main import create_app


def make_client(fault_mode: str = "none") -> TestClient:
    return TestClient(create_app(Settings(fault_mode=fault_mode)))


def test_health_and_readiness() -> None:
    with make_client() as client:
        assert client.get("/healthz").json() == {"status": "ok"}
        assert client.get("/readyz").json() == {"status": "ready"}


def test_create_and_list_order() -> None:
    with make_client() as client:
        response = client.post("/api/v1/orders", json={"product": "coffee", "quantity": 2})
        assert response.status_code == 201
        order = response.json()
        assert order["product"] == "coffee"
        assert order["quantity"] == 2
        assert order["status"] == "accepted"

        orders = client.get("/api/v1/orders").json()
        assert orders == [order]


def test_rejects_invalid_order() -> None:
    with make_client() as client:
        response = client.post("/api/v1/orders", json={"product": "", "quantity": 0})
        assert response.status_code == 422


def test_error_fault_mode() -> None:
    with make_client("errors") as client:
        response = client.post("/api/v1/orders", json={"product": "tea", "quantity": 1})
        assert response.status_code == 503
        assert response.json()["detail"].startswith("fault injection")


def test_not_ready_fault_mode() -> None:
    with make_client("not-ready") as client:
        assert client.get("/healthz").status_code == 200
        assert client.get("/readyz").status_code == 503


def test_metrics_are_exposed() -> None:
    with make_client() as client:
        client.get("/healthz")
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "aegis_http_requests_total" in response.text
