# -*- coding: utf-8 -*-
"""
Satisfação — PMF, CSAT do atendimento e autorização para aprofundamento.

PMF: respostas "Nada desapontado" vindas de quem deu NPS 10 são realocadas
para "Muito desapontado". A pergunta é formulada na negativa e esses casos
indicam inversão de sentido pelo respondente.

CSAT: quatro atributos do atendimento do gerente de relacionamento, escala
1 a 5. "Satisfeitos" = avaliações com nota 4 ou 5.
"""
from .. import comparativo
from ..componentes import (AD_MALVA, AD_VERMELHO, PRINCIPAL, SECUNDARIO, barras, fonte, kpi,
                           n2, pct, pizza, subtitulo, tabela)
from ..metricas import notas, perc, respondentes

SECAO = 'nps'
ORDEM = 20
COLUNAS = ['nps', 'pmf', 'csat_empatia', 'csat_agilidade', 'csat_clareza', 'csat_conhecimento', 'contato']

PMF_OPCOES = ['Muito desapontado', 'Um pouco desapontado', 'Nada desapontado']
PMF_CHAVES = {'Muito desapontado': 'pmf_muito', 'Um pouco desapontado': 'pmf_pouco',
              'Nada desapontado': 'pmf_nada'}
ATRIBUTOS = [
    ('csat_empatia', 'Empatia e proatividade na solução de problemas'),
    ('csat_agilidade', 'Agilidade no atendimento às solicitações'),
    ('csat_clareza', 'Clareza e assertividade nas respostas'),
    ('csat_conhecimento', 'Conhecimento sobre produtos e serviços'),
]


def calcular(ctx):
    resp = respondentes(ctx['df'])
    pmf = {o: 0 for o in PMF_OPCOES}
    realocados = 0
    for nota, resposta in zip(resp['nps'], resp['pmf']):
        resposta = resposta.strip()
        if resposta == 'Nada desapontado' and nota == '10':
            resposta = 'Muito desapontado'
            realocados += 1
        if resposta in pmf:
            pmf[resposta] += 1
    total_pmf = sum(pmf.values())

    csat, todas = [], []
    for chave, rotulo in ATRIBUTOS:
        ns = notas(resp[chave], 1, 5)
        todas += ns
        csat.append({'chave': chave, 'rotulo': rotulo, 'media': sum(ns) / len(ns) if ns else 0,
                     'dist': {k: ns.count(k) for k in range(1, 6)}, 'n': len(ns)})
    medias = [a['media'] for a in csat if a['n']]

    contato = resp['contato'].value_counts().to_dict()
    return {
        'pmf': pmf, 'pmf_total': total_pmf, 'pmf_realocados': realocados,
        'pmf_muito_pct': perc(pmf['Muito desapontado'], total_pmf),
        'csat': csat,
        'csat_media': sum(medias) / len(medias) if medias else 0,
        'csat_total': len(todas),
        'csat_satisfeitos': sum(1 for n in todas if n >= 4),
        'csat_satisfeitos_pct': perc(sum(1 for n in todas if n >= 4), len(todas)),
        'csat_dist_total': {k: todas.count(k) for k in range(1, 6)},
        'contato_sim': contato.get('Sim', 0), 'contato_nao': contato.get('Não', 0),
    }


def kpis(ctx):
    m = ctx['m']['satisfacao']
    return [
        (50, kpi('💔', pct(m['pmf_muito_pct']), 'PMF',
                 'ficariam “muito desapontados” sem o serviço', cor='green')),
        (60, kpi('⭐', f'{n2(m["csat_media"])}/5', 'CSAT médio dos 4 atributos de atendimento', cor='green')),
    ]


def linhas_comparativo(ctx):
    m, ant = ctx['m']['satisfacao'], ctx['anterior']
    linhas = []
    tot_ant = sum(ant.get(k, 0) for k in PMF_CHAVES.values())
    if tot_ant:
        linhas.append((30, comparativo.linha_valor('PMF — “muito desapontados”',
                                                   ant['pmf_muito'] / tot_ant * 100, m['pmf_muito_pct'], 'pct')))
    if 'csat_consolidado' in ant:
        linhas.append((40, comparativo.linha_valor('CSAT médio', ant['csat_consolidado'], m['csat_media'], 'csat')))
    if 'csat_satisfeitos_pct' in ant:
        linhas.append((50, comparativo.linha_valor('CSAT — satisfeitos (notas 4 e 5)',
                                                   ant['csat_satisfeitos_pct'], m['csat_satisfeitos_pct'], 'pct')))
    return linhas


