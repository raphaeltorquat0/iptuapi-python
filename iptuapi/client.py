"""
Cliente principal para a IPTU API.
"""

import time
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import requests

from .config import ClientConfig, RetryConfig
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
)


class IPTUClient:
    """Cliente para interagir com a IPTU API."""

    def __init__(
        self,
        api_key: str,
        config: Optional[ClientConfig] = None,
    ):
        """
        Inicializa o cliente.

        Args:
            api_key: Chave de API para autenticacao
            config: Configuracoes opcionais do cliente
        """
        self.api_key = api_key
        self.config = config or ClientConfig()
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "iptuapi-python/1.0.0",
        })
        self._rate_limit_info: Optional[RateLimitInfo] = None
        self._last_request_id: Optional[str] = None

    @property
    def rate_limit_info(self) -> Optional[RateLimitInfo]:
        """Retorna informacoes do rate limit da ultima requisicao."""
        return self._rate_limit_info

    @property
    def last_request_id(self) -> Optional[str]:
        """Retorna o ID da ultima requisicao."""
        return self._last_request_id

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executa uma requisicao HTTP com retry."""
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        retry_config = self.config.retry_config or RetryConfig()
        delay = retry_config.initial_delay

        for attempt in range(retry_config.max_retries + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    timeout=self.config.timeout,
                )

                # Atualiza rate limit info
                self._rate_limit_info = RateLimitInfo.from_headers(
                    dict(response.headers)
                )
                self._last_request_id = response.headers.get("X-Request-ID")

                # Trata erros HTTP
                if response.status_code >= 400:
                    self._handle_error(response)

                return response.json()

            except requests.exceptions.Timeout:
                if attempt < retry_config.max_retries:
                    time.sleep(delay)
                    delay = min(delay * retry_config.backoff_factor, retry_config.max_delay)
                    continue
                raise TimeoutError(
                    message=f"Timeout apos {self.config.timeout}s",
                    timeout_seconds=self.config.timeout,
                )

            except requests.exceptions.ConnectionError as e:
                if attempt < retry_config.max_retries:
                    time.sleep(delay)
                    delay = min(delay * retry_config.backoff_factor, retry_config.max_delay)
                    continue
                raise NetworkError(
                    message=f"Erro de conexao: {str(e)}",
                    original_error=e,
                )

            except IPTUAPIError:
                raise

            except Exception as e:
                raise NetworkError(
                    message=f"Erro inesperado: {str(e)}",
                    original_error=e,
                )

        raise NetworkError(message="Maximo de tentativas excedido")

    def _handle_error(self, response: requests.Response) -> None:
        """Converte resposta HTTP em excecao apropriada."""
        request_id = response.headers.get("X-Request-ID")

        try:
            data = response.json()
            message = data.get("detail", data.get("message", "Erro desconhecido"))
        except ValueError:
            data = {}
            message = response.text or "Erro desconhecido"

        if response.status_code == 401:
            raise AuthenticationError(message=message, request_id=request_id)

        elif response.status_code == 403:
            raise ForbiddenError(
                message=message,
                required_plan=data.get("required_plan"),
                request_id=request_id,
            )

        elif response.status_code == 404:
            raise NotFoundError(
                message=message,
                resource=data.get("resource"),
                request_id=request_id,
            )

        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                message=message,
                retry_after=retry_after,
                request_id=request_id,
            )

        elif response.status_code in (400, 422):
            raise ValidationError(
                message=message,
                errors=data.get("errors", {}),
                status_code=response.status_code,
                request_id=request_id,
            )

        elif response.status_code >= 500:
            raise ServerError(
                message=message,
                status_code=response.status_code,
                request_id=request_id,
            )

        else:
            raise IPTUAPIError(
                message=message,
                status_code=response.status_code,
                request_id=request_id,
            )

    # ==================== CONSULTAS IPTU ====================

    def consulta_endereco(
        self,
        logradouro: str,
        numero: str,
        cidade: str = "sp",
    ) -> List[Imovel]:
        """
        Consulta imoveis por endereco.

        Args:
            logradouro: Nome da rua/avenida
            numero: Numero do imovel
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Lista de imoveis encontrados
        """
        data = self._make_request(
            "GET",
            "/consulta/endereco",
            params={"logradouro": logradouro, "numero": numero, "cidade": cidade},
        )
        return [Imovel.from_dict(item) for item in data.get("data", [])]

    def consulta_sql(
        self,
        sql: str,
        cidade: str = "sp",
    ) -> List[Imovel]:
        """
        Consulta imovel por numero SQL/Indice Cadastral.

        Requer plano Starter ou superior.

        Args:
            sql: Numero SQL (SP), Indice Cadastral (BH) ou Sequencial (Recife)
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Lista de imoveis encontrados
        """
        data = self._make_request(
            "GET",
            "/consulta/sql",
            params={"sql": sql, "cidade": cidade},
        )
        return [Imovel.from_dict(item) for item in data.get("data", [])]

    def consulta_cep(
        self,
        cep: str,
        cidade: str = "sp",
    ) -> List[Imovel]:
        """
        Consulta imoveis por CEP.

        Args:
            cep: CEP do endereco
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Lista de imoveis encontrados
        """
        data = self._make_request(
            "GET",
            "/consulta/cep",
            params={"cep": cep, "cidade": cidade},
        )
        return [Imovel.from_dict(item) for item in data.get("data", [])]

    def consulta_zoneamento(
        self,
        latitude: float,
        longitude: float,
    ) -> Zoneamento:
        """
        Consulta zoneamento por coordenadas.

        Args:
            latitude: Latitude do ponto
            longitude: Longitude do ponto

        Returns:
            Informacoes de zoneamento
        """
        data = self._make_request(
            "GET",
            "/consulta/zoneamento",
            params={"lat": latitude, "lng": longitude},
        )
        return Zoneamento.from_dict(data.get("data", {}))

    # ==================== VALUATION ====================

    def valuation_estimate(
        self,
        area_terreno: float,
        area_construida: float,
        bairro: str,
        cidade: str = "sp",
        zona: Optional[str] = None,
        tipo_uso: Optional[str] = None,
        tipo_padrao: Optional[str] = None,
        ano_construcao: Optional[int] = None,
    ) -> Valuation:
        """
        Calcula estimativa de valor de mercado.

        Requer plano Pro ou superior.

        Args:
            area_terreno: Area do terreno em m2
            area_construida: Area construida em m2
            bairro: Nome do bairro
            cidade: Codigo da cidade (sp, bh, recife)
            zona: Zona de uso (ex: ZM, ZR)
            tipo_uso: Tipo de uso (Residencial, Comercial, etc)
            tipo_padrao: Padrao de construcao (Alto, Medio, Baixo)
            ano_construcao: Ano de construcao

        Returns:
            Avaliacao de mercado
        """
        params: Dict[str, Any] = {
            "area_terreno": area_terreno,
            "area_construida": area_construida,
            "bairro": bairro,
            "cidade": cidade,
        }
        if zona:
            params["zona"] = zona
        if tipo_uso:
            params["tipo_uso"] = tipo_uso
        if tipo_padrao:
            params["tipo_padrao"] = tipo_padrao
        if ano_construcao:
            params["ano_construcao"] = ano_construcao

        data = self._make_request("GET", "/valuation/estimate", params=params)
        return Valuation.from_dict(data.get("data", {}))

    def valuation_comparables(
        self,
        bairro: str,
        area_min: float,
        area_max: float,
        cidade: str = "sp",
        limit: int = 10,
    ) -> List[Comparavel]:
        """
        Busca imoveis comparaveis.

        Requer plano Pro ou superior.

        Args:
            bairro: Nome do bairro
            area_min: Area minima em m2
            area_max: Area maxima em m2
            cidade: Codigo da cidade (sp, bh, recife)
            limit: Numero maximo de resultados

        Returns:
            Lista de imoveis comparaveis
        """
        data = self._make_request(
            "GET",
            "/valuation/comparables",
            params={
                "bairro": bairro,
                "area_min": area_min,
                "area_max": area_max,
                "cidade": cidade,
                "limit": limit,
            },
        )
        return [Comparavel.from_dict(item) for item in data.get("data", [])]

    # ==================== ITBI ====================

    def itbi_status(
        self,
        protocolo: str,
        cidade: str = "sp",
    ) -> ITBIStatus:
        """
        Consulta status de transacao ITBI.

        Args:
            protocolo: Numero do protocolo ITBI
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Status da transacao
        """
        data = self._make_request(
            "GET",
            "/itbi/status",
            params={"protocolo": protocolo, "cidade": cidade},
        )
        return ITBIStatus.from_dict(data.get("data", {}))

    def itbi_calcular(
        self,
        sql: str,
        valor_transacao: float,
        cidade: str = "sp",
    ) -> ITBICalculo:
        """
        Calcula valor do ITBI.

        Args:
            sql: Numero SQL do imovel
            valor_transacao: Valor da transacao
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Calculo do ITBI
        """
        data = self._make_request(
            "POST",
            "/itbi/calcular",
            json_data={
                "sql": sql,
                "valor_transacao": valor_transacao,
                "cidade": cidade,
            },
        )
        return ITBICalculo.from_dict(data.get("data", {}))

    def itbi_historico(
        self,
        sql: str,
        cidade: str = "sp",
    ) -> List[ITBIHistorico]:
        """
        Consulta historico de transacoes ITBI de um imovel.

        Requer plano Starter ou superior.

        Args:
            sql: Numero SQL do imovel
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Lista de transacoes historicas
        """
        data = self._make_request(
            "GET",
            "/itbi/historico",
            params={"sql": sql, "cidade": cidade},
        )
        return [ITBIHistorico.from_dict(item) for item in data.get("data", [])]

    def itbi_aliquotas(
        self,
        cidade: str = "sp",
    ) -> ITBIAliquota:
        """
        Consulta aliquotas ITBI vigentes.

        Args:
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Aliquotas vigentes
        """
        data = self._make_request(
            "GET",
            "/itbi/aliquotas",
            params={"cidade": cidade},
        )
        return ITBIAliquota.from_dict(data.get("data", {}))

    def itbi_isencoes(
        self,
        cidade: str = "sp",
    ) -> List[ITBIIsencao]:
        """
        Consulta isencoes ITBI disponiveis.

        Args:
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Lista de isencoes disponiveis
        """
        data = self._make_request(
            "GET",
            "/itbi/isencoes",
            params={"cidade": cidade},
        )
        return [ITBIIsencao.from_dict(item) for item in data.get("data", [])]

    def itbi_guia(
        self,
        sql: str,
        valor_transacao: float,
        comprador_nome: str,
        comprador_documento: str,
        vendedor_nome: str,
        vendedor_documento: str,
        cidade: str = "sp",
        comprador_email: Optional[str] = None,
    ) -> ITBIGuia:
        """
        Gera guia de pagamento ITBI.

        Requer plano Starter ou superior.

        Args:
            sql: Numero SQL do imovel
            valor_transacao: Valor da transacao
            comprador_nome: Nome do comprador
            comprador_documento: CPF/CNPJ do comprador
            vendedor_nome: Nome do vendedor
            vendedor_documento: CPF/CNPJ do vendedor
            cidade: Codigo da cidade (sp, bh, recife)
            comprador_email: Email do comprador (opcional)

        Returns:
            Guia de pagamento gerada
        """
        payload: Dict[str, Any] = {
            "sql": sql,
            "valor_transacao": valor_transacao,
            "comprador": {
                "nome": comprador_nome,
                "documento": comprador_documento,
            },
            "vendedor": {
                "nome": vendedor_nome,
                "documento": vendedor_documento,
            },
            "cidade": cidade,
        }
        if comprador_email:
            payload["comprador"]["email"] = comprador_email

        data = self._make_request("POST", "/itbi/guia", json_data=payload)
        return ITBIGuia.from_dict(data.get("data", {}))

    def itbi_validar_guia(
        self,
        protocolo: str,
        cidade: str = "sp",
    ) -> ITBIValidacao:
        """
        Valida autenticidade de uma guia ITBI.

        Args:
            protocolo: Numero do protocolo da guia
            cidade: Codigo da cidade (sp, bh, recife)

        Returns:
            Resultado da validacao
        """
        data = self._make_request(
            "GET",
            "/itbi/validar",
            params={"protocolo": protocolo, "cidade": cidade},
        )
        return ITBIValidacao.from_dict(data.get("data", {}))

    def itbi_simular(
        self,
        valor_transacao: float,
        cidade: str = "sp",
        tipo_financiamento: Optional[str] = None,
        valor_financiado: Optional[float] = None,
    ) -> ITBISimulacao:
        """
        Simula calculo de ITBI.

        Args:
            valor_transacao: Valor da transacao
            cidade: Codigo da cidade (sp, bh, recife)
            tipo_financiamento: Tipo de financiamento (sfh, nao_sfh)
            valor_financiado: Valor financiado

        Returns:
            Resultado da simulacao
        """
        payload: Dict[str, Any] = {
            "valor_transacao": valor_transacao,
            "cidade": cidade,
        }
        if tipo_financiamento:
            payload["tipo_financiamento"] = tipo_financiamento
        if valor_financiado is not None:
            payload["valor_financiado"] = valor_financiado

        data = self._make_request("POST", "/itbi/simular", json_data=payload)
        return ITBISimulacao.from_dict(data.get("data", {}))

    def close(self) -> None:
        """Fecha a sessao HTTP."""
        self._session.close()

    def __enter__(self) -> "IPTUClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
