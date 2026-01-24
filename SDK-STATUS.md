# Python SDK Status

**Última atualização:** 2026-01-24
**Versão:** 1.3.0
**Status:** 🟢 FUNCIONAL

---

## Informações

| Item | Valor |
|------|-------|
| **Versão** | 1.3.0 |
| **Registry** | PyPI (`pip install iptuapi`) |
| **Status** | 🟢 FUNCIONAL |
| **Mínimo** | Python 3.8+ |

## Instalação

```bash
pip install iptuapi
```

## Exemplo Rápido

```python
from iptuapi import IPTUClient

client = IPTUClient("sua_api_key")
cidades = client.iptu_tools_cidades()
print(f"{cidades['total']} cidades disponíveis")
```

## Validação Automática

Este SDK é validado automaticamente:
- ✅ Instalação limpa via pip
- ✅ Import do pacote
- ✅ Teste contra API real (`iptu_tools_cidades`)
- ✅ Teste autenticado (`consulta_endereco`)

---

*Atualizado automaticamente pelo CI/CD*
