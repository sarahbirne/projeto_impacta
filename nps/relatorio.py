# -*- coding: utf-8 -*-
"""
Motor do relatório: executa as seções ativas desta versão e monta o HTML.

Fluxo:
    planilha (CSV) -> leitura/validação -> cálculo por seção
                   -> síntese + comparativo -> documento HTML autocontido

Cada funcionalidade é um módulo em nps/secoes/ com a mesma interface:
    SECAO, ORDEM, COLUNAS
    calcular(ctx)            -> dict com as métricas da seção
    kpis(ctx)                -> [(ordem, html_do_card)]     (opcional)
    linhas_comparativo(ctx)  -> [(ordem, [células])]        (opcional)
    render(ctx)              -> html
    notas_metodo(ctx)        -> [str]                        (opcional)
"""
from . import comparativo
from .componentes import callout, documento, esc, kpi_grid, secao
from .leitura import carregar
from .secoes import MODULOS
from .versao import NOME_PROJETO, VERSAO, ENTREGA

# Seções do documento, na ordem em que aparecem. Só é exibida a seção que
# tiver pelo menos um módulo ativo nesta versão; a numeração é contínua.
SECOES = [
    ('funil', 'Funil de engajamento da pesquisa',
     'O funil fecha a conversão da pesquisa inteira: base total de contatos, contatos alcançados '
     'pelos dois métodos de alcance e respostas. Depois dele vem a divisão das respostas entre '
     'follow-up do CSM e e-mail marketing.'),
    ('nps', 'NPS & satisfação', None),
    ('quali', 'Feedback qualitativo',
     'Codificação temática das respostas abertas. Uma resposta pode receber mais de um tema, '
     'por isso o total de menções pode ser maior que o de respostas.'),
]


def colunas_necessarias():
    cols = {'respondeu'}
    for m in MODULOS:
        cols.update(m.COLUNAS)
    return sorted(cols)


def gerar(planilha, periodo_atual, base_comparativa=None):
    """Gera o relatório.

    planilha          — caminho ou bytes do CSV da pesquisa atual
    periodo_atual     — rótulo do período (ex.: 'Agosto/2026')
    base_comparativa  — caminho ou bytes do CSV do período anterior (opcional)

    Devolve (html, ctx). ctx traz métricas e validação para a interface.
    """
    df, validacao = carregar(planilha, colunas_necessarias())
    ctx = {
        'df': df,
        'validacao': validacao,
        'periodo_atual': periodo_atual,
        'anterior': comparativo.carregar_base_comparativa(base_comparativa) if base_comparativa else None,
        'm': {},
    }
    for mod in MODULOS:
        ctx['m'][mod.__name__.split('.')[-1]] = mod.calcular(ctx)

    corpo, indice = _sintese(ctx), [('sintese', '1 · Síntese executiva')]
    numero = 1
    for chave, titulo, nota in SECOES:
        mods = sorted((m for m in MODULOS if m.SECAO == chave), key=lambda m: m.ORDEM)
        if not mods:
            continue
        numero += 1
        corpo += secao(numero, titulo, chave, nota=nota)
        corpo += ''.join(m.render(ctx) for m in mods)
        indice.append((chave, f'{numero} · {titulo}'))
    corpo += _notas(ctx)

    html = documento(
        'Resultados · Pesquisa de Satisfação (NPS)', corpo,
        subtitulo=periodo_atual, indice=indice,
        titulo_aba=f'{NOME_PROJETO} — {periodo_atual}',
        assinatura=f'{NOME_PROJETO} · versão {VERSAO} ({ENTREGA})')
    return html, ctx


def _sintese(ctx):
    cards = sorted((c for m in MODULOS if hasattr(m, 'kpis') for c in m.kpis(ctx)), key=lambda c: c[0])
    html = secao(1, 'Síntese executiva', 'sintese')
    # distribui os cards em até duas linhas equilibradas (7 cards = 4 + 3, como no layout original)
    cards = [c[1] for c in cards]
    corte = {5: 3, 6: 3}.get(len(cards), 4)
    html += kpi_grid(cards[:corte])
    if cards[corte:]:
        html += kpi_grid(cards[corte:], colunas=len(cards[corte:]) if len(cards[corte:]) <= 3 else None)
    if ctx['anterior']:
        linhas = sorted((l for m in MODULOS if hasattr(m, 'linhas_comparativo')
                         for l in m.linhas_comparativo(ctx)), key=lambda l: l[0])
        if linhas:
            html += comparativo.bloco(ctx, 'Indicador', [l[1] for l in linhas])
    return html


def _notas(ctx):
    itens = []
    for m in MODULOS:
        if hasattr(m, 'notas_metodo'):
            itens += m.notas_metodo(ctx)
    if ctx['anterior']:
        itens.append(f'<b>Base comparativa:</b> indicadores consolidados de {esc(ctx["anterior"]["periodo"])}, '
                     f'lidos do CSV de indicadores. Variações de percentual são expressas em pontos '
                     f'percentuais (pts); médias e NPS, em valor absoluto.')
    for aviso in ctx['validacao']['avisos']:
        itens.append(f'<b>Qualidade de dado:</b> {esc(aviso)}')
    if not itens:
        return ''
    return callout('<ul>\n' + '\n'.join(f'<li>{i}</li>' for i in itens) + '\n</ul>',
                   titulo='🧾 Notas de método e qualidade de dado')
