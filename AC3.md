# AC3 — 08/11 · versão 3.0

## Objetivo

Adicionar os indicadores de satisfação: PMF, CSAT do atendimento e autorização para aprofundamento, com comparativo.

## Funcionalidade entregue

**Satisfação: PMF, CSAT e autorização de contato** — PMF com regra de realocação, CSAT dos 4 atributos de atendimento com distribuição ocultável, autorização para aprofundamento e os respectivos comparativos.

## Descrição técnica

Novo módulo `nps/secoes/satisfacao.py`, inserido na seção "NPS & satisfação" depois da composição do NPS. Aplica a regra de realocação do PMF ("nada desapontado" com NPS 10 → "muito desapontado"), calcula média e distribuição das notas de CSAT por atributo (tabela com colunas ocultáveis) e consolida a autorização de contato. Contribui cards (PMF e CSAT) e três linhas no comparativo da síntese, reutilizando `comparativo.py` da AC1.

## Arquivos envolvidos

- `nps/secoes/satisfacao.py`
- `nps/secoes/__init__.py`
- `nps/versao.py`

## Como testar

```bash
pip install -r requirements.txt
streamlit run app.py
```

1. Gerar com a planilha de exemplo.
2. PMF: 38 muito (80,9%), 9 um pouco, 0 nada — nota de método informa 2 realocações.
3. CSAT: consolidado 4,95/5; clicar em "Ver colunas de detalhe" mostra as notas 5, 4 e 3.
4. Comparativo da síntese: PMF 63,6% → 80,9% (+17,2 pts); CSAT 4,80 → 4,95 (+0,15).
5. Autorização de contato: Sim 43 (91,5%), Não 4.

## Roteiro do vídeo (3 a 4 minutos)

Tom de demonstração de desenvolvimento, não de apresentação comercial. Grave a tela com o sistema rodando.

1. **Recapitulando (20s)** — AC1: comparativo. AC2: funil.
2. **Problema (30s)** — NPS diz se recomendam; faltava medir dependência do serviço (PMF) e a qualidade do atendimento (CSAT).
3. **Dados (30s)** — Mostrar as colunas de PMF e dos 4 atributos de CSAT e explicar a regra de realocação.
4. **Funcionalidade da sprint (70s)** — Gerar, mostrar PMF, CSAT com distribuição e os comparativos. Mostrar `satisfacao.py`.
5. **Resultado (30s)** — Baixar o HTML e mostrar o board com AC3 concluída.
