"""Testes para o cliente IPTU API."""

import pytest
import responses
from iptuapi import IPTUClient, ClientConfig, RetryConfig
from iptuapi.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


@pytest.fixture
def client():
    """Cria um cliente para testes."""
    config = ClientConfig(base_url="https://api.test.com/v1")
    return IPTUClient("test_api_key", config)


class TestConsultaEndereco:
    """Testes para consulta por endereco."""

    @responses.activate
    def test_consulta_endereco_success(self, client):
        """Testa consulta por endereco com sucesso."""
        responses.add(
            responses.GET,
            "https://api.test.com/v1/consulta/endereco",
            json={
                "success": True,
                "data": [
                    {
                        "sql": "008.045.0123-4",
                        "logradouro": "AV PAULISTA",
                        "numero": "1000",
                        "bairro": "BELA VISTA",
                        "valor_venal": 2500000.0,
                    }
                ],
            },
            status=200,
        )

        result = client.consulta_endereco("Avenida Paulista", "1000", "sp")

        assert len(result) == 1
        assert result[0].sql == "008.045.0123-4"
        assert result[0].valor_venal == 2500000.0

    @responses.activate
    def test_consulta_endereco_not_found(self, client):
        """Testa consulta por endereco nao encontrado."""
        responses.add(
            responses.GET,
            "https://api.test.com/v1/consulta/endereco",
            json={"detail": "Imovel nao encontrado"},
            status=404,
        )

        with pytest.raises(NotFoundError):
            client.consulta_endereco("Rua Inexistente", "9999", "sp")


class TestAuthentication:
    """Testes de autenticacao."""

    @responses.activate
    def test_invalid_api_key(self, client):
        """Testa erro de API key invalida."""
        responses.add(
            responses.GET,
            "https://api.test.com/v1/consulta/endereco",
            json={"detail": "API Key invalida"},
            status=401,
        )

        with pytest.raises(AuthenticationError):
            client.consulta_endereco("Avenida Paulista", "1000", "sp")


class TestRateLimit:
    """Testes de rate limit."""

    @responses.activate
    def test_rate_limit_exceeded(self, client):
        """Testa erro de rate limit excedido."""
        responses.add(
            responses.GET,
            "https://api.test.com/v1/consulta/endereco",
            json={"detail": "Rate limit excedido"},
            status=429,
            headers={"Retry-After": "60"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.consulta_endereco("Avenida Paulista", "1000", "sp")

        assert exc_info.value.retry_after == 60
        assert exc_info.value.is_retryable() is True


class TestITBI:
    """Testes para endpoints ITBI."""

    @responses.activate
    def test_itbi_simular(self, client):
        """Testa simulacao ITBI."""
        responses.add(
            responses.POST,
            "https://api.test.com/v1/itbi/simular",
            json={
                "success": True,
                "data": {
                    "valor_transacao": 500000.0,
                    "valor_financiado": 400000.0,
                    "valor_nao_financiado": 100000.0,
                    "aliquota_sfh": 0.005,
                    "aliquota_padrao": 0.03,
                    "valor_itbi_financiado": 2000.0,
                    "valor_itbi_nao_financiado": 3000.0,
                    "valor_itbi_total": 5000.0,
                    "economia_sfh": 10000.0,
                },
            },
            status=200,
        )

        result = client.itbi_simular(
            valor_transacao=500000.0,
            cidade="sp",
            tipo_financiamento="sfh",
            valor_financiado=400000.0,
        )

        assert result.valor_itbi_total == 5000.0
        assert result.economia_sfh == 10000.0


class TestExceptions:
    """Testes para excecoes."""

    def test_exception_to_dict(self):
        """Testa conversao de excecao para dicionario."""
        error = RateLimitError(
            message="Rate limit excedido",
            retry_after=60,
            request_id="req_123",
        )

        data = error.to_dict()

        assert data["error"] == "RateLimitError"
        assert data["retry_after"] == 60
        assert data["retryable"] is True

    def test_forbidden_with_required_plan(self):
        """Testa excecao Forbidden com plano requerido."""
        error = ForbiddenError(
            message="Plano nao autorizado",
            required_plan="pro",
            request_id="req_123",
        )

        assert error.required_plan == "pro"
        data = error.to_dict()
        assert data["required_plan"] == "pro"
