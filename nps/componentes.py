# -*- coding: utf-8 -*-
"""
componentes — biblioteca de componentes HTML do relatório de NPS.

Cada função devolve uma string de HTML. O documento final é autocontido:
CSS, JavaScript e gráficos (SVG) ficam embutidos, então o arquivo abre
offline e pode ser compartilhado como anexo.
"""
import html as _html
import math
import os

RAIZ_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

# ══════════════════════════════════════════════════════════════════════
# Paleta
# ══════════════════════════════════════════════════════════════════════
PRINCIPAL   = '#be0380'   # magenta — cor principal
SECUNDARIO  = '#690046'   # magenta profundo
DESTAQUE    = '#40002d'   # ameixa — texto e blocos escuros
NEUTRO      = '#fafafa'
AD_CINZA    = '#f3f2f0'
AD_CAQUI    = '#ddddd5'
AD_AZUL     = '#dee2ed'
AD_MALVA    = '#e2d7e0'
AD_VERMELHO = '#ffb2b2'
AD_VERDE    = '#d9f1d8'

# Rampa padrão para séries de dados: escuro → marca → tons de apoio.
# Use nesta ordem para que a série mais relevante fique na cor da marca.
RAMPA = [DESTAQUE, SECUNDARIO, PRINCIPAL, AD_MALVA, AD_AZUL, AD_CAQUI, AD_VERDE, AD_VERMELHO]

TEXTO_SUAVE = '#6b5563'   # cinza puxado para ameixa, para rótulos
TEXTO_FRACO = '#8d7b86'


