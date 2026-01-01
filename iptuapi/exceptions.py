"""
Excecoes customizadas para a IPTU API.
"""

from typing import Any, Dict, List, Optional


class IPTUAPIError(Exception):
    """Excecao base para todos os erros da IPTU API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.response_data = response_data or {}

    def is_retryable(self) -> bool:
        """Verifica se o erro pode ser retentado."""
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Converte o erro para dicionario."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "request_id": self.request_id,
            "retryable": self.is_retryable(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code})"


class AuthenticationError(IPTUAPIError):
    """Erro de autenticacao (401). API Key invalida ou ausente."""

    def __init__(
        self,
        message: str = "API Key invalida ou ausente",
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=401, request_id=request_id)


class ForbiddenError(IPTUAPIError):
    """Erro de autorizacao (403). Plano nao permite acesso ao recurso."""

    def __init__(
        self,
        message: str = "Acesso negado",
        required_plan: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=403, request_id=request_id)
        self.required_plan = required_plan

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["required_plan"] = self.required_plan
        return data


class NotFoundError(IPTUAPIError):
    """Erro de recurso nao encontrado (404)."""

    def __init__(
        self,
        message: str = "Recurso nao encontrado",
        resource: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=404, request_id=request_id)
        self.resource = resource

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["resource"] = self.resource
        return data


class RateLimitError(IPTUAPIError):
    """Erro de rate limit excedido (429)."""

    def __init__(
        self,
        message: str = "Rate limit excedido",
        retry_after: Optional[int] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=429, request_id=request_id)
        self.retry_after = retry_after or 60

    def is_retryable(self) -> bool:
        return True

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["retry_after"] = self.retry_after
        return data


class ValidationError(IPTUAPIError):
    """Erro de validacao de parametros (400, 422)."""

    def __init__(
        self,
        message: str = "Parametros invalidos",
        errors: Optional[Dict[str, List[str]]] = None,
        status_code: int = 422,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=status_code, request_id=request_id)
        self.errors = errors or {}

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["validation_errors"] = self.errors
        return data


class ServerError(IPTUAPIError):
    """Erro interno do servidor (5xx). Retryable."""

    def __init__(
        self,
        message: str = "Erro interno do servidor",
        status_code: int = 500,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=status_code, request_id=request_id)

    def is_retryable(self) -> bool:
        return True


class TimeoutError(IPTUAPIError):
    """Erro de timeout na requisicao."""

    def __init__(
        self,
        message: str = "Timeout na requisicao",
        timeout_seconds: Optional[float] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code=408, request_id=request_id)
        self.timeout_seconds = timeout_seconds

    def is_retryable(self) -> bool:
        return True

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["timeout_seconds"] = self.timeout_seconds
        return data


class NetworkError(IPTUAPIError):
    """Erro de conexao de rede."""

    def __init__(
        self,
        message: str = "Erro de conexao",
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message, status_code=None, request_id=None)
        self.original_error = original_error

    def is_retryable(self) -> bool:
        return True
