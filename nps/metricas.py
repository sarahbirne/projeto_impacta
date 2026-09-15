# -*- coding: utf-8 -*-
"""Funções de cálculo compartilhadas entre as seções."""


def respondentes(df):
    """Linhas com Respondeu = Sim."""
    return df[df['respondeu'] == 'Sim']


def notas(serie, minimo, maximo):
    """Converte uma série de texto em inteiros válidos dentro da escala."""
    out = []
    for v in serie:
        v = str(v).strip()
        if v.isdigit() and minimo <= int(v) <= maximo:
            out.append(int(v))
    return out


def perc(parte, total):
    return (parte / total * 100) if total else 0.0


def calcular_nps(promotores, neutros, detratores):
    """Metodologia padrão: NPS = %promotores − %detratores."""
    total = promotores + neutros + detratores
    return perc(promotores, total) - perc(detratores, total) if total else 0.0

