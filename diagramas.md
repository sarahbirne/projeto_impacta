# Diagramas do projeto

Modelagem do sistema entregue na versão 4.0. Os três diagramas estão em
`docs/diagramas/`, em PNG (para visualizar e colar na apresentação) e em SVG
(vetorial, sem perder qualidade ao ampliar).

---

## 1. Diagrama de caso de uso

![Diagrama de caso de uso](diagramas/diagrama_caso_de_uso.png)

Mostra o que cada perfil faz com o sistema.

**Atores**

- **Analista de CX** — quem roda o sistema: envia a planilha da pesquisa, escolhe a base
  comparativa, gera o relatório, visualiza a prévia e baixa o HTML.
- **Gestor de CX** — quem consome o resultado: abre o relatório HTML já gerado.

**Relacionamentos**

- `«include»` — sempre executado como parte do caso base. *Gerar relatório* sempre
  valida a planilha e sempre calcula os indicadores.
- `«extend»` — executado só em certas condições. *Comparar com quadrimestre anterior*
  só acontece quando a base comparativa é informada; *codificar respostas abertas em
  temas* só quando existem respostas abertas preenchidas.

---

## 2. Diagrama de classes

![Diagrama de classes](diagramas/diagrama_de_classes.png)

Mostra a arquitetura do código, que está em `nps/`.

| Classe | Arquivo | Papel |
|---|---|---|
| `PlanilhaPesquisa` | `nps/leitura.py` | Lê o CSV, reconhece as colunas pelo nome, normaliza os valores e valida |
| `Validacao` | `nps/leitura.py` | Resultado da validação: linhas, respondentes, colunas reconhecidas e avisos |
| `Relatorio` | `nps/relatorio.py` | Motor: executa as seções ativas, monta a síntese e gera o HTML |
| `BaseComparativa` | `nps/comparativo.py` | Lê os indicadores do quadrimestre anterior e monta as tabelas de variação |
| `Secao` *(interface)* | `nps/secoes/` | Contrato que toda funcionalidade implementa |
| `ComposicaoNPS` | `nps/secoes/composicao_nps.py` | AC1 — promotores, neutros, detratores e NPS |
| `Funil` | `nps/secoes/funil.py` | AC2 — alcance, conversão e origem das respostas |
| `Satisfacao` | `nps/secoes/satisfacao.py` | AC3 — PMF, CSAT e autorização de contato |
| `Qualitativo` | `nps/secoes/qualitativo.py` | Entrega final — respostas abertas por tema |
| `CodificadorTemas` | `nps/temas.py` | Codificação temática por palavras-chave |
| `Componentes` | `nps/componentes.py` | Biblioteca de componentes HTML e SVG do relatório |

O ponto central do desenho é a interface **`Secao`**: as quatro funcionalidades
implementam os mesmos cinco métodos (`calcular`, `kpis`, `linhas_comparativo`,
`render`, `notas_metodo`). Por isso cada entrega acrescentou uma classe nova e a
registrou em `nps/secoes/__init__.py`, sem reescrever o que já existia.

---

## 3. MER — modelo entidade-relacionamento

![MER](diagramas/mer.png)

Mostra o modelo de dados por trás da pesquisa, que na prática chega ao sistema como
planilha.

| Entidade | Conteúdo |
|---|---|
| `EMPRESA` | Empresa cliente |
| `GERENTE_RELACIONAMENTO` | CSM dono da carteira |
| `CONTATO` | Pessoa da base de envio |
| `PERIODO` | Quadrimestre da pesquisa |
| `ENVIO_PESQUISA` | Disparo para um contato: abriu, respondeu |
| `RESPOSTA` | NPS, PMF, autorização e os textos abertos |
| `ATRIBUTO_CSAT` | Os quatro atributos avaliados do atendimento |
| `AVALIACAO_CSAT` | Nota de 1 a 5 de um atributo em uma resposta |
| `TEMA` | Tema da codificação das respostas abertas |
| `RESPOSTA_TEMA` | Tema atribuído a uma resposta |
| `INDICADOR_CONSOLIDADO` | Indicadores já fechados de um período (base comparativa) |

**Correspondência com os arquivos de entrada**

- `data/exemplo_base_atual.csv` é a junção de `CONTATO` + `ENVIO_PESQUISA` + `RESPOSTA`
  (uma linha por contato, no formato em que a pesquisa é exportada do CRM).
- `data/base_comparativa_marco2026.csv` corresponde a `PERIODO` + `INDICADOR_CONSOLIDADO`.

`AVALIACAO_CSAT` e `RESPOSTA_TEMA` são tabelas associativas (N:N): uma resposta tem
quatro notas de CSAT, e uma resposta aberta pode receber mais de um tema.
