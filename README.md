# Projeto de NPS (Net Promoter Score) para empresas

**Versão 2.0 — AC2 (13/10)** · funcionalidade da sprint: **Funil de engajamento da pesquisa**

## Contexto

Projeto desenvolvido para a disciplina de Projeto de Software, em 4 entregas incrementais. É uma solução de dados/BI para empresas B2B que fazem, a cada quadrimestre, uma pesquisa de NPS com seus clientes.

A base de contatos foi gerada de forma fictícia no CRM (nome, sobrenome, celular, e-mail, empresa). A pesquisa do quadrimestre foi simulada sobre essa base e tratada na planilha de controle *base contatada vs. respostas*. Este sistema recebe essa planilha e gera um relatório HTML padronizado.

## Objetivo

Transformar a planilha da pesquisa em um relatório analítico reexecutável: calcular os indicadores do período atual e compará-los com o quadrimestre anterior, para identificar evolução, regressões e padrões.

## Funcionalidades desta versão (2.0)

- Upload e validação da planilha (CSV)
- Síntese executiva: base, respostas e NPS
- Composição do NPS (promotores, neutros, detratores)
- Base comparativa com o quadrimestre anterior (variação em p.p.)
- Notas de método e qualidade de dado
- Download do relatório HTML
- Funil de engajamento da pesquisa
- Cards de conversão (alcance, conversão, resposta)
- Origem das respostas: follow-up do CSM x e-mail marketing

### Novidades desta entrega

- Funil de engajamento da pesquisa
- Cards de conversão (alcance, conversão, resposta)
- Origem das respostas: follow-up do CSM x e-mail marketing

## Roadmap acadêmico

| Entrega | Data | Versão | Funcionalidade da sprint | Status |
|---|---|---|---|---|
| AC1 | 14/09 | 1.0 | Base comparativa entre quadrimestres | ✅ Concluída |
| AC2 | 13/10 | 2.0 | Funil de engajamento da pesquisa | ✅ Entregue nesta versão |
| AC3 | 08/11 | 3.0 | Satisfação: PMF, CSAT e autorização de contato | ⏳ Planejada |
| Entrega final | 22/11 | 4.0 | Feedback qualitativo | ⏳ Planejada |

## Arquitetura

```
Planilha CSV ──► leitura.py ──► secoes/*.py ──► relatorio.py ──► HTML autocontido
 (pesquisa)     mapeia colunas   cálculo por      síntese +          (CSS, JS e SVG
                normaliza        funcionalidade   comparativo        embutidos)
                valida                 ▲
CSV indicadores ──► comparativo.py ────┘
 (período anterior)
```

Cada funcionalidade é um módulo em `nps/secoes/` com a mesma interface (`calcular`, `kpis`, `linhas_comparativo`, `render`, `notas_metodo`). Uma nova entrega adiciona um módulo e o registra em `nps/secoes/__init__.py`, sem reescrever o que já existe.

## Tecnologias

- Python 3.10+
- pandas — leitura e tratamento da planilha
- Streamlit — interface de upload, validação e prévia
- HTML, CSS e JavaScript — relatório final; gráficos gerados em SVG pelo próprio Python, sem biblioteca de gráficos

## Estrutura do projeto

```
projeto-nps-empresas/
├── app.py                  # interface (Streamlit): upload, validação, prévia e download
├── gerar_relatorio.py      # mesma geração pela linha de comando
├── requirements.txt
├── nps/
│   ├── versao.py           # nome, versão e funcionalidades desta entrega
│   ├── leitura.py          # leitura do CSV, mapeamento de colunas, normalização e validação
│   ├── metricas.py         # cálculos compartilhados (NPS, percentuais, notas)
│   ├── comparativo.py      # base comparativa: leitura do período anterior e tabelas de variação
│   ├── relatorio.py        # motor: executa as seções ativas e monta o HTML
│   ├── componentes.py      # componentes HTML/SVG (cards, gráficos, tabelas, abas)
│   └── secoes/
│       ├── __init__.py     # lista das seções ativas nesta versão
│       ├── composicao_nps.py   # AC1 — composição do NPS + comparativo
│       ├── funil.py            # AC2 — funil de engajamento
├── assets/                 # CSS, JS e fonte embutidos no HTML gerado
├── data/
│   ├── exemplo_base_atual.csv          # planilha de exemplo (dados fictícios anonimizados)
│   └── base_comparativa_marco2026.csv  # indicadores do quadrimestre anterior
├── exemplos/relatorio_exemplo.html     # relatório gerado com os dados de exemplo
└── docs/
    ├── AC2.md               # objetivo, teste e roteiro do vídeo desta entrega
    ├── backlog.md          # funcionalidades para o board
    └── entrega_classroom.md
```

## Como executar

```bash
# 1. clonar e entrar na pasta
git clone <url-do-repositorio>
cd projeto-nps-empresas

# 2. (opcional) ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. instalar dependências
pip install -r requirements.txt

# 4a. abrir a interface
streamlit run app.py
```

Na interface: envie a planilha (ou marque "usar a planilha de exemplo"), escolha a base comparativa, clique em **Gerar relatório**, confira a validação e baixe o HTML.

```bash
# 4b. ou gerar direto pela linha de comando
python gerar_relatorio.py data/exemplo_base_atual.csv \
    --periodo "Agosto/2026" \
    --comparativa data/base_comparativa_marco2026.csv \
    --saida saida/relatorio_nps.html
```

O HTML gerado abre em qualquer navegador, sem servidor.

## Formato dos dados de entrada

**Planilha da pesquisa** — CSV com uma linha por contato. As colunas são reconhecidas pelo nome (sem depender da ordem):

| Coluna | Uso |
|---|---|
| `Respondeu` | `Sim` / `Não` — define os respondentes |
| `NPS` | nota 0 a 10 |
| `E-mail` | conferência de duplicidade e contatos sem e-mail |
| `Abriu?` | `Sim` / `Não` / `FUP` — alcance e origem da resposta |

Cada versão exige só as colunas das funcionalidades ativas; se faltar alguma, a interface informa qual.

**Base comparativa** — CSV `indicador,valor` com os indicadores consolidados do quadrimestre anterior (veja `data/base_comparativa_marco2026.csv`). Obrigatórios: `periodo`, `respostas`, `promotores`, `neutros`, `detratores`.

## Regras de negócio

- **NPS** — padrão Reichheld/Bain: 9–10 promotores, 7–8 neutros, 0–6 detratores; NPS = %promotores − %detratores.
- **Taxa de resposta** — denominador é a base contatada (todas as linhas da planilha).
- **Comparativo** — diferença de percentuais em pontos percentuais (pts); NPS e médias em valor absoluto. Para neutros, detratores e respostas negativas, queda aparece em verde.
- **Origem da resposta** — respondeu com `Abriu? = Sim` → e-mail marketing; sem registro de abertura ou `FUP` → follow-up do CSM (nunca "indeterminado").

## Privacidade

Todos os dados do repositório são fictícios e foram anonimizados para fins acadêmicos: nomes, e-mails, telefones, empresas, IDs e responsáveis foram substituídos, e menções a marcas nos textos abertos foram neutralizadas. Contagens, notas e respostas foram preservadas, então os indicadores não mudam.

## Documentação da entrega

- [`docs/AC2.md`](docs/AC2.md) — objetivo, como testar e roteiro do vídeo
- [`docs/backlog.md`](docs/backlog.md) — funcionalidades para o board
- [`docs/entrega_classroom.md`](docs/entrega_classroom.md) — checklist da entrega
