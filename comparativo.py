# -*- coding: utf-8 -*-
"""
Base comparativa — confronta o período atual com o período anterior.

A base do período anterior vem consolidada (indicadores agregados), num CSV
de duas colunas principais: `indicador` e `valor`. Veja
data/base_comparativa_marco2026.csv.

Cada seção do relatório pede ao módulo as linhas do seu comparativo; o
resultado é exibido em blocos expansíveis com a diferença em pontos
percentuais (p.p.) ou em valor absoluto.
"""
from .componentes import bloco_comparativo, n2, pct, tabela, variacao
from .leitura import ler_csv

OBRIGATORIOS = ['periodo', 'respostas', 'promotores', 'neutros', 'detratores']


def carregar_base_comparativa(origem):
    """Lê o CSV de indicadores do período anterior e devolve um dict tipado."""
    df = ler_csv(origem)
    colunas = {c.strip().lower(): c for c in df.columns}
    if 'indicador' not in colunas or 'valor' not in colunas:
        raise ValueError('A base comparativa precisa das colunas "indicador" e "valor".')
    dados = {}
    for _, linha in df.iterrows():
        chave = str(linha[colunas['indicador']]).strip().lower()
        valor = str(linha[colunas['valor']]).strip()
        if not chave:
            continue
        if chave == 'periodo':
            dados[chave] = valor
            continue
        try:
            num = float(valor.replace(',', '.'))
        except ValueError:
            raise ValueError(f'Valor não numérico para o indicador "{chave}": {valor}')
        dados[chave] = int(num) if num.is_integer() and not chave.startswith('csat') else num
    faltando = [k for k in OBRIGATORIOS if k not in dados]
    if faltando:
        raise ValueError(f'Indicadores obrigatórios ausentes na base comparativa: {", ".join(faltando)}')
    return dados


def contagem(n, total):
    """'56 (84,8%)'"""
    return f'{n} ({pct(n / total * 100 if total else 0)})'


def linha_distribuicao(rotulo, n_ant, tot_ant, n_at, tot_at, inverso=False):
    """Linha com contagem e percentual nos dois períodos e variação em p.p."""
    p_ant = n_ant / tot_ant * 100 if tot_ant else 0
    p_at = n_at / tot_at * 100 if tot_at else 0
    return [rotulo, contagem(n_ant, tot_ant), contagem(n_at, tot_at),
            variacao(p_at - p_ant, ' pts', inverso=inverso)]


def linha_valor(rotulo, ant, atual, fmt='int', inverso=False):
    """Linha de indicador simples. fmt: 'int', 'pct' (variação em p.p.) ou 'csat'."""
    if fmt == 'pct':
        return [rotulo, pct(ant), pct(atual), variacao(atual - ant, ' pts', inverso=inverso)]
    if fmt == 'csat':
        return [rotulo, f'{n2(ant)}/5', f'{n2(atual)}/5', variacao(atual - ant, casas=2, inverso=inverso)]
    if fmt == 'csat_curto':
        return [rotulo, n2(ant), n2(atual), variacao(atual - ant, casas=2, inverso=inverso)]
    return [rotulo, f'{round(ant):.0f}', f'{round(atual):.0f}',
            variacao(round(atual) - round(ant), casas=0, inverso=inverso)]


def bloco(ctx, cabecalho_1, linhas, contador=None, total=None):
    """Bloco expansível 'Comparativo' com a tabela período anterior x atual."""
    ant = ctx['anterior']
    cab = [cabecalho_1, ant['periodo'], ctx['periodo_atual'], 'Variação']
    cont = contador or f'{ant["periodo"]} · {ant["respostas"]} respostas'
    return bloco_comparativo('Comparativo', cont, tabela(cab, linhas, total=total))
