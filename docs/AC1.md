# AC1 — 14/09 · versão 1.0

## Objetivo

Entregar a primeira versão funcional: o fluxo completo planilha → relatório HTML, com a base comparativa como funcionalidade da sprint.

## Funcionalidade entregue

**Base comparativa entre quadrimestres** — Upload e validação da planilha, síntese executiva (base, respostas, NPS), composição do NPS e comparativo com o quadrimestre anterior em blocos expansíveis, com variação em pontos percentuais.

## Descrição técnica

`nps/comparativo.py` lê o CSV de indicadores do quadrimestre anterior (`indicador,valor`), valida os campos obrigatórios e oferece dois construtores de linha: `linha_distribuicao` (contagem + % nos dois períodos, variação em pts) e `linha_valor` (NPS e totais em valor absoluto). O motor (`relatorio.py`) pede a cada seção suas linhas de comparativo e monta os blocos expansíveis. A cor da variação respeita o sentido do indicador: queda de neutros/detratores aparece em verde.

A seção `composicao_nps.py` calcula promotores, neutros, detratores e NPS e fornece os cards da síntese.

## Arquivos envolvidos

- `nps/comparativo.py`
- `nps/secoes/composicao_nps.py`
- `nps/relatorio.py`
- `nps/leitura.py`
- `app.py`
- `data/base_comparativa_marco2026.csv`

## Como testar

```bash
pip install -r requirements.txt
streamlit run app.py
```

1. Rodar `streamlit run app.py`, marcar "usar a planilha de exemplo" e gerar.
2. Conferir: 189 contatos, 47 respostas, NPS 98.
3. Abrir "Comparativo" na síntese: Respostas 66 → 47 (−19), NPS 83 → 98 (+15).
4. Abrir "Comparativo" da composição: Promotores 84,8% → 97,9% (+13,0 pts).
5. Trocar para "Não comparar" e gerar de novo: os blocos de comparativo somem.
6. Enviar um CSV sem a coluna `NPS`: a interface mostra o erro de coluna obrigatória.

## Roteiro do vídeo (3 a 4 minutos)

Tom de demonstração de desenvolvimento, não de apresentação comercial. Grave a tela com o sistema rodando.

1. **Problema (30s)** — A cada quadrimestre a empresa faz uma pesquisa de NPS com clientes B2B e consolida tudo à mão. Mostrar a planilha e dizer que o objetivo é gerar o relatório automaticamente e comparar com o período anterior.
2. **Dados (40s)** — Abrir `data/exemplo_base_atual.csv`: uma linha por contato, colunas Abriu?/Respondeu, NPS e respostas. Abrir `base_comparativa_marco2026.csv`: indicadores de Março. Citar que são fictícios e anonimizados.
3. **Sistema (40s)** — Rodar `streamlit run app.py`. Mostrar upload, rótulo do período e a escolha da base comparativa. Clicar em Gerar e mostrar a validação (linhas, respondentes, colunas reconhecidas).
4. **Funcionalidade da sprint (60s)** — No relatório, abrir o Comparativo da síntese e o da composição do NPS. Explicar pts x valor absoluto e a cor invertida para neutros/detratores. Mostrar rapidamente `comparativo.py`.
5. **Resultado (30s)** — Baixar o HTML, abrir no navegador fora do Streamlit. Mostrar o board com AC1 concluída e as próximas planejadas.
