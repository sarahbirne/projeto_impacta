# -*- coding: utf-8 -*-
"""
Funil de engajamento — base, alcance e respostas, e origem das respostas.

Regra de origem: quem respondeu e tem "Abriu? = Sim" veio do e-mail
marketing. Quem respondeu sem registro de abertura, ou com abertura
indeterminada ("FUP", "Não" ou vazio), conta como follow-up do CSM — nunca
como "indeterminado".
"""
from ..componentes import (PRINCIPAL, SECUNDARIO, barras, callout, funil, kpi,
                           kpi_grid, n0, pct, subtitulo)
from ..metricas import perc, respondentes

SECAO = 'funil'
ORDEM = 10
COLUNAS = ['abriu']


def calcular(ctx):
    df = ctx['df']
    resp = respondentes(df)
    alcancados = int(df['abriu'].isin(['Sim', 'FUP']).sum())
    email = int((resp['abriu'] == 'Sim').sum())
    fup = len(resp) - email
    return {
        'base': len(df), 'alcancados': alcancados, 'respostas': len(resp),
        'email': email, 'fup': fup,
        'taxa_alcance': perc(alcancados, len(df)),
        'conversao': perc(len(resp), alcancados),
        'taxa_resposta': perc(len(resp), len(df)),
        'pct_fup': perc(fup, len(resp)), 'pct_email': perc(email, len(resp)),
    }


def kpis(ctx):
    m = ctx['m']['funil']
    return [
        (20, kpi('👁️', n0(m['alcancados']), 'Alcançados pela pesquisa', f'{pct(m["taxa_alcance"])} da base')),
        (70, kpi('🤝', pct(m['pct_fup']), 'Respostas obtidas por follow-up do CSM',
                 f'{m["fup"]} do total', cor='green')),
    ]


def render(ctx):
    m = ctx['m']['funil']
    html = funil([
        {'valor': m['base'], 'titulo': 'Base total de contatos',
         'linhas': ['Contatos da planilha de envio · 100%']},
        {'valor': m['alcancados'], 'titulo': 'Alcançados pela pesquisa',
         'linhas': [f'{pct(m["taxa_alcance"])} da base — e-mail aberto ou follow-up']},
        {'valor': m['respostas'], 'titulo': 'Responderam',
         'linhas': [f'{pct(m["conversao"])} de quem foi alcançado',
                    f'{pct(m["taxa_resposta"])} da base']},
    ])
    html += subtitulo('Conversão da pesquisa')
    html += kpi_grid([
        kpi('👁️', pct(m['taxa_alcance']), f'Taxa de alcance\n{m["alcancados"]} de {m["base"]} contatos', cor='pink'),
        kpi('🔁', pct(m['conversao']), f'Conversão de quem foi alcançado\n{m["respostas"]} de {m["alcancados"]}', cor='green'),
        kpi('✍️', pct(m['taxa_resposta']), f'Taxa de resposta sobre a base\n{m["respostas"]} de {m["base"]}'),
    ], colunas=3)
    html += subtitulo('Origem das respostas')
    html += barras([
        {'rotulo': 'Follow-up do CSM', 'valor': m['fup'], 'pct': m['pct_fup'], 'cor': PRINCIPAL},
        {'rotulo': 'E-mail marketing', 'valor': m['email'], 'pct': m['pct_email'], 'cor': SECUNDARIO},
    ])
    if m['respostas']:
        f10 = round(m['pct_fup'] / 10)
        html += callout(f'De cada 10 respostas, cerca de {f10} vieram do follow-up dos CSMs '
                        f'e {10 - f10} do e-mail marketing.')
    return html


def notas_metodo(ctx):
    m = ctx['m']['funil']
    return [
        f'<b>Alcance:</b> {m["alcancados"]} contatos com "Abriu?" igual a "Sim" (abertura do e-mail) '
        f'ou "FUP" (follow-up do CSM). A planilha não registra visualizações da página da pesquisa.',
        '<b>Origem da resposta:</b> respondente com abertura registrada conta como e-mail marketing; '
        'sem registro de abertura, ou com abertura indeterminada, conta como follow-up do CSM.',
    ]