def render(ctx):
    m, ant = ctx['m']['satisfacao'], ctx['anterior']
    html = ''

    # ── PMF
    html += subtitulo('PMF — “Se não pudesse mais usar o serviço, como se sentiria?”')
    cores = [SECUNDARIO, AD_MALVA, AD_VERMELHO]
    html += pizza([{'rotulo': o, 'valor': m['pmf'][o], 'pct': perc(m['pmf'][o], m['pmf_total']), 'cor': cores[i]}
                   for i, o in enumerate(PMF_OPCOES)])
    tot_ant = sum(ant.get(k, 0) for k in PMF_CHAVES.values()) if ant else 0
    if tot_ant:
        linhas = [comparativo.linha_distribuicao(o, ant.get(PMF_CHAVES[o], 0), tot_ant, m['pmf'][o],
                                                 m['pmf_total'], inverso=(i > 0))
                  for i, o in enumerate(PMF_OPCOES)]
        html += comparativo.bloco(ctx, 'Resposta', linhas)

    # ── CSAT
    html += subtitulo('⭐ CSAT — atendimento do gerente de relacionamento (escala 1 a 5)')
    notas_vistas = [k for k in range(5, 0, -1) if m['csat_dist_total'][k]] or [5, 4]
    cab = ['Atributo avaliado', 'Média'] + [f'Nota {k}' for k in notas_vistas]
    linhas = [[a['rotulo'], f'<b>{n2(a["media"])}</b>'] + [str(a['dist'][k]) for k in notas_vistas]
              for a in m['csat']]
    total = ['CONSOLIDADO', n2(m['csat_media'])] + [str(m['csat_dist_total'][k]) for k in notas_vistas]
    html += tabela(cab, linhas, total=total, esconder=range(2, len(cab)), id_tabela='tab-csat')
    baixas = [k for k in (1, 2) if m['csat_dist_total'][k]]
    obs = ('Nenhuma nota 1 ou 2 em nenhum atributo.' if not baixas
           else f'{sum(m["csat_dist_total"][k] for k in baixas)} avaliação(ões) com nota 1 ou 2.')
    html += fonte(f'{m["csat_satisfeitos"]} das {m["csat_total"]} avaliações '
                  f'({pct(m["csat_satisfeitos_pct"])}) são notas 4 ou 5. {obs}')
    if ant and 'csat_consolidado' in ant:
        linhas = [comparativo.linha_valor(a['rotulo'], ant[a['chave']], a['media'], 'csat_curto')
                  for a in m['csat'] if a['chave'] in ant]
        total = comparativo.linha_valor('CONSOLIDADO', ant['csat_consolidado'], m['csat_media'], 'csat_curto')
        html += comparativo.bloco(ctx, 'Atributo', linhas, contador=f'{ant["periodo"]} · média 1 a 5', total=total)

    # ── Autorização de contato
    html += subtitulo('📞 Autorização para aprofundamento')
    tot = m['contato_sim'] + m['contato_nao']
    html += barras([
        {'rotulo': 'Sim, podem entrar em contato', 'valor': m['contato_sim'], 'pct': perc(m['contato_sim'], tot), 'cor': PRINCIPAL},
        {'rotulo': 'Não', 'valor': m['contato_nao'], 'pct': perc(m['contato_nao'], tot), 'cor': AD_VERMELHO},
    ])
    return html


def notas_metodo(ctx):
    m = ctx['m']['satisfacao']
    itens = []
    if m['pmf_realocados']:
        itens.append(f'<b>PMF:</b> {m["pmf_realocados"]} resposta(s) registrada(s) como “nada desapontado” '
                     f'foram realocadas para “muito desapontado”. Todas vinham com nota 10 de NPS, o que indica '
                     f'inversão de sentido da pergunta, formulada na negativa.')
    else:
        itens.append('<b>PMF:</b> regra de realocação (“nada desapontado” com NPS 10) aplicada; '
                     'nenhum caso nesta base.')
    itens.append('<b>CSAT:</b> média simples por atributo (escala 1 a 5); o consolidado é a média dos 4 atributos.')
    return itens
