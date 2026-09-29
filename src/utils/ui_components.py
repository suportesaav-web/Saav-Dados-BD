"""Componentes visuais, cards KPI, gráficos e guias interativos da interface."""

import streamlit as st
import pandas as pd
from src.config.settings import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION, APP_ICON, CUSTOM_CSS, 
    PRIMARY_COLOR, DARK_NEUTRAL, CONTRATOS_MAPPING
)
from src.services.table_service import gerar_template_exemplo_vendas


def render_header():
    """Renderiza a barra de título e injeção do CSS corporativo Saavedra."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        f'<div class="main-title">{APP_ICON} {APP_TITLE} <span class="badge-version">v{APP_VERSION}</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<p class="sub-title">{APP_SUBTITLE}</p>', unsafe_allow_html=True)


def render_sidebar_help():
    """Renderiza o menu lateral de ajuda com instruções completas de uso do sistema."""
    with st.sidebar:
        st.markdown(f"### 📖 Central de Ajuda")
        st.markdown(f"**Saav Dados BD** `v{APP_VERSION}`")
        st.divider()
        
        with st.expander("🚀 Como Usar (Passo a Passo)", expanded=True):
            st.markdown("""
            1. **Anexe o Relatório de Vendas** (`.xlsx`, `.xls` ou `.csv`).
            2. **Anexe os Contratos BD em PDF** (propostas comerciais com preços tabelados).
            3. *(Opcional)* **Anexe a Tabela Normal** de preços de compra.
            4. O sistema equaliza e cruza as informações automaticamente.
            5. **Revise a Prévia**: se houver itens com preço de compra em branco, dê duplo-clique para preencher.
            6. Clique em **GERAR RELATÓRIO FINAL** para baixar a planilha consolidada.
            """)

        with st.expander("⚖️ Regra de Contingência (BD vs NORMAL)"):
            st.markdown("""
            * **Itens com Contrato BD:** Se a referência do produto constar no contrato do cliente (PDF), o item vai para a aba específica da instituição com o valor tabelado.
            * **Itens fora de Contrato:** Produtos sem correspondência de preço BD são direcionados automaticamente para a aba **`NORMAL`**.
            """)

        with st.expander("🏢 Contratos & Clientes Mapeados"):
            for cli, num in CONTRATOS_MAPPING.items():
                st.markdown(f"• **{cli}**: Contrato `{num}`")

        with st.expander("📥 Baixar Planilha Modelo"):
            st.markdown("Baixe um modelo pronto para testar o processamento:")
            template_bytes = gerar_template_exemplo_vendas()
            st.download_button(
                label="📄 Download Template (.xlsx)",
                data=template_bytes,
                file_name="Template_Vendas_Saav_Dados_BD_Exemplo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="sidebar_download_template"
            )

        with st.expander("👨‍💻 Suporte Corporativo"):
            st.markdown("""
            * **Unidade:** Saavedra Suporte Web
            * **Desenvolvedor:** Jonatan Severo
            * **E-mail:** `suporte.saav@saavedra.com.br`
            """)

        st.divider()
        st.caption("© Saavedra. Todos os direitos reservados.")


def render_guia_inicial():
    """Renderiza painel explicativo e botão de template quando nenhum arquivo de vendas estiver anexado."""
    st.info("Para iniciar a equalização e consolidação, faça o upload do relatório de vendas nos campos acima.")
    
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1:
        st.markdown("""
        #### 1. Relatório de Vendas
        * Arquivos `.xlsx`, `.xls` ou `.csv`
        * Identificação heurística de cabeçalho
        * Mapeamento de `REFPROD`, `VLRTOTAL`, `RAZAOSOCIAL`
        """)
    with col_g2:
        st.markdown("""
        #### 2. Contratos BD (PDF)
        * Propostas comerciais Becton Dickinson
        * Extração de preços unitários tabelados
        * Suporte a múltiplos PDFs em lote
        """)
    with col_g3:
        st.markdown("""
        #### 3. Tabela Preço Normal
        * Tabela padrão de custos (Excel/CSV)
        * Preenchimento para itens fora de contrato BD
        * Destinação automática para aba `NORMAL`
        """)
        
    st.divider()
    
    st.markdown("#### 📥 Planilha Modelo para Testes")
    template_bytes = gerar_template_exemplo_vendas()
    st.download_button(
        label="📄 Baixar Planilha Modelo (.xlsx)",
        data=template_bytes,
        file_name="Template_Vendas_Saav_Dados_BD_Exemplo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Baixe uma planilha estruturada para testar as regras de negócio do sistema."
    )


def render_kpis_e_graficos(df: pd.DataFrame):
    """Exibe painel executivo de KPIs financeiros, cobertura de preços e gráficos de distribuição."""
    total_linhas = len(df)
    total_bd = int(df['TEM_PRECO_BD'].sum())
    total_normal = total_linhas - total_bd
    vlr_total_venda = float(df['VLRTOTAL'].sum())
    
    # Cálculos financeiros de custo e margem
    custo_compra_series = df['QTDCOM'] * df['PRECO_COMPRA_FINAL'].fillna(0)
    vlr_total_compra = float(custo_compra_series.sum())
    margem_bruta = vlr_total_venda - vlr_total_compra
    pct_margem = (margem_bruta / vlr_total_venda * 100) if vlr_total_venda > 0 else 0.0
    
    itens_sem_preco = int(df['PRECO_COMPRA_FINAL'].isna().sum())
    itens_sem_ref = int((df['REFPROD'] == 'SEM_REF').sum())
    
    # 1ª Linha: Visão Financeira Executiva
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Faturado (Vendas)", f"R$ {vlr_total_venda:,.2f}")
    with kpi2:
        st.metric("Custo Estimado (Compras)", f"R$ {vlr_total_compra:,.2f}", help="Custo total com base nos contratos BD e tabela normal.")
    with kpi3:
        st.metric("Margem Bruta Estimada", f"R$ {margem_bruta:,.2f}", delta=f"{pct_margem:.1f}% Margem")
    with kpi4:
        if itens_sem_preco > 0:
            st.metric("Preços Pendentes", f"{itens_sem_preco:,}", delta="Revisar na prévia", delta_color="inverse")
        else:
            st.metric("Cobertura de Preços", "100%", delta="Auditoria OK")

    # 2ª Linha: Visão Operacional e Distribuição de Contratos
    col_op1, col_op2, col_op3 = st.columns(3)
    with col_op1:
        st.metric("Volume de Linhas", f"{total_linhas:,}")
    with col_op2:
        pct_bd = (total_bd / total_linhas * 100) if total_linhas > 0 else 0
        st.metric("Itens com Contrato BD", f"{total_bd:,}", delta=f"{pct_bd:.1f}% faturado sob contrato")
    with col_op3:
        pct_norm = (total_normal / total_linhas * 100) if total_linhas > 0 else 0
        st.metric("Itens na Aba NORMAL", f"{total_normal:,}", delta=f"-{pct_norm:.1f}% contingência", delta_color="inverse")

    # Alertas Preventivos
    if itens_sem_ref > 0:
        st.warning(f"⚠️ Atenção: Há {itens_sem_ref} linha(s) sem código de referência (`REFPROD`). Verifique se a coluna correta foi identificada no relatório do ERP.")
    elif itens_sem_preco > 0:
        st.info(f"💡 Dica Financeira: Há {itens_sem_preco} item(ns) sem preço de compra definido. Você pode preenchê-los na prévia editável abaixo antes de exportar.")

    # Gráficos de Apoio com paleta oficial Saavedra
    with st.expander("📊 Análise Gráfica de Distribuição & Margens", expanded=False):
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("**Faturamento por Grupo de Cliente (R$)**")
            chart_data = df.groupby('GRUPO_CLIENTE')['VLRTOTAL'].sum().reset_index()
            chart_data = chart_data.sort_values(by='VLRTOTAL', ascending=False).set_index('GRUPO_CLIENTE')
            st.bar_chart(chart_data, color=PRIMARY_COLOR)
            
        with col_c2:
            st.markdown("**Proporção de Itens (Contrato BD vs NORMAL)**")
            status_data = pd.DataFrame({
                'Categoria': ['Contrato BD', 'Aba NORMAL'],
                'Qtd Itens': [int(total_bd), int(total_normal)]
            }).set_index('Categoria')
            st.bar_chart(status_data, color=DARK_NEUTRAL)
