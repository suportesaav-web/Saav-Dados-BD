"""Serviço de extração e interpretação de propostas/contratos em arquivos PDF."""

import re
import streamlit as st
import pandas as pd
import pdfplumber
from src.config.settings import CONTRATOS_MAPPING, CLIENTES_CONFIG


def agrupar_cliente(texto: str, fallback: str = None) -> str:
    """Identifica e padroniza a instituição/cliente a partir de termos-chave e CNPJs configurados."""
    if not texto or pd.isna(texto):
        return fallback if fallback is not None else "OUTROS"
    
    r = str(texto).upper()
    for cfg in CLIENTES_CONFIG:
        if 'custom_match' in cfg and cfg['custom_match'](r):
            return cfg['sigla']
        for termo in cfg.get('termos', []):
            if termo in r:
                return cfg['sigla']
    
    return fallback if fallback is not None else r.strip()


# Regex monetário flexível: aceita 'R$ 1.234,56', 'R$1234,56', '1.234,56', '125,50'
RE_MOEDA_BR = re.compile(r'(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*,\d{2})')


@st.cache_data(show_spinner=False)
def extrair_precos_pdf(arquivos_pdf) -> pd.DataFrame:
    """
    Extrai referências e valores unitários tabelados de contratos em PDF utilizando pdfplumber
    e expressões regulares resilientes.
    """
    dados_precos = []
    
    for arquivo in arquivos_pdf:
        try:
            with pdfplumber.open(arquivo) as pdf:
                if not pdf.pages:
                    continue
                
                # Identifica cliente varrendo as primeiras 2 páginas se necessário
                texto_identificacao = ""
                for p in pdf.pages[:2]:
                    txt = p.extract_text() or ""
                    texto_identificacao += " " + txt.upper()
                
                grupo_cliente = agrupar_cliente(texto_identificacao, fallback="REVISAR")
                
                for page in pdf.pages:
                    tabelas = page.extract_tables()
                    for tabela in tabelas:
                        for linha in tabela:
                            if not linha or len(linha) < 3: 
                                continue
                            
                            celulas = [str(c).strip() if c is not None else "" for c in linha]
                            ref_prod = celulas[0].replace('.', '').replace('-', '').strip()
                            
                            # Verifica se o primeiro campo aparenta ser código de produto
                            if ref_prod.isalnum() and len(ref_prod) >= 4:
                                preco_encontrado = None
                                
                                # 1. Tenta encontrar célula explicitamente com 'R$'
                                for c in celulas:
                                    if "R$" in c:
                                        match = RE_MOEDA_BR.search(c)
                                        if match:
                                            preco_encontrado = match.group(1)
                                            break
                                
                                # 2. Se não achou com R$, busca valor monetário nas últimas colunas
                                if not preco_encontrado:
                                    for c in reversed(celulas[1:]):
                                        match = RE_MOEDA_BR.search(c)
                                        if match:
                                            preco_encontrado = match.group(1)
                                            break
                                
                                if preco_encontrado:
                                    valor_limpo = preco_encontrado.replace(".", "").replace(",", ".").strip()
                                    try:
                                        dados_precos.append({
                                            'GRUPO_CLIENTE': grupo_cliente,
                                            'REFPROD': ref_prod,
                                            'VALOR_TABELADO_BD': float(valor_limpo)
                                        })
                                    except ValueError:
                                        pass
        except Exception as e:
            nome = getattr(arquivo, 'name', 'desconhecido')
            st.warning(f"⚠️ Não foi possível processar o PDF {nome}: {e}")
            
    return pd.DataFrame(dados_precos)
