# -*- coding: utf-8 -*-
"""
Feedback qualitativo — respostas abertas codificadas por tema.

Três abas:
  1. Principal benefício   — nuvem de temas + respostas na íntegra
  2. Como podemos melhorar — nuvem de temas + respostas na íntegra
  3. Atendimento do CSM    — classificação das respostas + respostas por gerente
"""
from collections import Counter

from ..componentes import (AD_MALVA, PRINCIPAL, SECUNDARIO, abas, abas_laterais, badge, barras,
                           bloco_expansivel, esc, fonte, item_expansivel, nuvem, pct, pergunta,
                           subtitulo)
from ..metricas import perc, respondentes, texto_preenchido
from ..temas import TEMAS_BENEFICIO, TEMAS_MELHORAR, classificar_atendimento, codificar

SECAO = 'quali'
ORDEM = 10
COLUNAS = ['nome', 'sobrenome', 'email', 'empresa', 'gerente', 'beneficio', 'melhorar', 'atendimento']

SEM_CARTEIRA = 'Sem carteira'


def _quem(linha):
    nome = f'{linha["nome"]} {linha["sobrenome"]}'.strip()
    return nome or linha['email'] or 'Respondente sem nome'


def _gerente(linha):
    g = linha['gerente'].strip()
    return g if g and g != '-' else SEM_CARTEIRA


def _onde(linha):
    g = _gerente(linha)
    partes = [p for p in (linha['empresa'].strip(), 'sem carteira' if g == SEM_CARTEIRA else f'carteira {g}') if p]
    return ' · '.join(partes)


def calcular(ctx):
    resp = respondentes(ctx['df'])
    out = {'respondentes': len(resp)}
    for campo, temas in (('beneficio', TEMAS_BENEFICIO), ('melhorar', TEMAS_MELHORAR)):
        itens = []
        for _, l in resp.iterrows():
            if texto_preenchido(l[campo]):
                itens.append({'quem': _quem(l), 'onde': _onde(l), 'texto': l[campo],
                              'temas': codificar(l[campo], temas)})
        out[campo] = {'itens': itens, 'temas': Counter(t for i in itens for t in i['temas'])}

    atend = []
    for _, l in resp.iterrows():
        if texto_preenchido(l['atendimento']):
            rotulo, tipo = classificar_atendimento(l['atendimento'])
            atend.append({'quem': _quem(l), 'empresa': l['empresa'], 'gerente': _gerente(l),
                          'texto': l['atendimento'], 'classe': rotulo, 'tipo': tipo})
    out['atendimento'] = {'itens': atend, 'classes': Counter(i['classe'] for i in atend)}
    out['sem_carteira'] = sum(1 for _, l in resp.iterrows() if _gerente(l) == SEM_CARTEIRA)
    return out


def _painel_tema(m, campo, enunciado, id_lista):
    bloco = m[campo]
    n, tot = len(bloco['itens']), m['respondentes']
    mencoes = sum(bloco['temas'].values())
    html = pergunta(enunciado)
    html += fonte(f'{n} respostas de {tot} respondentes ({pct(perc(n, tot))}). {mencoes} menções temáticas.')
    html += subtitulo('Temas identificados')
    html += nuvem(sorted(bloco['temas'].items(), key=lambda t: -t[1]))
    itens = [item_expansivel(i['quem'], esc(i['texto']).replace('\n', '<br>'), subtitulo=i['onde'], tags=i['temas'])
             for i in bloco['itens']]
    html += bloco_expansivel('Respostas na íntegra', itens, contador=f'{n} respostas', id_lista=id_lista)
    return html


def _painel_atendimento(m):
    bloco = m['atendimento']
    n, tot = len(bloco['itens']), m['respondentes']
    html = pergunta('Existe algo que podemos melhorar no atendimento oferecido pelo(a) gerente de relacionamento?')
    html += fonte(f'{n} respostas de {tot} respondentes ({pct(perc(n, tot))}).')
    cores = {'Elogio explícito ao CSM': PRINCIPAL, 'Sem apontamento': AD_MALVA, 'Com ressalva ou sugestão': SECUNDARIO}
    html += barras([{'rotulo': c, 'valor': bloco['classes'].get(c, 0), 'pct': perc(bloco['classes'].get(c, 0), n),
                     'cor': cores[c]} for c in cores])
    html += subtitulo('Respostas por CSM')
    por_gerente = {}
    for i in bloco['itens']:
        por_gerente.setdefault(i['gerente'], []).append(i)
    rotulo_badge = {'green': 'positiva', 'grey': 'sem apontamento', 'amber': 'com ressalva'}
    grupos = []
    ordem = sorted(por_gerente, key=lambda g: (g == SEM_CARTEIRA, -len(por_gerente[g]), g))
    for k, g in enumerate(ordem, 1):
        itens = ''.join(item_expansivel(i['quem'], esc(i['texto']).replace('\n', '<br>'), subtitulo=i['empresa'],
                                        badges=[badge(rotulo_badge[i['tipo']], i['tipo'], mini=True)])
                        for i in por_gerente[g])
        grupos.append({'id': f'm{k}', 'rotulo': g, 'contagem': len(por_gerente[g]),
                       'conteudo': f'<div class="cmt-list">{itens}</div>'})
    if grupos:
        html += abas_laterais(grupos)
    return html


def render(ctx):
    m = ctx['m']['qualitativo']
    return abas([
        {'id': 't1', 'rotulo': 'Principal benefício', 'contagem': len(m['beneficio']['itens']),
         'conteudo': _painel_tema(m, 'beneficio',
                                  'Qual é o principal benefício que você e sua empresa obtém ao usar os nossos serviços?',
                                  'lst-ben')},
        {'id': 't2', 'rotulo': 'Como podemos melhorar', 'contagem': len(m['melhorar']['itens']),
         'conteudo': _painel_tema(m, 'melhorar', 'Como podemos melhorar nossos serviços para você e sua empresa?',
                                  'lst-mel')},
        {'id': 't3', 'rotulo': 'Atendimento do CSM', 'contagem': len(m['atendimento']['itens']),
         'conteudo': _painel_atendimento(m)},
    ])


def notas_metodo(ctx):
    m = ctx['m']['qualitativo']
    itens = ['<b>Codificação temática:</b> feita por palavras-chave (nps/temas.py). Uma resposta pode receber '
             'mais de um tema; respostas sem correspondência caem em “Outros”.',
             '<b>Atribuição de CSM:</b> pelo proprietário do contato na planilha.']
    if m['sem_carteira']:
        itens[-1] += f' {m["sem_carteira"]} resposta(s) permaneceram sem vínculo de carteira.'
    return itens
