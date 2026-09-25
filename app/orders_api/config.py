"""Environment-based application configuration."""

from dataclasses import dataclass
from os import getenv

DEFAULT_SERVICE_NAME = "orders-api"
DEFAULT_VERSION = "0.1.0"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_FAULT_MODE = "none"


@dataclass(frozen=True, slots=True)
class Settings:
    service_name: str = DEFAULT_SERVICE_NAME
    version: str = DEFAULT_VERSION
    log_level: str = DEFAULT_LOG_LEVEL
    fault_mode: str = DEFAULT_FAULT_MODE

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            service_name=getenv("AEGIS_SERVICE_NAME", DEFAULT_SERVICE_NAME),
            version=getenv("AEGIS_VERSION", DEFAULT_VERSION),
            log_level=getenv("AEGIS_LOG_LEVEL", DEFAULT_LOG_LEVEL).upper(),
            fault_mode=getenv("AEGIS_FAULT_MODE", DEFAULT_FAULT_MODE).lower(),
        )
