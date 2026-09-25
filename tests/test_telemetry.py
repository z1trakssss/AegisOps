from unittest.mock import patch

from fastapi import FastAPI
from orders_api.config import Settings
from orders_api.telemetry import configure_telemetry


def test_telemetry_is_disabled_without_endpoint() -> None:
    with patch("orders_api.telemetry.FastAPIInstrumentor.instrument_app") as instrument:
        configure_telemetry(FastAPI(), Settings())
        instrument.assert_not_called()


def test_telemetry_exports_to_configured_collector() -> None:
    settings = Settings(otel_endpoint="http://otel-collector:4317")

    with (
        patch("orders_api.telemetry.TracerProvider") as tracer_provider_class,
        patch("orders_api.telemetry.OTLPSpanExporter") as trace_exporter_class,
        patch("orders_api.telemetry.BatchSpanProcessor") as span_processor_class,
        patch("orders_api.telemetry.trace.set_tracer_provider") as set_tracer_provider,
        patch("orders_api.telemetry.FastAPIInstrumentor.instrument_app") as instrument,
        patch("orders_api.telemetry.LoggerProvider") as logger_provider_class,
        patch("orders_api.telemetry.OTLPLogExporter") as log_exporter_class,
        patch("orders_api.telemetry.BatchLogRecordProcessor") as log_processor_class,
        patch("orders_api.telemetry.set_logger_provider") as set_log_provider,
        patch("orders_api.telemetry.LoggingHandler") as logging_handler_class,
        patch("orders_api.telemetry.logging.getLogger") as get_logger,
    ):
        configure_telemetry(FastAPI(), settings)

    trace_exporter_class.assert_called_once_with(endpoint=settings.otel_endpoint, insecure=True)
    span_processor_class.assert_called_once_with(trace_exporter_class.return_value)
    tracer_provider_class.return_value.add_span_processor.assert_called_once_with(
        span_processor_class.return_value
    )
    set_tracer_provider.assert_called_once_with(tracer_provider_class.return_value)
    instrument.assert_called_once()
    log_exporter_class.assert_called_once_with(endpoint=settings.otel_endpoint, insecure=True)
    log_processor_class.assert_called_once_with(log_exporter_class.return_value)
    logger_provider_class.return_value.add_log_record_processor.assert_called_once_with(
        log_processor_class.return_value
    )
    set_log_provider.assert_called_once_with(logger_provider_class.return_value)
    logging_handler_class.assert_called_once_with(
        logger_provider=logger_provider_class.return_value
    )
    get_logger.return_value.addHandler.assert_called_once_with(logging_handler_class.return_value)
