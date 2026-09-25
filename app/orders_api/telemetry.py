"""Optional OpenTelemetry tracing and logging configuration."""

import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from orders_api.config import Settings


def configure_telemetry(app: FastAPI, settings: Settings) -> None:
    """Enable OTLP traces and logs when a collector endpoint is configured."""
    if not settings.otel_endpoint:
        return

    resource = Resource.create(
        {
            "service.name": settings.service_name,
            "service.version": settings.version,
            "deployment.environment": "kubernetes",
        }
    )

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.otel_endpoint,
                insecure=settings.otel_endpoint.startswith("http://"),
            )
        )
    )
    trace.set_tracer_provider(tracer_provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(
                endpoint=settings.otel_endpoint,
                insecure=settings.otel_endpoint.startswith("http://"),
            )
        )
    )
    set_logger_provider(logger_provider)
    logging.getLogger().addHandler(LoggingHandler(logger_provider=logger_provider))
