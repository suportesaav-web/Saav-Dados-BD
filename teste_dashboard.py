import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv

# Carrega o token e credenciais do arquivo .env
load_dotenv(override=True)

st.set_page_config(page_title="Teste de Integração Sankhya", layout="wide")

st.title("🧪 Teste de Integração: Dashboard Sankhya (API)")
st.write("Esta tela é dedicada a testar a extração de dados diretamente do Sankhya, validando credenciais, tokens e o retorno da consulta do **Dashboard 1402**.")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Configuração da Requisição")
    codemp = st.text_input("Empresa (CODEMP)", value="1")
    
    col_d1, col_d2 = st.columns(2)
    import datetime
    hoje = datetime.date.today()
    data_ini = col_d1.date_input("Data Inicial", value=hoje - datetime.timedelta(days=30))
    data_fim = col_d2.date_input("Data Final", value=hoje)
    
    st.write("**Filtros automáticos embutidos na Query:**")
    st.markdown("- **Tipo Movimento:** Saída (`TIPMOV IN ('V', 'E')`)")
    
    if st.button("Executar Consulta", type="primary", use_container_width=True):
        st.session_state['run_test'] = True
        
with col2:
    st.subheader("Resultados / Logs")
    if st.session_state.get('run_test'):
        with st.spinner("Conectando ao Sankhya W (Sandbox)..."):
            try:
                from src.services.sankhya_service import SankhyaService
                srv = SankhyaService()
                
                # Formatando as datas para DD/MM/YYYY
                str_ini = data_ini.strftime("%d/%m/%Y")
                str_fim = data_fim.strftime("%d/%m/%Y")
                
                df = srv.buscar_vendas(str_ini, str_fim, codemp)
                
                st.success(f"✅ Conexão estabelecida e query executada! Foram retornados {len(df)} registros.")
                
                st.write("📊 **Amostra dos Dados (Filtrados conforme o Excel de Vendas):**")
                
                # Filtrando apenas as colunas que têm no arquivo(8).xlsx e renomeando
                colunas_de_interesse = [
                    'CNPJ_PARCEIRO', 'RAZSOCIAL', 'REFERENCIA', 'DESCRICAO', 
                    'QTDCOM', 'VLRUNIT', 'VLRPROD', 'NCM', 'CFOP', 'NUMNF', 'DTEMISSAO'
                ]
                
                # Selecionar as colunas (caso alguma venha diferente do esperado, iteramos apenas nas que existem)
                colunas_existentes = [col for col in colunas_de_interesse if col in df.columns]
                df_view = df[colunas_existentes].copy()
                
                # Renomeando para ficar igual à planilha antiga pra facilitar a visualização
                rename_map = {
                    'RAZSOCIAL': 'Razão Social',
                    'REFERENCIA': 'Ref Prod',
                    'DESCRICAO': 'Descrição',
                    'QTDCOM': 'Qtd Com',
                    'VLRUNIT': 'Preço Unitário',
                    'VLRPROD': 'Valor Prod',
                    'NUMNF': 'NF'
                }
                df_view = df_view.rename(columns=rename_map)
                
                st.dataframe(df_view.head(50))
                
            except Exception as e:
                st.error("❌ Ocorreu um erro na conexão com a API:")
                st.code(str(e))
                
        # Reseta o botão para não reexecutar do nada
        st.session_state['run_test'] = False
