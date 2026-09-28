"""Motor de regras de negócio e consolidação de dados de vendas e contratos."""

import numpy as np
import pandas as pd
from src.config.settings import CONTRATOS_MAPPING
from src.services.pdf_service import agrupar_cliente


def normalizar_colunas_vendas(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza e mapeia os nomes de colunas de vendas para os padrões do sistema."""
    df.columns = df.columns.astype(str).str.upper().str.strip()
    
    novas_colunas = {}
    for col in df.columns:
        c_up = str(col).upper().strip()
        if 'REF' in c_up and 'PROD' in c_up: novas_colunas[col] = 'REFPROD'
        elif 'DESC' in c_up: novas_colunas[col] = 'DESCRICAO'
        elif 'QTD' in c_up: novas_colunas[col] = 'QTDCOM'
        elif 'VLR' in c_up or 'VALOR' in c_up: novas_colunas[col] = 'VLRTOTAL'
        elif 'RAZ' in c_up and 'SOC' in c_up: novas_colunas[col] = 'RAZAOSOCIAL'
        elif 'CONV' in c_up: novas_colunas[col] = 'CONVENIO'
        elif 'CONTRATO' in c_up: novas_colunas[col] = 'CONTRATOCLIENTE'
        elif 'UF' == c_up: novas_colunas[col] = 'UF'
        elif 'COD' in c_up and 'CLI' in c_up: novas_colunas[col] = 'CODCLIUSO'
        elif 'COD' in c_up and 'PARC' in c_up: novas_colunas[col] = 'CODPARC'
        elif 'CNPJ' in c_up and 'PARCEIRO' in c_up: novas_colunas[col] = 'CNPJPARCEIRO'
    
    df = df.rename(columns=novas_colunas)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Garantia de colunas essenciais
    if 'RAZAOSOCIAL' not in df.columns: df['RAZAOSOCIAL'] = 'DESCONHECIDO'
    if 'REFPROD' not in df.columns: df['REFPROD'] = 'SEM_REF'
    if 'QTDCOM' not in df.columns: df['QTDCOM'] = 1
    if 'VLRTOTAL' not in df.columns: df['VLRTOTAL'] = 0.0
    if 'DESCRICAO' not in df.columns: df['DESCRICAO'] = 'SEM DESCRICAO'
    if 'CONTRATOCLIENTE' not in df.columns: df['CONTRATOCLIENTE'] = ''
    
    # Limpeza de códigos alfanuméricos e CNPJs
    df['REFPROD'] = df['REFPROD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
    if 'CNPJPARCEIRO' in df.columns:
        df['CNPJPARCEIRO'] = df['CNPJPARCEIRO'].astype(str).str.replace(r'\D', '', regex=True)
    if 'CNPJPARCUSO' in df.columns:
        df['CNPJPARCUSO'] = df['CNPJPARCUSO'].astype(str).str.replace(r'\D', '', regex=True)
        
    df['GRUPO_CLIENTE'] = df['RAZAOSOCIAL'].apply(lambda x: agrupar_cliente(x))
    df['CONTRATO_ORIGINAL'] = df['CONTRATOCLIENTE']
    
    return df


def aplicar_regra_suprema(df_vendas: pd.DataFrame, df_precos_pdf: pd.DataFrame, df_normal: pd.DataFrame) -> pd.DataFrame:
    """Cruza vendas com PDFs de contratos e Tabela Normal aplicando a Regra Suprema de Contingência."""
    df = df_vendas.copy()
    
    # 1. Merge com Contratos BD (PDFs)
    if df_precos_pdf is not None and not df_precos_pdf.empty:
        df_precos_pdf = df_precos_pdf.drop_duplicates(subset=['GRUPO_CLIENTE', 'REFPROD'])
        df = pd.merge(df, df_precos_pdf, on=['GRUPO_CLIENTE', 'REFPROD'], how='left')
    
    if 'VALOR_TABELADO_BD' not in df.columns:
        df['VALOR_TABELADO_BD'] = np.nan
        
    # 2. Merge com Tabela Normal
    if df_normal is not None and not df_normal.empty:
        norm_cols = {}
        for col in df_normal.columns:
            c_up = str(col).upper().strip()
            if 'REF' in c_up and 'PROD' in c_up: norm_cols[col] = 'REFPROD'
            elif any(k in c_up for k in ['VLR', 'VALOR', 'PRECO', 'PREÇO']): norm_cols[col] = 'PRECO_NORMAL'
        
        df_norm = df_normal.rename(columns=norm_cols)
        if 'REFPROD' in df_norm.columns and 'PRECO_NORMAL' in df_norm.columns:
            df_norm['REFPROD'] = df_norm['REFPROD'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df_norm = df_norm.drop_duplicates(subset=['REFPROD'])
            df = pd.merge(df, df_norm[['REFPROD', 'PRECO_NORMAL']], on='REFPROD', how='left')
        else:
            df['PRECO_NORMAL'] = np.nan
    else:
        df['PRECO_NORMAL'] = np.nan
        
    # 3. Aplicação da Regra de Negócio Suprema
    df['TEM_PRECO_BD'] = df['VALOR_TABELADO_BD'].notna()
    
    # Se não tiver preço de BD, destina para a aba NORMAL
    df['ABA_DESTINO'] = np.where(df['TEM_PRECO_BD'], df['GRUPO_CLIENTE'], 'NORMAL')
    df['SIGLA_RESUMO'] = np.where(df['TEM_PRECO_BD'], df['GRUPO_CLIENTE'], 'NORMAL')
    
    # Número do contrato
    df['CONTRATO_BD_NUM'] = df['GRUPO_CLIENTE'].map(CONTRATOS_MAPPING).fillna('NORMAL')
    df['CONTRATO_FINAL'] = np.where(df['TEM_PRECO_BD'], df['CONTRATO_BD_NUM'], 'NORMAL')
    
    # Preço final de compra
    df['PRECO_COMPRA_FINAL'] = df['VALOR_TABELADO_BD'].fillna(df['PRECO_NORMAL'])
    
    return df
