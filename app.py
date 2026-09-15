# -*- coding: utf-8 -*-
"""
Interface do Projeto de NPS para empresas.

Execute com:
    streamlit run app.py

Fluxo na tela: enviar a planilha -> escolher a base comparativa -> gerar
-> conferir validação -> visualizar e baixar o HTML.
"""
from pathlib import Path

import streamlit as st

from nps.relatorio import gerar
from nps.versao import ENTREGA, FUNCIONALIDADES, NOME_PROJETO, VERSAO

RAIZ = Path(__file__).parent
EXEMPLO = RAIZ / 'data' / 'exemplo_base_atual.csv'
COMPARATIVA_PADRAO = RAIZ / 'data' / 'base_comparativa_marco2026.csv'

st.set_page_config(page_title=NOME_PROJETO, page_icon='📊', layout='wide')

with st.sidebar:
    st.markdown(f'### {NOME_PROJETO}')
    st.caption(f'Versão {VERSAO} · {ENTREGA}')
    st.markdown('**Funcionalidades desta versão**')
    for f in FUNCIONALIDADES:
        st.markdown(f'- {f}')

st.title('Relatório de NPS')
st.write('Envie a planilha da pesquisa (base contatada vs. respostas) para gerar o relatório HTML.')

col1, col2 = st.columns(2)
with col1:
    st.subheader('1. Pesquisa atual')
    arquivo = st.file_uploader('Planilha em CSV', type=['csv'])
    usar_exemplo = st.checkbox('Usar a planilha de exemplo do repositório', value=arquivo is None)
    periodo = st.text_input('Rótulo do período atual', value='Agosto/2026')

with col2:
    st.subheader('2. Base comparativa')
    modo = st.radio('Período anterior', ['Usar base incluída (Março/2026)', 'Enviar outro CSV de indicadores',
                                         'Não comparar'])
    comparativa = None
    if modo.startswith('Usar'):
        comparativa = COMPARATIVA_PADRAO.read_bytes()
    elif modo.startswith('Enviar'):
        arq_cmp = st.file_uploader('CSV de indicadores (colunas: indicador, valor)', type=['csv'], key='cmp')
        comparativa = arq_cmp.getvalue() if arq_cmp else None

st.divider()
if st.button('Gerar relatório', type='primary'):
    if arquivo is not None and not usar_exemplo:
        planilha = arquivo.getvalue()
    elif usar_exemplo:
        planilha = EXEMPLO.read_bytes()
    else:
        st.error('Envie uma planilha ou marque a opção de usar o exemplo.')
        st.stop()
    try:
        html, ctx = gerar(planilha, periodo, comparativa)
    except ValueError as erro:
        st.error(str(erro))
        st.stop()
    st.session_state['html'] = html
    st.session_state['ctx'] = ctx

if 'html' in st.session_state:
    ctx = st.session_state['ctx']
    v = ctx['validacao']
    m = ctx['m']['composicao_nps']

    st.subheader('3. Validação')
    c1, c2, c3 = st.columns(3)
    c1.metric('Linhas lidas', v['linhas'])
    c2.metric('Respondentes', v['respondentes'])
    c3.metric('NPS', f'{round(m["nps"]):.0f}')
    for aviso in v['avisos']:
        st.warning(aviso)
    with st.expander('Colunas reconhecidas na planilha'):
        st.table({'Campo': list(v['colunas_mapeadas']), 'Coluna na planilha': list(v['colunas_mapeadas'].values())})
        if v['colunas_ignoradas']:
            st.caption('Não utilizadas nesta versão: ' + ', '.join(v['colunas_ignoradas']))

    st.subheader('4. Relatório')
    nome = f'relatorio_nps_{periodo.replace("/", "_").lower()}.html'
    st.download_button('Baixar HTML', st.session_state['html'], file_name=nome, mime='text/html')
    # o HTML é gerado pelo próprio sistema e escapa todo texto vindo da planilha
    if hasattr(st, 'iframe'):
        st.iframe(st.session_state['html'], height=1400)
    else:  # versões antigas do Streamlit
        import streamlit.components.v1 as components
        components.html(st.session_state['html'], height=1400, scrolling=True)
