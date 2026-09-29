"""Saav Dados BD - Portal Financeiro Saavedra
Orquestrador da aplicação web Streamlit.
"""

import streamlit as st
import numpy as np
import pandas as pd

from src.config.settings import APP_TITLE, APP_ICON
from src.services.table_service import ler_arquivo_tabela
from src.services.pdf_service import extrair_precos_pdf
from src.services.business_rules import normalizar_colunas_vendas, aplicar_regra_suprema
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

def gerar_assinatura_arquivos(vendas, pdfs, normal) -> str:
    """Gera assinatura única considerando o estado de todos os arquivos carregados."""
    partes = []
    if vendas:
        partes.append(f"vendas:{vendas.name}:{vendas.size}")
    if pdfs:
        for p in sorted(pdfs, key=lambda x: x.name):
            partes.append(f"pdf:{p.name}:{p.size}")
    if normal:
        partes.append(f"normal:{normal.name}:{normal.size}")
    return "|".join(partes)


# --- SESSÃO & PERSISTÊNCIA ---
if 'df_processado' not in st.session_state:
    st.session_state['df_processado'] = None
if 'arquivos_assinatura' not in st.session_state:
    st.session_state['arquivos_assinatura'] = None
if 'excel_export_bytes' not in st.session_state:
    st.session_state['excel_export_bytes'] = None

# --- UPLOAD DE ARQUIVOS ---
col1, col2, col3 = st.columns(3)
with col1:
    arquivo_excel = st.file_uploader("1º Relatório de Vendas (Excel / CSV)", type=['xlsx', 'xls', 'csv'], key="upload_vendas")
with col2:
    arquivos_pdf = st.file_uploader("2º Contratos BD (PDFs)", type=['pdf'], accept_multiple_files=True, key="upload_pdf")
with col3:
    arquivo_normal = st.file_uploader("3º Tabela Preços Normal (Excel / CSV)", type=['xlsx', 'xls', 'csv'], key="upload_normal")

# --- FLUXO PRINCIPAL ---
if not arquivo_excel:
    st.session_state['df_processado'] = None
    st.session_state['arquivos_assinatura'] = None
    st.session_state['excel_export_bytes'] = None
    render_guia_inicial()
