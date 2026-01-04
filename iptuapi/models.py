"""
Modelos de dados para a IPTU API.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class RateLimitInfo:
    """Informacoes de rate limit."""

    limit: int
    remaining: int
    reset_at: datetime

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> Optional["RateLimitInfo"]:
        """Cria RateLimitInfo a partir dos headers da resposta."""
        try:
            return cls(
                limit=int(headers.get("X-RateLimit-Limit", 0)),
                remaining=int(headers.get("X-RateLimit-Remaining", 0)),
                reset_at=datetime.fromtimestamp(
                    int(headers.get("X-RateLimit-Reset", 0))
                ),
            )
        except (ValueError, TypeError):
            return None


@dataclass
class Imovel:
    """Dados de um imovel."""

    sql: str
    logradouro: str
    numero: str
    bairro: str
    cep: Optional[str] = None
    area_terreno: Optional[float] = None
    area_construida: Optional[float] = None
    valor_venal: Optional[float] = None
    valor_venal_terreno: Optional[float] = None
    valor_venal_construcao: Optional[float] = None
    ano_construcao: Optional[int] = None
    uso: Optional[str] = None
    padrao: Optional[str] = None
    testada: Optional[float] = None
    fracao_ideal: Optional[float] = None
    quantidade_pavimentos: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Imovel":
        """Cria Imovel a partir de um dicionario."""
        return cls(
            sql=data.get("sql", ""),
            logradouro=data.get("logradouro", ""),
            numero=data.get("numero", ""),
            bairro=data.get("bairro", ""),
            cep=data.get("cep"),
            area_terreno=data.get("area_terreno"),
            area_construida=data.get("area_construida"),
            valor_venal=data.get("valor_venal"),
            valor_venal_terreno=data.get("valor_venal_terreno"),
            valor_venal_construcao=data.get("valor_venal_construcao"),
            ano_construcao=data.get("ano_construcao"),
            uso=data.get("uso"),
            padrao=data.get("padrao"),
            testada=data.get("testada"),
            fracao_ideal=data.get("fracao_ideal"),
            quantidade_pavimentos=data.get("quantidade_pavimentos"),
        )


@dataclass
class Zoneamento:
    """Dados de zoneamento."""

    zona: str
    uso_permitido: str
    coeficiente_aproveitamento: Optional[float] = None
    taxa_ocupacao: Optional[float] = None
    gabarito: Optional[int] = None
    recuo_frontal: Optional[float] = None
    legislacao: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Zoneamento":
        """Cria Zoneamento a partir de um dicionario."""
        return cls(
            zona=data.get("zona", ""),
            uso_permitido=data.get("uso_permitido", ""),
            coeficiente_aproveitamento=data.get("coeficiente_aproveitamento"),
            taxa_ocupacao=data.get("taxa_ocupacao"),
            gabarito=data.get("gabarito"),
            recuo_frontal=data.get("recuo_frontal"),
            legislacao=data.get("legislacao"),
        )


@dataclass
class Valuation:
    """Resultado de avaliacao de mercado."""

    valor_estimado: float
    valor_minimo: float
    valor_maximo: float
    confianca: float
    valor_m2: float
    metodologia: str
    data_referencia: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Valuation":
        """Cria Valuation a partir de um dicionario."""
        return cls(
            valor_estimado=data.get("valor_estimado", 0),
            valor_minimo=data.get("valor_minimo", 0),
            valor_maximo=data.get("valor_maximo", 0),
            confianca=data.get("confianca", 0),
            valor_m2=data.get("valor_m2", 0),
            metodologia=data.get("metodologia", ""),
            data_referencia=data.get("data_referencia", ""),
        )


@dataclass
class Comparavel:
    """Imovel comparavel para avaliacao."""

    sql: str
    logradouro: str
    bairro: str
    area_construida: float
    valor_venal: float
    valor_m2: float
    distancia_km: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Comparavel":
        """Cria Comparavel a partir de um dicionario."""
        return cls(
            sql=data.get("sql", ""),
            logradouro=data.get("logradouro", ""),
            bairro=data.get("bairro", ""),
            area_construida=data.get("area_construida", 0),
            valor_venal=data.get("valor_venal", 0),
            valor_m2=data.get("valor_m2", 0),
            distancia_km=data.get("distancia_km"),
        )


@dataclass
class ITBIStatus:
    """Status de transacao ITBI."""

    protocolo: str
    status: str
    data_solicitacao: str
    valor_transacao: float
    valor_venal_referencia: float
    base_calculo: float
    aliquota: float
    valor_itbi: float
    data_aprovacao: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBIStatus":
        """Cria ITBIStatus a partir de um dicionario."""
        return cls(
            protocolo=data.get("protocolo", ""),
            status=data.get("status", ""),
            data_solicitacao=data.get("data_solicitacao", ""),
            valor_transacao=data.get("valor_transacao", 0),
            valor_venal_referencia=data.get("valor_venal_referencia", 0),
            base_calculo=data.get("base_calculo", 0),
            aliquota=data.get("aliquota", 0),
            valor_itbi=data.get("valor_itbi", 0),
            data_aprovacao=data.get("data_aprovacao"),
        )


@dataclass
class ITBICalculo:
    """Resultado de calculo ITBI."""

    sql: str
    valor_transacao: float
    valor_venal_referencia: float
    base_calculo: float
    aliquota: float
    valor_itbi: float
    isencao_aplicavel: bool
    fundamentacao_legal: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBICalculo":
        """Cria ITBICalculo a partir de um dicionario."""
        return cls(
            sql=data.get("sql", ""),
            valor_transacao=data.get("valor_transacao", 0),
            valor_venal_referencia=data.get("valor_venal_referencia", 0),
            base_calculo=data.get("base_calculo", 0),
            aliquota=data.get("aliquota", 0),
            valor_itbi=data.get("valor_itbi", 0),
            isencao_aplicavel=data.get("isencao_aplicavel", False),
            fundamentacao_legal=data.get("fundamentacao_legal", ""),
        )


@dataclass
class ITBIHistorico:
    """Transacao historica de ITBI."""

    protocolo: str
    data_transacao: str
    tipo_transacao: str
    valor_transacao: float
    valor_itbi: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBIHistorico":
        """Cria ITBIHistorico a partir de um dicionario."""
        return cls(
            protocolo=data.get("protocolo", ""),
            data_transacao=data.get("data_transacao", ""),
            tipo_transacao=data.get("tipo_transacao", ""),
            valor_transacao=data.get("valor_transacao", 0),
            valor_itbi=data.get("valor_itbi", 0),
        )


@dataclass
class ITBIAliquota:
    """Aliquotas ITBI de uma cidade."""

    cidade: str
    aliquota_padrao: float
    aliquota_financiamento_sfh: float
    valor_minimo_isencao: float
    base_legal: str
    vigencia: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBIAliquota":
        """Cria ITBIAliquota a partir de um dicionario."""
        return cls(
            cidade=data.get("cidade", ""),
            aliquota_padrao=data.get("aliquota_padrao", 0),
            aliquota_financiamento_sfh=data.get("aliquota_financiamento_sfh", 0),
            valor_minimo_isencao=data.get("valor_minimo_isencao", 0),
            base_legal=data.get("base_legal", ""),
            vigencia=data.get("vigencia", ""),
        )


@dataclass
class ITBIIsencao:
    """Isencao de ITBI."""

    tipo: str
    descricao: str
    requisitos: List[str]
    base_legal: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBIIsencao":
        """Cria ITBIIsencao a partir de um dicionario."""
        return cls(
            tipo=data.get("tipo", ""),
            descricao=data.get("descricao", ""),
            requisitos=data.get("requisitos", []),
            base_legal=data.get("base_legal", ""),
        )


@dataclass
class ITBIGuia:
    """Guia de pagamento ITBI."""

    protocolo: str
    codigo_barras: str
    linha_digitavel: str
    data_emissao: str
    data_vencimento: str
    valor_itbi: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBIGuia":
        """Cria ITBIGuia a partir de um dicionario."""
        return cls(
            protocolo=data.get("protocolo", ""),
            codigo_barras=data.get("codigo_barras", ""),
            linha_digitavel=data.get("linha_digitavel", ""),
            data_emissao=data.get("data_emissao", ""),
            data_vencimento=data.get("data_vencimento", ""),
            valor_itbi=data.get("valor_itbi", 0),
        )


@dataclass
class ITBIValidacao:
    """Resultado de validacao de guia ITBI."""

    protocolo: str
    valido: bool
    pago: bool
    data_pagamento: Optional[str] = None
    valor_pago: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBIValidacao":
        """Cria ITBIValidacao a partir de um dicionario."""
        return cls(
            protocolo=data.get("protocolo", ""),
            valido=data.get("valido", False),
            pago=data.get("pago", False),
            data_pagamento=data.get("data_pagamento"),
            valor_pago=data.get("valor_pago"),
        )


@dataclass
class ITBISimulacao:
    """Resultado de simulacao ITBI."""

    valor_transacao: float
    valor_financiado: float
    valor_nao_financiado: float
    aliquota_sfh: float
    aliquota_padrao: float
    valor_itbi_financiado: float
    valor_itbi_nao_financiado: float
    valor_itbi_total: float
    economia_sfh: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ITBISimulacao":
        """Cria ITBISimulacao a partir de um dicionario."""
        return cls(
            valor_transacao=data.get("valor_transacao", 0),
            valor_financiado=data.get("valor_financiado", 0),
            valor_nao_financiado=data.get("valor_nao_financiado", 0),
            aliquota_sfh=data.get("aliquota_sfh", 0),
            aliquota_padrao=data.get("aliquota_padrao", 0),
            valor_itbi_financiado=data.get("valor_itbi_financiado", 0),
            valor_itbi_nao_financiado=data.get("valor_itbi_nao_financiado", 0),
            valor_itbi_total=data.get("valor_itbi_total", 0),
            economia_sfh=data.get("economia_sfh", 0),
        )


# ==================== AVM EVALUATE ====================

@dataclass
class AVMEstimate:
    """Estimativa do modelo AVM (Machine Learning)."""

    valor_estimado: float
    valor_minimo: float
    valor_maximo: float
    valor_m2: float
    confianca: float
    modelo_versao: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["AVMEstimate"]:
        """Cria AVMEstimate a partir de um dicionario."""
        if not data:
            return None
        return cls(
            valor_estimado=data.get("valor_estimado", 0),
            valor_minimo=data.get("valor_minimo", 0),
            valor_maximo=data.get("valor_maximo", 0),
            valor_m2=data.get("valor_m2", 0),
            confianca=data.get("confianca", 0),
            modelo_versao=data.get("modelo_versao", ""),
        )


@dataclass
class ITBIMarketEstimate:
    """Estimativa baseada em transacoes ITBI reais."""

    valor_estimado: float
    faixa_minima: float
    faixa_maxima: float
    valor_m2_mediana: float
    total_transacoes: int
    periodo: str
    fonte: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["ITBIMarketEstimate"]:
        """Cria ITBIMarketEstimate a partir de um dicionario."""
        if not data:
            return None
        return cls(
            valor_estimado=data.get("valor_estimado", 0),
            faixa_minima=data.get("faixa_minima", 0),
            faixa_maxima=data.get("faixa_maxima", 0),
            valor_m2_mediana=data.get("valor_m2_mediana", 0),
            total_transacoes=data.get("total_transacoes", 0),
            periodo=data.get("periodo", ""),
            fonte=data.get("fonte", ""),
        )


@dataclass
class FinalValuation:
    """Valor final combinado (AVM + ITBI)."""

    estimado: float
    minimo: float
    maximo: float
    metodo: str
    peso_avm: float
    peso_itbi: float
    confianca: float
    nota: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FinalValuation":
        """Cria FinalValuation a partir de um dicionario."""
        return cls(
            estimado=data.get("estimado", 0),
            minimo=data.get("minimo", 0),
            maximo=data.get("maximo", 0),
            metodo=data.get("metodo", ""),
            peso_avm=data.get("peso_avm", 0),
            peso_itbi=data.get("peso_itbi", 0),
            confianca=data.get("confianca", 0),
            nota=data.get("nota"),
        )


@dataclass
class PropertyEvaluation:
    """
    Resultado completo da avaliacao de imovel.

    Combina dados do IPTU, modelo AVM (ML) e transacoes ITBI
    para fornecer uma avaliacao abrangente do valor de mercado.
    """

    imovel: Dict[str, Any]
    avaliacao_avm: Optional[AVMEstimate]
    avaliacao_itbi: Optional[ITBIMarketEstimate]
    valor_final: FinalValuation
    comparaveis: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PropertyEvaluation":
        """Cria PropertyEvaluation a partir de um dicionario."""
        return cls(
            imovel=data.get("imovel", {}),
            avaliacao_avm=AVMEstimate.from_dict(data.get("avaliacao_avm")),
            avaliacao_itbi=ITBIMarketEstimate.from_dict(data.get("avaliacao_itbi")),
            valor_final=FinalValuation.from_dict(data.get("valor_final", {})),
            comparaveis=data.get("comparaveis"),
            metadata=data.get("metadata", {}),
        )

    @property
    def valor_estimado(self) -> float:
        """Retorna o valor estimado final."""
        return self.valor_final.estimado

    @property
    def fontes_utilizadas(self) -> List[str]:
        """Retorna lista de fontes de dados utilizadas."""
        return self.metadata.get("fontes", [])
