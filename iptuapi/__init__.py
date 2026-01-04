"""
IPTU API - Python SDK

SDK oficial para integracao com a IPTU API.
Acesso a dados de IPTU e ITBI de Sao Paulo, Belo Horizonte e Recife.
"""

from .client import IPTUClient
from .exceptions import (
    IPTUAPIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
    TimeoutError,
    NetworkError,
)
from .models import (
    Imovel,
    Zoneamento,
    Valuation,
    Comparavel,
    ITBIStatus,
    ITBICalculo,
    ITBIHistorico,
    ITBIAliquota,
    ITBIIsencao,
    ITBIGuia,
    ITBIValidacao,
    ITBISimulacao,
    RateLimitInfo,
    # AVM Evaluate
    PropertyEvaluation,
    AVMEstimate,
    ITBIMarketEstimate,
    FinalValuation,
)
from .config import ClientConfig, RetryConfig

__version__ = "1.1.0"
__author__ = "IPTU API"
__email__ = "suporte@iptuapi.com.br"

__all__ = [
    # Client
    "IPTUClient",
    # Config
    "ClientConfig",
    "RetryConfig",
    # Exceptions
    "IPTUAPIError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
    "TimeoutError",
    "NetworkError",
    # Models
    "Imovel",
    "Zoneamento",
    "Valuation",
    "Comparavel",
    "ITBIStatus",
    "ITBICalculo",
    "ITBIHistorico",
    "ITBIAliquota",
    "ITBIIsencao",
    "ITBIGuia",
    "ITBIValidacao",
    "ITBISimulacao",
    "RateLimitInfo",
    # AVM Evaluate Models
    "PropertyEvaluation",
    "AVMEstimate",
    "ITBIMarketEstimate",
    "FinalValuation",
]
