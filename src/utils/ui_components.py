import streamlit as st
import pandas as pd
from src.config.settings import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION, APP_ICON, CUSTOM_CSS, 
    PRIMARY_COLOR, DARK_NEUTRAL, CONTRATOS_MAPPING
)
from src.services.table_service import gerar_template_exemplo_vendas

def render_header():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="main-title">{APP_ICON} {APP_TITLE}</div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<p class="sub-title">{APP_SUBTITLE}</p>', unsafe_allow_html=True)

def render_sidebar_help():
    with st.sidebar:
        st.markdown(f"### 📖 Instruções")
        st.markdown(f"**Saav dados de BD/ Cliente** {APP_VERSION}")
        st.divider()
        
        with st.expander("🚀 Como Usar", expanded=True):
            st.markdown("""
            1. **Anexe o Relatório de Vendas** (.xlsx, .xls ou .csv).
            2. **Mapeie os Parceiros**: O sistema identificará os clientes. Você poderá selecionar quais ganharão uma aba própria.
            3. **Gere o Relatório**: Clique no botão final para baixar a planilha estruturada.
            """)

        with st.expander("🏢 Parceiros Pré-Mapeados"):
            for cli, num in CONTRATOS_MAPPING.items():
                if cli and cli != 'NORMAL':
                    st.markdown(f"• **{cli}**")

        st.divider()
        st.caption("© Saavedra. Todos os direitos reservados.")

def render_guia_inicial():
    st.info("Para iniciar, faça o upload do relatório de vendas acima.")
    
def render_kpis_e_graficos(df: pd.DataFrame):
    total_linhas = len(df)
    vlr_total_venda = float(df['VLRTOTAL'].sum())
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de Linhas (Faturamento)", total_linhas)
    with col2:
        st.metric("Valor Total Faturado", f"R$ {vlr_total_venda:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
    itens_sem_ref = int((df['REFPROD'] == 'SEM_REF').sum())
    if itens_sem_ref > 0:
        st.warning(f"⚠️ Atenção: Há {itens_sem_ref} linha(s) sem código de referência (REFPROD). Verifique se a coluna correta foi identificada no relatório do ERP.")
