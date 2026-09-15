# -*- coding: utf-8 -*-
"""
Composição do NPS — promotores, neutros e detratores.

Metodologia padrão (Reichheld/Bain): notas 9–10 promotores, 7–8 neutros,
0–6 detratores; NPS = %promotores − %detratores.
"""
from .. import comparativo
from ..componentes import (AD_MALVA, AD_VERMELHO, PRINCIPAL, donut, kpi, n0, pct,
                           subtitulo)
from ..metricas import calcular_nps, notas, perc, respondentes

SECAO = 'nps'
ORDEM = 10
COLUNAS = ['nps']


def calcular(ctx):
    df = ctx['df']
    resp = respondentes(df)
    ns = notas(resp['nps'], 0, 10)
    prom = sum(1 for n in ns if n >= 9)
    neut = sum(1 for n in ns if 7 <= n <= 8)
    detr = sum(1 for n in ns if n <= 6)
    return {
        'base': len(df),
        'respostas': len(resp),
        'com_nota': len(ns),
        'promotores': prom, 'neutros': neut, 'detratores': detr,
        'por_nota': {k: ns.count(k) for k in range(11)},
        'nps': calcular_nps(prom, neut, detr),
        'taxa_resposta': perc(len(resp), len(df)),
    }


def kpis(ctx):
    m = ctx['m']['composicao_nps']
    return [
        (10, kpi('📇', n0(m['base']), 'Contatos na base', cor='pink')),
        (30, kpi('✍️', n0(m['respostas']), 'Respostas válidas',
                 f'{pct(m["taxa_resposta"])} da base', cor='green')),
        (40, kpi('🏆', f'{round(m["nps"]):.0f}', 'NPS',
                 f'{m["promotores"]} promotores e {m["detratores"]} detratores', cor='green')),
    ]


def linhas_comparativo(ctx):
    m, ant = ctx['m']['composicao_nps'], ctx['anterior']
    nps_ant = calcular_nps(ant['promotores'], ant['neutros'], ant['detratores'])
    return [
        (10, comparativo.linha_valor('Respostas', ant['respostas'], m['respostas'])),
        (20, comparativo.linha_valor('NPS', nps_ant, m['nps'])),
    ]


def _detalhe(por_nota, faixa):
    partes = [f'{por_nota[n]} {"nota" if por_nota[n] == 1 else "notas"} {n}'
              for n in faixa if por_nota[n]]
    return ' + '.join(partes) if len(partes) > 1 else ''


def render(ctx):
    m = ctx['m']['composicao_nps']
    tot = m['com_nota']
    html = subtitulo('Composição do NPS')
    html += donut([
        {'rotulo': 'Promotores · notas 9–10', 'valor': m['promotores'], 'pct': perc(m['promotores'], tot),
         'cor': PRINCIPAL, 'detalhe': _detalhe(m['por_nota'], [10, 9])},
        {'rotulo': 'Neutros · notas 7–8', 'valor': m['neutros'], 'pct': perc(m['neutros'], tot),
         'cor': AD_MALVA, 'detalhe': _detalhe(m['por_nota'], [8, 7])},
        {'rotulo': 'Detratores · notas 0–6', 'valor': m['detratores'], 'pct': perc(m['detratores'], tot),
         'cor': AD_VERMELHO, 'detalhe': _detalhe(m['por_nota'], range(6, -1, -1))},
    ], rotulo_centro='NPS', valor_centro=f'{round(m["nps"]):.0f}')

    ant = ctx['anterior']
    if ant:
        ta = ant['promotores'] + ant['neutros'] + ant['detratores']
        linhas = [
            comparativo.linha_distribuicao('Promotores (9–10)', ant['promotores'], ta, m['promotores'], tot),
            comparativo.linha_distribuicao('Neutros (7–8)', ant['neutros'], ta, m['neutros'], tot, inverso=True),
            comparativo.linha_distribuicao('Detratores (0–6)', ant['detratores'], ta, m['detratores'], tot, inverso=True),
        ]
        nps_ant = calcular_nps(ant['promotores'], ant['neutros'], ant['detratores'])
        total = comparativo.linha_valor('NPS', nps_ant, m['nps'])
        html += comparativo.bloco(ctx, 'Grupo', linhas, total=total)
    return html


def notas_metodo(ctx):
    m = ctx['m']['composicao_nps']
    return [
        f'<b>Base:</b> {m["base"]} contatos na planilha enviada; {m["respostas"]} com "Respondeu = Sim". '
        f'A taxa de resposta usa a base contatada como denominador.',
        '<b>NPS:</b> metodologia padrão — promotores 9–10, neutros 7–8, detratores 0–6; '
        'NPS = %promotores − %detratores.',
    ]
