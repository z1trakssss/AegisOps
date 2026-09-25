"""FastAPI demo workload instrumented for reliability experiments."""

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from threading import Lock
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, Request, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field

from orders_api.config import Settings

LOGGER = logging.getLogger("orders_api")
REQUESTS = Counter(
    "aegis_http_requests_total",
    "Total HTTP requests handled by the service.",
    ("method", "path", "status"),
)
LATENCY = Histogram(
    "aegis_http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ("method", "path"),
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
READY = Gauge("aegis_service_ready", "Whether the service is ready to receive traffic.")


class OrderInput(BaseModel):
    product: str = Field(min_length=1, max_length=100, examples=["coffee"])
    quantity: int = Field(ge=1, le=100, examples=[2])


class Order(OrderInput):
    id: UUID
    status: str = "accepted"


class OrderStore:
    """Small thread-safe in-memory store suitable for the demo workload."""

    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}
        self._lock = Lock()

    def create(self, order_input: OrderInput) -> Order:
        order = Order(id=uuid4(), **order_input.model_dump())
        with self._lock:
            self._orders[order.id] = order
        return order

    def list(self) -> list[Order]:
        with self._lock:
            return list(self._orders.values())


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or Settings.from_env()
    store = OrderStore()

    logging.basicConfig(
        level=app_settings.log_level,
        format="%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s",
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        READY.set(1)
        LOGGER.info("service_started version=%s", app_settings.version)
        yield
        READY.set(0)
        LOGGER.info("service_stopped")

    app = FastAPI(
        title="AegisOps Orders API",
        version=app_settings.version,
        description="Demo service for DevSecOps, SRE and SOC experiments.",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def observe_request(request: Request, call_next):  # type: ignore[no-untyped-def]
        started = time.perf_counter()
        response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        path = request.url.path
        try:
            response = await call_next(request)
            response_status = response.status_code
            return response
        finally:
            REQUESTS.labels(request.method, path, str(response_status)).inc()
            LATENCY.labels(request.method, path).observe(time.perf_counter() - started)

    @app.get("/", tags=["system"])
    async def root() -> dict[str, str]:
        return {"service": app_settings.service_name, "version": app_settings.version}

    @app.get("/healthz", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["system"])
    async def readiness() -> dict[str, str]:
        if app_settings.fault_mode == "not-ready":
            raise HTTPException(status_code=503, detail="fault injection: not ready")
        return {"status": "ready"}

    @app.get("/metrics", include_in_schema=False)
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/api/v1/orders", response_model=list[Order], tags=["orders"])
    async def list_orders() -> list[Order]:
        return store.list()

    @app.post(
        "/api/v1/orders",
        response_model=Order,
        status_code=status.HTTP_201_CREATED,
        tags=["orders"],
    )
    async def create_order(order_input: OrderInput) -> Order:
        if app_settings.fault_mode == "latency":
            await asyncio.sleep(1.5)
        if app_settings.fault_mode == "errors":
            raise HTTPException(status_code=503, detail="fault injection: upstream unavailable")
        return store.create(order_input)

    return app


app = create_app()
