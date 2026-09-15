# -*- coding: utf-8 -*-
"""
Gera o relatório HTML pela linha de comando (sem interface).

Exemplo:
    python gerar_relatorio.py data/exemplo_base_atual.csv \
        --periodo "Agosto/2026" \
        --comparativa data/base_comparativa_marco2026.csv \
        --saida saida/relatorio_nps.html
"""
import argparse
import sys

from nps.componentes import salvar
from nps.relatorio import gerar
from nps.versao import ENTREGA, NOME_PROJETO, VERSAO


def main():
    ap = argparse.ArgumentParser(description=f'{NOME_PROJETO} — gerador do relatório (v{VERSAO})')
    ap.add_argument('planilha', help='CSV da pesquisa atual (base contatada vs. respostas)')
    ap.add_argument('--periodo', default='Agosto/2026', help='Rótulo do período atual')
    ap.add_argument('--comparativa', help='CSV de indicadores do período anterior (opcional)')
    ap.add_argument('--saida', default='saida/relatorio_nps.html', help='Caminho do HTML gerado')
    args = ap.parse_args()

    try:
        html, ctx = gerar(args.planilha, args.periodo, args.comparativa)
    except ValueError as erro:
        print(f'ERRO: {erro}', file=sys.stderr)
        sys.exit(1)

    salvar(args.saida, html)
    v = ctx['validacao']
    print(f'{NOME_PROJETO} · v{VERSAO} ({ENTREGA})')
    print(f'Linhas lidas: {v["linhas"]} · respondentes: {v["respondentes"]}')
    for aviso in v['avisos']:
        print(f'  aviso: {aviso}')
    print(f'Relatório salvo em: {args.saida}')


if __name__ == '__main__':
    main()