else:
    # Identificador único combinando todos os arquivos carregados para reatividade imediata
    assinatura_atual = gerar_assinatura_arquivos(arquivo_excel, arquivos_pdf, arquivo_normal)
    
    # Processa se for a primeira vez ou se qualquer arquivo foi alterado/adicionado
    if st.session_state['df_processado'] is None or st.session_state['arquivos_assinatura'] != assinatura_atual:
        with st.spinner('Saav Dados BD está processando e equalizando os dados...'):
            # 1. Leitura e normalização de vendas
            df_vendas_raw = ler_arquivo_tabela(arquivo_excel)
            df_vendas = normalizar_colunas_vendas(df_vendas_raw)
            
            # 2. Leitura de PDFs
            df_precos_pdf = None
            if arquivos_pdf:
                df_precos_pdf = extrair_precos_pdf(arquivos_pdf)
                
            # 3. Leitura da Tabela Normal
            df_normal = None
            if arquivo_normal:
                df_normal = ler_arquivo_tabela(arquivo_normal)
                
            # 4. Aplicação da Regra Suprema
            df_final = aplicar_regra_suprema(df_vendas, df_precos_pdf, df_normal)
            
            st.session_state['df_processado'] = df_final
            st.session_state['arquivos_assinatura'] = assinatura_atual
            st.session_state['excel_export_bytes'] = None  # Invalida exportação anterior
            st.session_state['mapeamento_parceiros'] = None
            st.toast('Equalização de dados atualizada com sucesso!', icon='✅')

    df = st.session_state['df_processado'].copy()

    st.divider()

    # --- MAPEAMENTO DE PARCEIROS ---
    st.subheader("⚙️ Classificação de Parceiros")
    st.markdown("Defina se as vendas de cada parceiro devem ser direcionadas para a aba **NORMAL** ou para a aba do **CLIENTE**.")
    
    if 'CODPARC' not in df.columns: df['CODPARC'] = 'N/A'
    if 'CNPJPARCEIRO' not in df.columns: df['CNPJPARCEIRO'] = 'N/A'

    if st.session_state.get('mapeamento_parceiros') is None:
        parceiros_df = df[['CODPARC', 'CNPJPARCEIRO', 'RAZAOSOCIAL', 'ABA_DESTINO']].drop_duplicates(subset=['CODPARC', 'CNPJPARCEIRO'])
        parceiros_df['DESTINO'] = parceiros_df['ABA_DESTINO'].apply(lambda x: "NORMAL" if x == "NORMAL" else "CLIENTE")
        st.session_state['mapeamento_parceiros'] = parceiros_df[['CODPARC', 'CNPJPARCEIRO', 'RAZAOSOCIAL', 'DESTINO']]
        
    parceiros_editados = st.data_editor(
        st.session_state['mapeamento_parceiros'],
        column_config={
            "DESTINO": st.column_config.SelectboxColumn(
                "Aba Destino",
                help="Selecione NORMAL para contingência ou CLIENTE para a aba do respectivo cliente.",
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

    # Atualiza ABA_DESTINO e SIGLA_RESUMO no dataframe baseado na seleção do usuário
    mapeamento_dict = parceiros_editados.set_index(['CODPARC', 'CNPJPARCEIRO'])['DESTINO'].to_dict()
    
    def aplicar_mapeamento(row):
        destino_selecionado = mapeamento_dict.get((row['CODPARC'], row['CNPJPARCEIRO']), "NORMAL")
        return "NORMAL" if destino_selecionado == "NORMAL" else row['RAZAOSOCIAL']
        
    df['ABA_DESTINO'] = df.apply(aplicar_mapeamento, axis=1)
    df['SIGLA_RESUMO'] = df['ABA_DESTINO']

    st.divider()

    # --- PAINEL DE MÉTRICAS & GRÁFICOS ---
    render_kpis_e_graficos(df)

    st.divider()

    # --- PRÉVIA EDITÁVEL ---
    st.subheader("👁️ Prévia do Relatório (Aba RESUMO)")
    
    col_info, col_filtro = st.columns([3, 1])
    with col_info:
        st.markdown("✏️ **Dica:** Dê um duplo-clique na coluna `PRECO_COMPRA_FINAL` para preencher ou ajustar valores antes de gerar a planilha final.")
    with col_filtro:
        filtrar_pendentes = st.toggle("🔍 Apenas preços pendentes", value=False, help="Filtra a tabela para exibir apenas itens sem preço de compra preenchido.")

    # Agrupamento para exibição na Aba Resumo com Margens em tempo real
    agg_dict = {
        'QTDCOM': 'sum',
        'VLRTOTAL': 'sum',
        'PRECO_COMPRA_FINAL': 'first',
        'CONTRATO_FINAL': 'first',
        'SIGLA_RESUMO': 'first'
    }
    
    resumo_df = df.groupby(['ABA_DESTINO', 'GRUPO_CLIENTE', 'REFPROD', 'DESCRICAO']).agg(agg_dict).reset_index()
    resumo_df['VLR UNIT VENDA'] = np.where(resumo_df['QTDCOM'] > 0, resumo_df['VLRTOTAL'] / resumo_df['QTDCOM'], 0)
    
    custo_compra_calc = resumo_df['QTDCOM'] * resumo_df['PRECO_COMPRA_FINAL'].fillna(0)
    resumo_df['MARGEM BRUTA'] = np.where(
        resumo_df['PRECO_COMPRA_FINAL'].notna(),
        resumo_df['VLRTOTAL'] - custo_compra_calc,
        np.nan
    )
    
    cols_ui = ['CONTRATO_FINAL', 'SIGLA_RESUMO', 'GRUPO_CLIENTE', 'REFPROD', 'DESCRICAO', 'QTDCOM', 'VLR UNIT VENDA', 'VLRTOTAL', 'PRECO_COMPRA_FINAL', 'MARGEM BRUTA']
    resumo_df_ui = resumo_df[cols_ui].copy()
    
    if filtrar_pendentes:
        resumo_df_ui = resumo_df_ui[resumo_df_ui['PRECO_COMPRA_FINAL'].isna()]
        if resumo_df_ui.empty:
            st.success("Todos os itens possuem preço de compra definido.")
    
    colunas_bloqueadas = ['CONTRATO_FINAL', 'SIGLA_RESUMO', 'GRUPO_CLIENTE', 'REFPROD', 'DESCRICAO', 'QTDCOM', 'VLR UNIT VENDA', 'VLRTOTAL', 'MARGEM BRUTA']
    
    resumo_df_editado = st.data_editor(
        resumo_df_ui, 
        use_container_width=True, 
        hide_index=True,
        disabled=colunas_bloqueadas,
        column_config={
            "SIGLA_RESUMO": "nome da aba",
            "REFPROD": "Catalogo",
            "QTDCOM": "Quantidade",
            "VLR UNIT VENDA": st.column_config.NumberColumn(format="R$ %.2f"),
            "VLRTOTAL": st.column_config.NumberColumn(format="R$ %.2f"),
            "PRECO_COMPRA_FINAL": st.column_config.NumberColumn(format="R$ %.2f"),
            "MARGEM BRUTA": st.column_config.NumberColumn(format="R$ %.2f"),
        },
        key="data_editor_precos"
    )
    
    # Atualiza o DataFrame na sessão com edições manuais
    if not resumo_df_editado.empty:
        precos_editados = resumo_df_editado.set_index(['GRUPO_CLIENTE', 'REFPROD'])['PRECO_COMPRA_FINAL'].to_dict()
        df['PRECO_COMPRA_FINAL'] = df.apply(
            lambda row: precos_editados.get((row['GRUPO_CLIENTE'], row['REFPROD']), row['PRECO_COMPRA_FINAL']), 
            axis=1
        )
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
            file_name="PROCESSADO_Relatorio_Final_Saav_Dados_BD.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )