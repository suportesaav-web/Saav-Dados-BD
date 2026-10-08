import streamlit as st
import numpy as np
import pandas as pd
import os

from src.config.settings import APP_TITLE, APP_ICON, CONTRATOS_MAPPING
from src.services.table_service import ler_arquivo_tabela
from src.services.business_rules import normalizar_colunas_vendas
from src.services.excel_exporter import gerar_planilha_consolidada
from src.utils.ui_components import render_header, render_guia_inicial, render_kpis_e_graficos, render_sidebar_help

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)

# --- CABEÇALHO, ESTILOS & MENU LATERAL DE AJUDA ---
render_header()
render_sidebar_help()

def gerar_assinatura_arquivos(vendas) -> str:
    """Gera assinatura única considerando o estado do arquivo de vendas."""
    if vendas:
        return f"vendas:{vendas.name}:{vendas.size}"
    return ""

# --- SESSÃO & PERSISTÊNCIA ---
if 'df_processado' not in st.session_state:
    st.session_state['df_processado'] = None
if 'arquivos_assinatura' not in st.session_state:
    st.session_state['arquivos_assinatura'] = None
if 'excel_export_bytes' not in st.session_state:
    st.session_state['excel_export_bytes'] = None
if 'mapeamento_parceiros' not in st.session_state:
    st.session_state['mapeamento_parceiros'] = None

# --- UPLOAD DE ARQUIVOS ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    arquivo_excel = st.file_uploader("Relatório de Vendas (Excel / CSV)", type=['xlsx', 'xls', 'csv'], key="upload_vendas")

# --- FLUXO PRINCIPAL ---
if not arquivo_excel:
    st.session_state['df_processado'] = None
    st.session_state['arquivos_assinatura'] = None
    st.session_state['excel_export_bytes'] = None
    st.session_state['mapeamento_parceiros'] = None
    render_guia_inicial()
else:
    assinatura_atual = gerar_assinatura_arquivos(arquivo_excel)
    
    if st.session_state['df_processado'] is None or st.session_state['arquivos_assinatura'] != assinatura_atual:
        with st.spinner('O sistema está processando os dados...'):
            df_vendas_raw = ler_arquivo_tabela(arquivo_excel)
            df_final = normalizar_colunas_vendas(df_vendas_raw)
            
            # Init prices columns just so other parts don't crash
            df_final['PRECO_COMPRA_FINAL'] = np.nan
            df_final['VALOR_TABELADO_BD'] = np.nan
            df_final['PRECO_NORMAL'] = np.nan
            df_final['CONTRATO_FINAL'] = 'N/A'
            df_final['ABA_DESTINO'] = 'NORMAL'
            df_final['SIGLA_RESUMO'] = 'NORMAL'
            
            st.session_state['df_processado'] = df_final
            st.session_state['arquivos_assinatura'] = assinatura_atual
            st.session_state['excel_export_bytes'] = None
            st.session_state['mapeamento_parceiros'] = None
            st.toast('Relatório lido com sucesso!', icon='✅')

    df = st.session_state['df_processado'].copy()

    st.divider()

    # --- MAPEAMENTO DE PARCEIROS ---
    st.subheader("⚙️ Classificação de Parceiros (Seleção de Abas)")
    st.markdown("Veja os clientes presentes no relatório e selecione quais devem ganhar uma aba própria (CLIENTE) ou ficar na aba genérica (NORMAL).")
    
    if 'CODPARC' not in df.columns: df['CODPARC'] = 'N/A'
    if 'CNPJPARCEIRO' not in df.columns: df['CNPJPARCEIRO'] = 'N/A'

    if st.session_state['mapeamento_parceiros'] is None:
        parceiros_df = df[['CODPARC', 'CNPJPARCEIRO', 'RAZAOSOCIAL', 'GRUPO_CLIENTE']].drop_duplicates(subset=['CODPARC', 'CNPJPARCEIRO'])
        # Mapeia como CLIENTE se tiver Grupo Mapeado (ex: UNIMED), caso contrário NORMAL
        parceiros_df['DESTINO'] = parceiros_df['GRUPO_CLIENTE'].apply(lambda x: "CLIENTE" if x != "NORMAL" else "NORMAL")
        st.session_state['mapeamento_parceiros'] = parceiros_df[['CODPARC', 'CNPJPARCEIRO', 'RAZAOSOCIAL', 'DESTINO']]
        
    parceiros_editados = st.data_editor(
        st.session_state['mapeamento_parceiros'],
        column_config={
            "DESTINO": st.column_config.SelectboxColumn(
                "Aba Destino",
                help="Selecione NORMAL para contingência ou CLIENTE para gerar uma aba específica.",
                options=["NORMAL", "CLIENTE"],
                required=True,
            )
        },
        disabled=['CODPARC', 'CNPJPARCEIRO', 'RAZAOSOCIAL'],
        hide_index=True,
        use_container_width=True,
        key="editor_parceiros"
    )
    
    st.session_state['mapeamento_parceiros'] = parceiros_editados

    # Atualiza ABA_DESTINO e SIGLA_RESUMO no dataframe baseado na seleção
    mapeamento_dict = parceiros_editados.set_index(['CODPARC', 'CNPJPARCEIRO'])['DESTINO'].to_dict()
    
    def aplicar_mapeamento(row):
        destino_selecionado = mapeamento_dict.get((row['CODPARC'], row['CNPJPARCEIRO']), "NORMAL")
        # Se escolheu CLIENTE, a aba ganha o nome do Grupo ou Razão Social
        nome_aba = row['GRUPO_CLIENTE'] if row['GRUPO_CLIENTE'] != 'NORMAL' else row['RAZAOSOCIAL']
        return "NORMAL" if destino_selecionado == "NORMAL" else nome_aba
        
    df['ABA_DESTINO'] = df.apply(aplicar_mapeamento, axis=1)
    df['SIGLA_RESUMO'] = df['ABA_DESTINO']

    st.divider()

    # --- PAINEL DE MÉTRICAS & GRÁFICOS ---
    render_kpis_e_graficos(df)

    st.divider()

    # --- PRÉVIA EDITÁVEL ---
    st.subheader("👁️ Prévia do Relatório (Aba RESUMO)")
    
    # Agrupamento para exibição na Aba Resumo
    agg_dict = {
        'QTDCOM': 'sum',
        'VLRTOTAL': 'sum',
        'SIGLA_RESUMO': 'first'
    }
    
    resumo_df = df.groupby(['ABA_DESTINO', 'REFPROD', 'DESCRICAO']).agg(agg_dict).reset_index()
    resumo_df['VLR UNIT VENDA'] = np.where(resumo_df['QTDCOM'] > 0, resumo_df['VLRTOTAL'] / resumo_df['QTDCOM'], 0)
    
    cols_ui = ['SIGLA_RESUMO', 'REFPROD', 'DESCRICAO', 'QTDCOM', 'VLR UNIT VENDA', 'VLRTOTAL']
    resumo_df_ui = resumo_df[cols_ui].copy()
    
    st.dataframe(
        resumo_df_ui, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "SIGLA_RESUMO": "Aba Destino",
            "REFPROD": "Catalogo",
            "QTDCOM": "Quantidade",
            "VLR UNIT VENDA": st.column_config.NumberColumn(format="R$ %.2f"),
            "VLRTOTAL": st.column_config.NumberColumn(format="R$ %.2f"),
        }
    )
    
    # Guarda as alteracoes no estado (mesmo sem o editor de preco de compra)
    st.session_state['df_processado'] = df
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- GERAÇÃO DO ARQUIVO CONSOLIDADO ---
    col_btn, col_status = st.columns([2, 3])
    with col_btn:
        if st.button("GERAR RELATÓRIO FINAL 📥", type="primary", use_container_width=True):
            with st.spinner("Consolidando dados e gerando arquivo Excel..."):
                excel_bytes = gerar_planilha_consolidada(st.session_state['df_processado'])
                st.session_state['excel_export_bytes'] = excel_bytes
                st.toast("Relatório consolidado gerado com sucesso!", icon="📊")

    if 'excel_export_bytes' in st.session_state and st.session_state['excel_export_bytes'] is not None:
        st.download_button(
            label="📄 Baixar Planilha Consolidada (.xlsx)",
            data=st.session_state['excel_export_bytes'],
            file_name="Saav_Dados_BD_Clientes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
