# -*- coding: utf-8 -*-
"""
Leitura, mapeamento de colunas e validação da planilha de pesquisa.

A planilha é a "base contatada vs. respostas": uma linha por contato da base
de envio, com as colunas de controle (Abriu?, Respondeu) e as respostas.

Regras herdadas do tratamento de dados original:
  * tudo é lido como texto (evita 10 virar 10.0 e IDs em notação científica);
  * nulos viram string vazia;
  * valores são normalizados antes de qualquer comparação
    (strip, "10.0" -> "10", quebras de linha CRLF -> LF).
"""
import io
import re
import unicodedata

import pandas as pd


def _sem_acento(t):
    t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', t).strip().lower()


# nome canônico -> (regra de busca no cabeçalho, descrição)
# 'igual:' compara o cabeçalho inteiro; 'contem:' procura o trecho.
COLUNAS = {
    'email':        ('igual:e-mail', 'E-mail'),
    'abriu':        ('contem:abriu', 'Abriu? (Sim / Não / FUP)'),
    'respondeu':    ('igual:respondeu', 'Respondeu (Sim / Não)'),
    'nps':          ('igual:nps', 'NPS (0 a 10)'),
}


def _normalizar_valor(v):
    v = str(v).strip()
    if re.fullmatch(r'\d+\.0', v):
        v = str(int(float(v)))
    return v.replace('\r\n', '\n').replace('\r', '\n')


def ler_csv(origem):
    """Lê o CSV de um caminho ou de bytes/arquivo enviado pela interface."""
    if hasattr(origem, 'read'):
        origem = origem.read()
    if isinstance(origem, (bytes, bytearray)):
        for cod in ('utf-8-sig', 'latin-1'):
            try:
                texto = origem.decode(cod)
                break
            except UnicodeDecodeError:
                continue
        return pd.read_csv(io.StringIO(texto), dtype=str, sep=None, engine='python').fillna('')
    return pd.read_csv(origem, dtype=str, sep=None, engine='python', encoding='utf-8-sig').fillna('')


def mapear_colunas(df):
    """Devolve {nome_canonico: nome_da_coluna_na_planilha} para o que foi encontrado.

    O dicionário COLUNAS descreve o layout completo da planilha; cada versão
    usa apenas as colunas exigidas pelas funcionalidades ativas.
    """
    cab = {c: _sem_acento(c) for c in df.columns}
    achadas = {}
    for canon, (regra, _) in COLUNAS.items():
        modo, trecho = regra.split(':', 1)
        for original, norm in cab.items():
            if original in achadas.values():
                continue
            if (modo == 'igual' and norm == trecho) or (modo == 'contem' and trecho in norm):
                achadas[canon] = original
                break
    return achadas


def carregar(origem, colunas_necessarias):
    """Lê, mapeia, normaliza e valida a planilha.

    Devolve (df_canonico, relatorio_validacao). O df devolvido tem apenas as
    colunas canônicas encontradas. Levanta ValueError se faltar coluna
    obrigatória para as funcionalidades ativas nesta versão.
    """
    bruto = ler_csv(origem)
    mapa = mapear_colunas(bruto)
    faltando = [c for c in colunas_necessarias if c not in mapa]
    if faltando:
        desc = ', '.join(COLUNAS[c][1] for c in faltando)
        raise ValueError(f'A planilha não tem colunas obrigatórias para esta versão: {desc}')

    usadas = {c: mapa[c] for c in mapa if c in colunas_necessarias or c == 'email'}
    df = pd.DataFrame({canon: bruto[orig].map(_normalizar_valor) for canon, orig in usadas.items()})
    for c in ('abriu', 'respondeu', 'contato'):
        if c in df:
            df[c] = df[c].str.strip()

    avisos = []
    if 'email' in df:
        emails = df['email'].str.lower()
        dup = emails[(emails != '') & emails.duplicated()]
        if len(dup):
            avisos.append(f'{len(dup)} e-mail(s) duplicado(s) na base: {", ".join(sorted(set(dup))[:5])}')
        sem = int((emails == '').sum())
        if sem:
            avisos.append(f'{sem} contato(s) sem e-mail (não recebem o disparo).')
    resp = df['respondeu'] == 'Sim'
    if 'nps' in df:
        invalidos = df[resp & ~df['nps'].str.fullmatch(r'(10|[0-9])')]
        if len(invalidos):
            avisos.append(f'{len(invalidos)} respondente(s) sem nota de NPS válida — ficam fora do cálculo de NPS.')
    valores_abriu = set(df['abriu']) - {'Sim', 'Não', 'FUP', ''} if 'abriu' in df else set()
    if valores_abriu:
        avisos.append(f'Valores inesperados em "Abriu?": {", ".join(sorted(valores_abriu))}')

    validacao = {
        'linhas': len(df),
        'respondentes': int(resp.sum()),
        'colunas_mapeadas': usadas,
        'colunas_ignoradas': [c for c in bruto.columns if c not in usadas.values()],
        'avisos': avisos,
    }
    return df, validacao
