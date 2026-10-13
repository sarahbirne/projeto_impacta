# AC2 — 13/10 · versão 2.0

## Objetivo

Adicionar o funil de engajamento: quanto da base foi alcançada, quanto respondeu e por qual canal.

## Funcionalidade entregue

**Funil de engajamento da pesquisa** — Funil base → alcançados → respondentes, cards de conversão e origem das respostas (follow-up do CSM x e-mail marketing).

## Descrição técnica

Novo módulo `nps/secoes/funil.py`. Alcançados = contatos com `Abriu?` igual a `Sim` ou `FUP`. Origem: respondente com `Abriu? = Sim` conta como e-mail marketing; os demais como follow-up do CSM. O módulo contribui dois cards para a síntese (alcançados e % por follow-up) e a seção 2 do relatório (funil em SVG, cards de conversão, barras de origem). Nenhum outro módulo foi alterado além do registro em `secoes/__init__.py`.

## Arquivos envolvidos

- `nps/secoes/funil.py`
- `nps/secoes/__init__.py`
- `nps/relatorio.py` (seção registrada)
- `nps/versao.py`

## Como testar

```bash
pip install -r requirements.txt
streamlit run app.py
```

1. Gerar com a planilha de exemplo.
2. Conferir o funil: 189 → 94 → 47.
3. Conversão: alcance 49,7%, conversão 50,0%, resposta 24,9%.
4. Origem: follow-up 24 (51,1%) e e-mail marketing 23 (48,9%).
5. Na síntese devem aparecer 5 cards (3 + 2).

## Roteiro do vídeo (3 a 4 minutos)

Tom de demonstração de desenvolvimento, não de apresentação comercial. Grave a tela com o sistema rodando.

1. **Recapitulando (20s)** — Na AC1 entregamos o relatório com a base comparativa.
2. **Problema (30s)** — Só o NPS não mostra se a pesquisa chegou nas pessoas e qual canal funcionou.
3. **Dados (30s)** — Mostrar as colunas `Abriu?` (Sim/Não/FUP) e `Respondeu` e a regra de origem.
4. **Funcionalidade da sprint (70s)** — Gerar o relatório, navegar até a seção Funil: etapas, taxas e origem das respostas. Mostrar `funil.py` e o registro do módulo.
5. **Resultado (30s)** — Baixar o HTML e mostrar o board com AC2 concluída.
