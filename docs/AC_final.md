# Entrega final — 22/11 · versão 4.0

> Entregue junto com a AC3 no mesmo pacote. O roteiro de vídeo abaixo cobre as duas
> funcionalidades; a documentação da AC3 está em [`AC3.md`](AC3.md).

## Objetivo

Entregar a versão final consolidada, com a análise das respostas abertas.

## Funcionalidade entregue

**Feedback qualitativo** — Abas por pergunta aberta, nuvem de temas com codificação por palavras-chave, respostas na íntegra expansíveis e respostas agrupadas por CSM.

## Descrição técnica

Novos arquivos `nps/secoes/qualitativo.py` e `nps/temas.py`. As respostas abertas são codificadas por palavras-chave (texto sem acento, expressões regulares, regras de exclusão entre temas sobrepostos). Cada pergunta vira uma aba com nuvem de temas (circle packing em SVG) e respostas na íntegra; a aba de atendimento classifica cada resposta (elogio, sem apontamento, ressalva) e agrupa por CSM em abas laterais.

## Arquivos envolvidos

- `nps/secoes/qualitativo.py`
- `nps/temas.py`
- `nps/secoes/__init__.py`
- `nps/versao.py`
- `docs/diagramas.md` e `docs/diagramas/` — diagrama de caso de uso, diagrama de classes e MER

## Modelagem entregue

Além do código, a entrega final traz a modelagem pedida, em `docs/diagramas.md`:

- **Diagrama de caso de uso** — atores (Analista de CX e Gestor de CX), os casos de uso do
  sistema e os relacionamentos `«include»` e `«extend»`.
- **Diagrama de classes** — as classes de `nps/` e a interface `Secao`, que as quatro
  funcionalidades implementam; cada subclasse está marcada com a entrega em que nasceu.
- **MER** — o modelo entidade-relacionamento da base da pesquisa, com as tabelas
  associativas `AVALIACAO_CSAT` e `RESPOSTA_TEMA` e a correspondência com os CSVs.

## Como testar

```bash
pip install -r requirements.txt
streamlit run app.py
```

1. Gerar com a planilha de exemplo.
2. Aba "Principal benefício": 35 respostas; maior tema "Atendimento próximo e resolutivo".
3. Aba "Como podemos melhorar": 27 respostas; "Nada a melhorar / já satisfeito" e "Ampliar rede fora de SP" no topo.
4. Aba "Atendimento do CSM": 23 respostas; clicar em cada CSM na lateral.
5. "Expandir todos" abre todas as respostas.

## Roteiro do vídeo (3 a 4 minutos)

Tom de demonstração de desenvolvimento, não de apresentação comercial. Grave a tela com o sistema rodando.

1. **Visão geral (30s)** — Problema, dados e as 4 entregas do roadmap.
2. **Modelagem (60s)** — Abrir `docs/diagramas.md`. No **caso de uso**, apontar os dois atores e
   explicar um `«include»` (validar a planilha sempre acontece) e um `«extend»` (comparar só quando
   há base comparativa). No **diagrama de classes**, mostrar a interface `Secao` e dizer que cada AC
   acrescentou uma classe que a implementa. No **MER**, mostrar que a planilha é a junção de
   `CONTATO + ENVIO_PESQUISA + RESPOSTA` e que o CSV comparativo é `PERIODO + INDICADOR_CONSOLIDADO`.
3. **Fluxo completo (30s)** — Upload, validação, base comparativa e geração.
4. **AC3 — satisfação (45s)** — PMF: 38 de 47 (80,9%) ficariam muito desapontados sem o serviço,
   contra 63,6% em março (+17,2 pts); citar a regra de realocação (2 casos). CSAT: 4,95/5
   consolidado, 187 das 188 avaliações com nota 4 ou 5; abrir "Ver colunas de detalhe".
   Autorização de contato: 43 sim (91,5%).
5. **Entrega final — feedback qualitativo (60s)** — Abas qualitativas, nuvem de temas,
   respostas por CSM. Mostrar `nps/temas.py` e como ajustar um tema.
6. **Resultado final (30s)** — Percorrer o relatório inteiro, baixar o HTML e mostrar o board
   100% concluído.
