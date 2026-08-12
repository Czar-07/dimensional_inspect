# DIMENSION-RATE

Sistema web para análise de relatórios dimensionais em PDF e cálculo automático do RATE.

## Estrutura

- `app/` — aplicação Flask, domínio, serviços, API e interface.
- `tests/` — testes automatizados do motor de extração e cálculo.
- `run.py` — entrada local da aplicação.
- `requirements.txt` — dependências Python.

## Executar

```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python run.py
```

Abra `http://127.0.0.1:5000`.

## Interface

A interface foi reorganizada em uma arquitetura de painel profissional: menu lateral, barra superior, análise por upload, indicadores, gráficos, auditoria, relatório completo e histórico local.