def texto_sobre(cor):
    """Cor de texto legível sobre `cor`: ameixa em fundo claro, branco em escuro.

    Sempre use isto ao escrever texto dentro de uma forma colorida. Metade do
    kit são tons pálidos, e texto branco sobre eles fica ilegível.
    """
    r, g, b = (int(cor.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return DESTAQUE if (0.2126 * r + 0.7152 * g + 0.0722 * b) > 0.62 else '#fff'


# ══════════════════════════════════════════════════════════════════════
# Formatação pt-BR
# ══════════════════════════════════════════════════════════════════════
def n1(v):
    return f'{v:.1f}'.replace('.', ',')


def n2(v):
    return f'{v:.2f}'.replace('.', ',')


def n0(v):
    return f'{v:,.0f}'.replace(',', '.')


def pct(v, casas=1):
    return f'{v:.{casas}f}'.replace('.', ',') + '%'


def esc(t):
    return _html.escape(str(t))


def _txt(t):
    """Escapa e converte quebras de linha em <br>."""
    return esc(t).replace('\n', '<br>')


# ══════════════════════════════════════════════════════════════════════
# Estrutura da página
# ══════════════════════════════════════════════════════════════════════
def _asset(nome):
    with open(os.path.join(RAIZ_ASSETS, nome), encoding='utf-8') as f:
        return f.read()


def documento(titulo, corpo, subtitulo=None, indice=None, assinatura=None,
              titulo_aba=None, largura=1080):
    """Monta o HTML completo.

    titulo      — vai no bloco colorido do topo
    corpo       — HTML das seções, já concatenado
    subtitulo   — linha sob o título (ex.: 'Agosto/2026')
    indice      — lista de (ancora, rótulo) para as pílulas de navegação
    assinatura  — texto discreto no rodapé (ex.: nome e versão do projeto)
    """
    sub = f'\n    <p class="subtitle">{esc(subtitulo)}</p>' if subtitulo else ''
    toc = ''
    if indice:
        pil = '\n'.join(f'    <a href="#{a}">{esc(r)}</a>' for a, r in indice)
        toc = f'\n  <div class="toc">\n{pil}\n  </div>'
    marca = (f'\n<div class="marca"><p class="assinatura">{esc(assinatura)}</p></div>'
             if assinatura else '')
    estilo_largura = '' if largura == 1080 else f'\n.page{{max-width:{largura}px}}'
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(titulo_aba or titulo)}</title>
{_asset('fonte.html').strip()}
<style>
{_asset('1-base.css')}
{_asset('2-anim.css')}
{_asset('3-tema.css')}{estilo_largura}
</style>
</head>
<body>
<div class="page">

  <header class="doc-header">
    <h1>{esc(titulo)}</h1>{sub}
  </header>{toc}
{corpo}{marca}
</div>
<script>
{_asset('interacoes.js')}
</script>
<script>
{_asset('anim.js')}
</script>
</body>
</html>'''


def salvar(caminho, html):
    os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html)
    return caminho


def secao(numero, titulo, ancora, nota=None):
    """Título de seção numerado. `nota` é a linha explicativa abaixo."""
    n = f'\n<p class="section-note">{_txt(nota)}</p>' if nota else ''
    return (f'\n<h2 class="section-title" id="{ancora}">'
            f'<span class="num">{numero}</span>{esc(titulo)}</h2>{n}\n')


def subtitulo(texto):
    return f'\n<h3 class="sub-title">{_txt(texto)}</h3>\n'


def callout(texto, titulo=None):
    """Bloco rosa pálido de destaque. Aceita HTML no texto (use <b>, <ul>)."""
    t = f'<span class="callout-title">{_txt(titulo)}</span>\n' if titulo else ''
    return f'\n<div class="callout">\n{t}{texto}\n</div>\n'


# ══════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════
def kpi(icone, valor, rotulo, nota=None, cor=None):
    """Um card de indicador. `nota` é a linha de detalhe abaixo do número.
    `cor` opcional: 'pink' ou 'green' (acento do card)."""
    n = f'<div class="kpi-note">{_txt(nota)}</div>' if nota else ''
    c = f' {cor}' if cor else ''
    return (f'<div class="kpi-card{c}"><div class="kpi-icon">{icone}</div>'
            f'<div class="kpi-value">{valor}</div>'
            f'<div class="kpi-label">{_txt(rotulo)}</div>{n}</div>')


def kpi_grid(cards, colunas=None):
    """Grade de cards. colunas=2, 3 ou 4 (padrão: deduz do número de cards).

    Os números alinham na mesma altura porque o CSS reserva a faixa do rótulo
    e a do detalhe — não mexa nessas alturas sem rodar checar_css.py depois.
    """
    if colunas is None:
        colunas = 3 if len(cards) % 3 == 0 and len(cards) != 4 else min(len(cards), 4)
    cls = {2: 'kpi-grid g2', 3: 'kpi-grid g3'}.get(colunas, 'kpi-grid')
    return f'\n<div class="{cls}">\n' + '\n'.join(cards) + '\n</div>\n'


# ══════════════════════════════════════════════════════════════════════
# Donut e pizza
# ══════════════════════════════════════════════════════════════════════
def _ponto(cx, cy, r, ang):
    a = math.radians(ang - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def donut(fatias, rotulo_centro='', valor_centro=''):
    """Rosca com texto no centro.

    fatias — lista de dicts: {'rotulo', 'valor', 'pct', 'cor'?, 'detalhe'?}
             'detalhe' aparece em cinza ao lado da legenda.
    """
    cx = cy = 116
    R, ri = 104, 60
    partes, ang = [], 0.0
    for i, f in enumerate(fatias):
        p = f['pct']
        if p <= 0:
            continue
        cor = f.get('cor') or RAMPA[i % len(RAMPA)]
        a2 = ang + p * 3.6
        x1, y1 = _ponto(cx, cy, R, ang)
        x2, y2 = _ponto(cx, cy, R, a2)
        x3, y3 = _ponto(cx, cy, ri, a2)
        x4, y4 = _ponto(cx, cy, ri, ang)
        la = 1 if p > 50 else 0
        partes.append(f'<path d="M {x1:.2f} {y1:.2f} A {R} {R} 0 {la} 1 {x2:.2f} {y2:.2f} '
                      f'L {x3:.2f} {y3:.2f} A {ri} {ri} 0 {la} 0 {x4:.2f} {y4:.2f} Z" '
                      f'fill="{cor}" stroke="#fff" stroke-width="2"/>')
        ang = a2
    if rotulo_centro:
        partes.append(f'<text x="116" y="107" text-anchor="middle" dominant-baseline="central" '
                      f'font-size="11" fill="{TEXTO_FRACO}" letter-spacing=".08em">{esc(rotulo_centro)}</text>')
    if valor_centro:
        partes.append(f'<text x="116" y="130" text-anchor="middle" dominant-baseline="central" '
                      f'font-size="26" fill="{DESTAQUE}" font-weight="500">{esc(valor_centro)}</text>')
    return _pie_wrap(partes, fatias, 'Composição')


def _pie_wrap(partes, fatias, rotulo_svg):
    itens = []
    for i, f in enumerate(fatias):
        cor = f.get('cor') or RAMPA[i % len(RAMPA)]
        det = (f'<span style="color:{TEXTO_FRACO};font-weight:400">{esc(f["detalhe"])}</span>'
               if f.get('detalhe') else '')
        itens.append(f'<li><span class="dot" style="background:{cor}"></span>'
                     f'<span class="pl">{esc(f["rotulo"])}</span>'
                     f'<span class="pv">{f["valor"]} <span class="pp">({pct(f["pct"])})</span></span> {det}</li>')
    return (f'<div class="pie-wrap"><svg class="pie" viewBox="0 0 232 232" role="img" '
            f'aria-label="{rotulo_svg}">{"".join(partes)}</svg>'
            f'<ul class="pie-legend">{"".join(itens)}</ul></div>\n')


# ══════════════════════════════════════════════════════════════════════
# Tabelas, badges, cards de pessoa
# ══════════════════════════════════════════════════════════════════════
def tabela(cabecalho, linhas, total=None, esconder=None, id_tabela=None):
    """Tabela. `total` é uma linha final destacada.

    esconder — índices de colunas que começam ocultas atrás de um botão
               'Ver distribuição'. Requer id_tabela.
    """
    esconder = set(esconder or [])
    cls = ' class="col-hide"' if esconder else ''
    idt = f' id="{id_tabela}"' if id_tabela else ''
    botao = ''
    if esconder and id_tabela:
        botao = (f'<div class="col-toggle-wrap"><button class="col-toggle" data-table="{id_tabela}" '
                 f'onclick="toggleCols(this)" aria-expanded="false">Ver colunas de detalhe</button></div>\n')
    th = ''.join(f'<th{" class=\"det\"" if i in esconder else ""}>{_txt(c)}</th>'
                 for i, c in enumerate(cabecalho))
    trs = []
    for linha in linhas:
        tds = ''.join(f'<td{" class=\"det\"" if i in esconder else ""}>{c}</td>'
                      for i, c in enumerate(linha))
        trs.append(f'<tr>{tds}</tr>')
    if total:
        tds = ''.join(f'<td{" class=\"det\"" if i in esconder else ""}>{c}</td>'
                      for i, c in enumerate(total))
        trs.append(f'<tr class="total-row">{tds}</tr>')
    return (botao + f'<table{idt}{cls}><thead><tr>{th}</tr></thead>\n'
            f'<tbody>\n' + '\n'.join(trs) + '\n</tbody></table>\n')


def badge(texto, tipo='pink', mini=False):
    """tipo: pink, green, amber, red, grey."""
    return f'<span class="badge{" mini" if mini else ""} {tipo}">{_txt(texto)}</span>'


# ══════════════════════════════════════════════════════════════════════
# Abas, blocos expansíveis e listas de comentários
# ══════════════════════════════════════════════════════════════════════


def bloco_comparativo(titulo, contador, conteudo):
    """Bloco recolhido para tabelas de comparativo entre períodos."""
    cont = f'<span class="grp-count">{esc(contador)}</span>' if contador else ''
    return (f'\n<details class="cmt-group"><summary><span class="grp-title">{esc(titulo)}</span>'
            f'{cont}</summary>\n<div class="cmp-body">\n{conteudo}\n</div>\n</details>\n')


def variacao(delta, sufixo='', casas=1, inverso=False):
    """Badge de variação com sinal. `inverso=True` quando cair é bom."""
    fmt = {0: lambda v: f'{v:.0f}', 2: n2}.get(casas, n1)
    piso = {0: 0.5, 2: 0.005}.get(casas, 0.05)
    if abs(delta) < piso:
        return badge({0: '0', 2: '0,00'}.get(casas, '0,0') + sufixo, 'grey')
    bom = (delta < 0) if inverso else (delta > 0)
    return badge(f'{"+" if delta > 0 else "−"}{fmt(abs(delta))}{sufixo}',
                 'green' if bom else 'red')
