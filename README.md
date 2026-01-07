# IPTU API - Python SDK

SDK oficial Python para integracao com a IPTU API. Acesso a dados de IPTU e ITBI de Sao Paulo, Belo Horizonte e Recife.

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/iptuapi)](https://pypi.org/project/iptuapi/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## Instalacao

```bash
pip install iptuapi
```

## Requisitos

- Python 3.9+
- requests >= 2.28.0

## Uso Rapido

```python
from iptuapi import IPTUClient

client = IPTUClient("sua_api_key")

# Consulta por endereco
imoveis = client.consulta_endereco("Avenida Paulista", "1000", "sp")
for imovel in imoveis:
    print(f"SQL: {imovel.sql}")
    print(f"Valor Venal: R$ {imovel.valor_venal:,.2f}")

# Consulta por SQL (Starter+)
imoveis = client.consulta_sql("008.045.0123-4", "sp")
```

## Configuracao

### Cliente Basico

```python
from iptuapi import IPTUClient

client = IPTUClient("sua_api_key")
```

### Configuracao Avancada

```python
from iptuapi import IPTUClient, ClientConfig, RetryConfig
import logging

# Configurar logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("iptuapi")

# Configuracao de retry
retry_config = RetryConfig(
    max_retries=5,
    initial_delay=1.0,       # segundos
    max_delay=30.0,          # segundos
    backoff_factor=2.0,
    retryable_status_codes=[429, 500, 502, 503, 504],
)

# Configuracao do cliente
config = ClientConfig(
    base_url="https://iptuapi.com.br/api/v1",
    timeout=60.0,
    retry_config=retry_config,
    logger=logger,
)

client = IPTUClient("sua_api_key", config)
```

### Context Manager

```python
from iptuapi import IPTUClient

with IPTUClient("sua_api_key") as client:
    imoveis = client.consulta_endereco("Avenida Paulista", "1000")
    # Sessao fechada automaticamente ao sair do bloco
```

---

## Endpoints de Consulta IPTU

### Consulta por Endereco

Busca dados de IPTU por logradouro e numero. Disponivel em **todos os planos**.

```python
imoveis = client.consulta_endereco("Avenida Paulista", "1000", "sp")

for imovel in imoveis:
    print(f"SQL: {imovel.sql}")
    print(f"Bairro: {imovel.bairro}")
    print(f"Area Terreno: {imovel.area_terreno} m2")
    print(f"Area Construida: {imovel.area_construida} m2")
    print(f"Valor Venal: R$ {imovel.valor_venal:,.2f}")
```

**Parametros:**

| Parametro | Tipo | Obrigatorio | Descricao |
|-----------|------|-------------|-----------|
| logradouro | str | Sim | Nome da rua/avenida |
| numero | str | Sim | Numero do imovel |
| cidade | str | Nao | Codigo da cidade (sp, bh, recife, poa, fortaleza, curitiba, rj, brasilia). Default: sp |

**Resposta (Imovel):**

```python
@dataclass
class Imovel:
    sql: str
    logradouro: str
    numero: str
    bairro: str
    cep: Optional[str]
    area_terreno: Optional[float]
    area_construida: Optional[float]
    valor_venal: Optional[float]
    valor_venal_terreno: Optional[float]
    valor_venal_construcao: Optional[float]
    ano_construcao: Optional[int]
    uso: Optional[str]
    padrao: Optional[str]
```

---

### Consulta por SQL/Indice Cadastral

Busca por identificador unico do imovel. Disponivel a partir do plano **Starter**.

```python
# Sao Paulo - numero SQL
imoveis = client.consulta_sql("008.045.0123-4", "sp")

# Belo Horizonte - indice cadastral
imoveis = client.consulta_sql("007028 005 0086", "bh")

# Recife - sequencial
imoveis = client.consulta_sql("123456", "recife")
```

---

### Consulta por CEP

Busca todos os imoveis de um CEP. Disponivel em **todos os planos**.

```python
imoveis = client.consulta_cep("01310-100", "sp")
print(f"Encontrados: {len(imoveis)} imoveis")
```

---

### Consulta Zoneamento

Retorna informacoes de zoneamento por coordenadas. Disponivel em **todos os planos**.

```python
zoneamento = client.consulta_zoneamento(-23.5505, -46.6333)

print(f"Zona: {zoneamento.zona}")
print(f"Uso Permitido: {zoneamento.uso_permitido}")
print(f"Coeficiente: {zoneamento.coeficiente_aproveitamento}")
print(f"Taxa Ocupacao: {zoneamento.taxa_ocupacao}")
```

---

## Endpoints de Valuation

### Estimativa de Valor de Mercado

Calcula valor estimado de mercado. Disponivel a partir do plano **Pro**.

```python
avaliacao = client.valuation_estimate(
    area_terreno=250.0,
    area_construida=180.0,
    bairro="Pinheiros",
    cidade="sp",
    zona="ZM",
    tipo_uso="Residencial",
    tipo_padrao="Medio",
    ano_construcao=2010,
)

print(f"Valor Estimado: R$ {avaliacao.valor_estimado:,.2f}")
print(f"Confianca: {avaliacao.confianca * 100:.1f}%")
print(f"Faixa: R$ {avaliacao.valor_minimo:,.2f} - R$ {avaliacao.valor_maximo:,.2f}")
print(f"Valor/m2: R$ {avaliacao.valor_m2:,.2f}")
```

**Resposta (Valuation):**

```python
@dataclass
class Valuation:
    valor_estimado: float
    valor_minimo: float
    valor_maximo: float
    confianca: float
    valor_m2: float
    metodologia: str
    data_referencia: str
```

---

### Buscar Comparaveis

Retorna imoveis similares para comparacao. Disponivel a partir do plano **Pro**.

```python
comparaveis = client.valuation_comparables(
    bairro="Pinheiros",
    area_min=150.0,
    area_max=250.0,
    cidade="sp",
    limit=10,
)

for comp in comparaveis:
    print(f"SQL: {comp.sql}")
    print(f"Area: {comp.area_construida:.0f} m2")
    print(f"Valor: R$ {comp.valor_venal:,.2f}")
    print(f"Distancia: {comp.distancia_km:.1f} km")
    print("---")
```

---

## Endpoints de ITBI

### Status da Transacao ITBI

Consulta status de uma transacao ITBI. Disponivel em **todos os planos**.

```python
status = client.itbi_status("ITBI-2024-123456", "sp")

print(f"Protocolo: {status.protocolo}")
print(f"Status: {status.status}")
print(f"Valor Transacao: R$ {status.valor_transacao:,.2f}")
print(f"Valor ITBI: R$ {status.valor_itbi:,.2f}")
```

**Resposta (ITBIStatus):**

```python
@dataclass
class ITBIStatus:
    protocolo: str
    status: str
    data_solicitacao: str
    valor_transacao: float
    valor_venal_referencia: float
    base_calculo: float
    aliquota: float
    valor_itbi: float
    data_aprovacao: Optional[str]
```

---

### Calculo de ITBI

Calcula valor do ITBI para uma transacao. Disponivel em **todos os planos**.

```python
calculo = client.itbi_calcular(
    sql="008.045.0123-4",
    valor_transacao=500000.0,
    cidade="sp",
)

print(f"Base de Calculo: R$ {calculo.base_calculo:,.2f}")
print(f"Aliquota: {calculo.aliquota * 100:.1f}%")
print(f"Valor ITBI: R$ {calculo.valor_itbi:,.2f}")
print(f"Isencao Aplicavel: {'Sim' if calculo.isencao_aplicavel else 'Nao'}")
```

---

### Historico de Transacoes ITBI

Retorna historico de transacoes de um imovel. Disponivel a partir do plano **Starter**.

```python
historico = client.itbi_historico("008.045.0123-4", "sp")

for tx in historico:
    print(f"{tx.data_transacao} - R$ {tx.valor_transacao:,.2f} ({tx.tipo_transacao})")
```

---

### Aliquotas ITBI

Retorna aliquotas vigentes por cidade. Disponivel em **todos os planos**.

```python
aliquotas = client.itbi_aliquotas("sp")

print(f"Aliquota Padrao: {aliquotas.aliquota_padrao * 100:.1f}%")
print(f"Aliquota SFH: {aliquotas.aliquota_financiamento_sfh * 100:.2f}%")
print(f"Base Legal: {aliquotas.base_legal}")
```

---

### Isencoes ITBI

Verifica isencoes aplicaveis. Disponivel em **todos os planos**.

```python
isencoes = client.itbi_isencoes("sp")

for isencao in isencoes:
    print(f"- {isencao.tipo}: {isencao.descricao}")
    print(f"  Requisitos: {', '.join(isencao.requisitos)}")
```

---

### Guia ITBI

Gera guia de pagamento do ITBI. Disponivel a partir do plano **Starter**.

```python
guia = client.itbi_guia(
    sql="008.045.0123-4",
    valor_transacao=500000.0,
    comprador_nome="Joao da Silva",
    comprador_documento="123.456.789-00",
    vendedor_nome="Maria Santos",
    vendedor_documento="987.654.321-00",
    cidade="sp",
    comprador_email="joao@email.com",
)

print(f"Protocolo: {guia.protocolo}")
print(f"Codigo de Barras: {guia.codigo_barras}")
print(f"Vencimento: {guia.data_vencimento}")
print(f"Valor: R$ {guia.valor_itbi:,.2f}")
```

---

### Validar Guia ITBI

Valida autenticidade de uma guia. Disponivel em **todos os planos**.

```python
validacao = client.itbi_validar_guia("ITBI-2024-789012", "sp")

if validacao.valido:
    print("Guia valida!")
    if validacao.pago:
        print(f"Pago em: {validacao.data_pagamento}")
        print(f"Valor pago: R$ {validacao.valor_pago:,.2f}")
else:
    print("Guia invalida!")
```

---

### Simular ITBI

Simula calculo sem gerar guia. Disponivel em **todos os planos**.

```python
simulacao = client.itbi_simular(
    valor_transacao=500000.0,
    cidade="sp",
    tipo_financiamento="sfh",
    valor_financiado=400000.0,
)

print(f"Valor ITBI Total: R$ {simulacao.valor_itbi_total:,.2f}")
print(f"  - Parte financiada (SFH): R$ {simulacao.valor_itbi_financiado:,.2f}")
print(f"  - Parte nao financiada: R$ {simulacao.valor_itbi_nao_financiado:,.2f}")
print(f"Economia com SFH: R$ {simulacao.economia_sfh:,.2f}")
```

**Resposta (ITBISimulacao):**

```python
@dataclass
class ITBISimulacao:
    valor_transacao: float
    valor_financiado: float
    valor_nao_financiado: float
    aliquota_sfh: float
    aliquota_padrao: float
    valor_itbi_financiado: float
    valor_itbi_nao_financiado: float
    valor_itbi_total: float
    economia_sfh: float
```

---

## Tratamento de Erros

```python
from iptuapi import IPTUClient
from iptuapi.exceptions import (
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

client = IPTUClient("sua_api_key")

try:
    imoveis = client.consulta_endereco("Rua Teste", "100")
except AuthenticationError as e:
    print(f"API Key invalida: {e.message}")
except ForbiddenError as e:
    print(f"Plano nao autorizado. Requer: {e.required_plan}")
except NotFoundError as e:
    print(f"Imovel nao encontrado: {e.resource}")
except RateLimitError as e:
    print(f"Rate limit excedido. Retry em {e.retry_after}s")
except ValidationError as e:
    print(f"Parametros invalidos:")
    for field, messages in e.errors.items():
        print(f"  {field}: {', '.join(messages)}")
except ServerError as e:
    print(f"Erro no servidor (retryable): {e.message}")
except TimeoutError as e:
    print(f"Timeout apos {e.timeout_seconds}s")
except NetworkError as e:
    print(f"Erro de conexao: {e.message}")
except IPTUAPIError as e:
    print(f"Erro: {e.message}")
    print(f"Request ID: {e.request_id}")
```

### Propriedades dos Erros

```python
try:
    imoveis = client.consulta_endereco("Rua Teste", "100")
except IPTUAPIError as e:
    print(f"Status Code: {e.status_code}")
    print(f"Request ID: {e.request_id}")
    print(f"Retryable: {'Sim' if e.is_retryable() else 'Nao'}")

    # Converter para dicionario
    error_data = e.to_dict()
    print(error_data)
```

### Verificar Tipo de Erro

```python
import time

try:
    imoveis = client.consulta_endereco("Rua Teste", "100")
except IPTUAPIError as e:
    if e.is_retryable():
        wait_time = e.retry_after if hasattr(e, 'retry_after') else 5
        print(f"Aguardando {wait_time}s antes de tentar novamente...")
        time.sleep(wait_time)
        imoveis = client.consulta_endereco("Rua Teste", "100")
```

---

## Hierarquia de Excecoes

```
IPTUAPIError (base)
├── AuthenticationError (401)
├── ForbiddenError (403)
├── NotFoundError (404)
├── RateLimitError (429) - retryable
├── ValidationError (400, 422)
├── ServerError (5xx) - retryable
├── TimeoutError (408) - retryable
└── NetworkError - retryable
```

---

## Rate Limiting

```python
# Verificar rate limit apos requisicao
rate_limit = client.rate_limit_info
if rate_limit:
    print(f"Limite: {rate_limit.limit}")
    print(f"Restantes: {rate_limit.remaining}")
    print(f"Reset em: {rate_limit.reset_at.strftime('%Y-%m-%d %H:%M:%S')}")

# ID da ultima requisicao (util para suporte)
print(f"Request ID: {client.last_request_id}")
```

### Limites por Plano

| Plano | Requisicoes/mes | Requisicoes/minuto |
|-------|-----------------|-------------------|
| Free | 100 | 10 |
| Starter | 5.000 | 60 |
| Pro | 50.000 | 300 |
| Enterprise | Ilimitado | 1.000 |

---

## Cidades Suportadas

| Codigo | Cidade | Identificador | Registros |
|--------|--------|---------------|-----------|
| sp | Sao Paulo | Numero SQL | 4.5M+ |
| bh | Belo Horizonte | Indice Cadastral | 800K+ |
| recife | Recife | Sequencial | 400K+ |

---

## Exemplo Completo

```python
import time
from iptuapi import IPTUClient, ClientConfig, RetryConfig
from iptuapi.exceptions import IPTUAPIError, RateLimitError
import os

# Configuracao
retry_config = RetryConfig(max_retries=3)
config = ClientConfig(timeout=30.0, retry_config=retry_config)

with IPTUClient(os.environ["IPTU_API_KEY"], config) as client:
    # Lista de enderecos para consultar
    enderecos = [
        ("Avenida Paulista", "1000"),
        ("Rua Augusta", "500"),
        ("Avenida Faria Lima", "3000"),
    ]

    for logradouro, numero in enderecos:
        try:
            imoveis = client.consulta_endereco(logradouro, numero, "sp")

            for imovel in imoveis:
                print(f"SQL: {imovel.sql}, Valor Venal: R$ {imovel.valor_venal:,.2f}")

            # Verificar rate limit
            rate_limit = client.rate_limit_info
            if rate_limit and rate_limit.remaining < 10:
                print(f"Atencao: Apenas {rate_limit.remaining} requisicoes restantes")

        except RateLimitError as e:
            print(f"Rate limit atingido. Aguardando {e.retry_after}s...")
            time.sleep(e.retry_after)
        except IPTUAPIError as e:
            print(f"Erro ao consultar {logradouro}: {e.message}")

    # Exemplo ITBI
    print("\n--- Simulacao ITBI ---")
    try:
        simulacao = client.itbi_simular(
            valor_transacao=800000.0,
            cidade="sp",
            tipo_financiamento="sfh",
            valor_financiado=600000.0,
        )
        print(f"Valor ITBI: R$ {simulacao.valor_itbi_total:,.2f}")
        print(f"Economia com SFH: R$ {simulacao.economia_sfh:,.2f}")
    except IPTUAPIError as e:
        print(f"Erro na simulacao ITBI: {e.message}")
```

---

## Testes

```bash
# Instalar dependencias de desenvolvimento
pip install -e ".[dev]"

# Rodar testes
pytest

# Com coverage
pytest --cov=iptuapi --cov-report=html

# Apenas um arquivo
pytest tests/test_client.py
```

### Analise Estatica

```bash
# Mypy
mypy iptuapi

# Ruff (linting)
ruff check iptuapi
```

---

## Licenca

Copyright (c) 2025-2026 IPTU API. Todos os direitos reservados.

Este software e propriedade exclusiva da IPTU API. O uso esta sujeito aos termos de servico disponiveis em https://iptuapi.com.br/termos

---

## Links

- [Documentacao](https://iptuapi.com.br/docs)
- [API Reference](https://iptuapi.com.br/docs/api)
- [Portal do Desenvolvedor](https://iptuapi.com.br/dashboard)
- [Suporte](mailto:suporte@iptuapi.com.br)
