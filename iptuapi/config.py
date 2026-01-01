"""
Configuracao do cliente IPTU API.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import logging


@dataclass
class RetryConfig:
    """Configuracao de retry para requisicoes."""

    max_retries: int = 3
    initial_delay: float = 1.0  # segundos
    max_delay: float = 30.0  # segundos
    backoff_factor: float = 2.0
    retryable_status_codes: List[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )


@dataclass
class ClientConfig:
    """Configuracao do cliente IPTU API."""

    base_url: str = "https://iptuapi.com.br/api/v1"
    timeout: float = 30.0  # segundos
    retry_config: Optional[RetryConfig] = None
    logger: Optional[logging.Logger] = None

    def __post_init__(self):
        if self.retry_config is None:
            self.retry_config = RetryConfig()
        if self.logger is None:
            self.logger = logging.getLogger("iptuapi")
