"""Testes unitários automatizados para regras de negócio e mapeamento do The Nehemizer."""

import pandas as pd
import numpy as np
import pytest

from src.services.pdf_service import agrupar_cliente
from src.services.business_rules import normalizar_colunas_vendas, aplicar_regra_suprema
from src.config.settings import CLIENTES_CONFIG, CONTRATOS_MAPPING


class TestAgruparCliente:
    """Testes de identificação heurística de clientes e contratos."""

    def test_identificacao_unimed(self):
        assert agrupar_cliente("UNIMED PORTO ALEGRE COOP MEDICA") == "UNIMED"
        assert agrupar_cliente("HOSPITAL PARCEIRO CNPJ 870966160001") == "UNIMED"

    def test_identificacao_puc(self):
        assert agrupar_cliente("UNIAO BRASILEIRA DE EDUCACAO E ASSISTENCIA") == "PUC"
        assert agrupar_cliente("HOSPITAL SAO LUCAS DA PUC") == "PUC"
        assert agrupar_cliente("PARCEIRO 88630413") == "PUC"

    def test_identificacao_hcpa(self):
        assert agrupar_cliente("HOSPITAL DE CLINICAS DE PORTO ALEGRE") == "HCPA"
        assert agrupar_cliente("HCPA 87020517") == "HCPA"

    def test_identificacao_sms_poa(self):
        assert agrupar_cliente("PREFEITURA DE PORTO ALEGRE SMS") == "SMS POA"
        assert agrupar_cliente("MUNICIPIO DE PORTO ALEGRE 92963560") == "SMS POA"

    def test_identificacao_ebserh(self):
        assert agrupar_cliente("EMPRESA BRASILEIRA DE SERVICOS HOSPITALARES EBSERH") == "EBSERH"

    def test_identificacao_hcaa(self):
        assert agrupar_cliente("HOSPITAL DE CARIDADE ASTROGILDO DE AZEVEDO") == "HCAA"

    def test_identificacao_divina(self):
        assert agrupar_cliente("SOCIEDADE SULINA DIVINA PROVIDENCIA") == "H DIVINA"

    def test_identificacao_ghc(self):
        assert agrupar_cliente("GRUPO HOSPITALAR CONCEICAO GHC") == "CONCEICAO"
        assert agrupar_cliente("HOSPITAL NOSSA SENHORA DA CONCEIÇÃO") == "CONCEICAO"

    def test_identificacao_desconhecido(self):
        assert agrupar_cliente("CLINICA MEDICA PRIVADA DESCONHECIDA") == "CLINICA MEDICA PRIVADA DESCONHECIDA"
        assert agrupar_cliente("", fallback="OUTROS") == "OUTROS"
        assert agrupar_cliente(None, fallback="OUTROS") == "OUTROS"


class TestNormalizacaoVendas:
    """Testes de padronização de colunas e dados brutos do ERP."""

    def test_renomeacao_colunas_sinonimos(self):
        df_raw = pd.DataFrame({
            'Cd Prod': [101, 102],
            'Descrição do Item': ['Item A', 'Item B'],
            'Qtd Faturada': [10, 20],
            'Vlr Total Liq': [150.0, 300.0],
            'Razão Social Cliente': ['UNIMED POA', 'CLINICA XYZ']
        })
        df_norm = normalizar_colunas_vendas(df_raw)
        
        assert 'REFPROD' in df_norm.columns
        assert 'DESCRICAO' in df_norm.columns
        assert 'QTDCOM' in df_norm.columns
        assert 'VLRTOTAL' in df_norm.columns
        assert 'RAZAOSOCIAL' in df_norm.columns
        assert 'GRUPO_CLIENTE' in df_norm.columns

    def test_limpeza_refprod_com_ponto_zero(self):
        df_raw = pd.DataFrame({
            'REFPROD': ['300600.0', '381423.0', 'ABC123'],
            'RAZAOSOCIAL': ['UNIMED', 'PUC', 'OUTROS'],
            'VLRTOTAL': [100.0, 200.0, 300.0]
        })
        df_norm = normalizar_colunas_vendas(df_raw)
        assert df_norm['REFPROD'].tolist() == ['300600', '381423', 'ABC123']


class TestRegraSupremaDeContingencia:
    """Testes da regra determinística de precificação e roteamento de abas."""

    def test_roteamento_com_e_sem_contrato(self):
        df_vendas = pd.DataFrame({
            'GRUPO_CLIENTE': ['UNIMED', 'UNIMED', 'PUC'],
            'REFPROD': ['300600', '999999', '381423'],
            'DESCRICAO': ['Cateter BD', 'Item Sem Contrato', 'Seringa BD'],
            'QTDCOM': [10, 5, 20],
            'VLRTOTAL': [500.0, 100.0, 800.0],
            'CONTRATOCLIENTE': ['', '', '']
        })

        # Simula PDF com preço apenas para 300600 na UNIMED e 381423 na PUC
        df_precos_pdf = pd.DataFrame({
            'GRUPO_CLIENTE': ['UNIMED', 'PUC'],
            'REFPROD': ['300600', '381423'],
            'VALOR_TABELADO_BD': [35.00, 28.50]
        })

        # Simula Tabela Normal com fallback
        df_normal = pd.DataFrame({
            'REFPROD': ['999999'],
            'PRECO': [12.00]
        })

        df_final = aplicar_regra_suprema(df_vendas, df_precos_pdf, df_normal)

        # 1. Item com contrato BD -> vai para aba UNIMED com valor tabelado
        item_bd = df_final[df_final['REFPROD'] == '300600'].iloc[0]
        assert item_bd['ABA_DESTINO'] == 'UNIMED'
        assert item_bd['TEM_PRECO_BD'] == True
        assert item_bd['PRECO_COMPRA_FINAL'] == 35.00
        assert item_bd['CONTRATO_FINAL'] == CONTRATOS_MAPPING['UNIMED']

        # 2. Item fora de contrato -> vai para aba NORMAL com valor da tabela normal
        item_normal = df_final[df_final['REFPROD'] == '999999'].iloc[0]
        assert item_normal['ABA_DESTINO'] == 'NORMAL'
        assert item_normal['TEM_PRECO_BD'] == False
        assert item_normal['PRECO_COMPRA_FINAL'] == 12.00
        assert item_normal['CONTRATO_FINAL'] == 'NORMAL'


class TestExcelExporter:
    """Testes de geração do arquivo consolidado em Excel com cálculos de margem."""

    def test_geracao_planilha_consolidada_com_margem(self):
        from src.services.excel_exporter import gerar_planilha_consolidada
        import io

        df_mock = pd.DataFrame({
            'ABA_DESTINO': ['UNIMED', 'NORMAL'],
            'GRUPO_CLIENTE': ['UNIMED', 'OUTROS'],
            'REFPROD': ['300600', '999999'],
            'DESCRICAO': ['Cateter', 'Outro'],
            'QTDCOM': [10, 5],
            'VLRTOTAL': [500.0, 100.0],
            'PRECO_COMPRA_FINAL': [30.0, 10.0],
            'CONTRATO_FINAL': ['450128261', 'NORMAL'],
            'SIGLA_RESUMO': ['UNIMED', 'NORMAL'],
            'CONTRATO_ORIGINAL': ['', ''],
            'CNPJPARCEIRO': ['87096616', '00000000'],
            'UF': ['RS', 'RS'],
            'CODCLIUSO': ['1', '2'],
            'RAZAOSOCIAL': ['UNIMED', 'OUTROS'],
            'CNPJPARCUSO': ['87096616', '00000000'],
            'CONVENIO': ['', '']
        })

        excel_bytes = gerar_planilha_consolidada(df_mock)
        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0

        # Valida que o Excel gerado pode ser lido pelo pandas e contém a aba RESUMO
        excel_file = io.BytesIO(excel_bytes)
        df_resumo_lido = pd.read_excel(excel_file, sheet_name='RESUMO')
        
        assert 'MARGEM BRUTA' in df_resumo_lido.columns
        assert '% MARGEM' in df_resumo_lido.columns
        assert 'TOTAL GERAL CONSOLIDADO' in df_resumo_lido['PEDIDO'].values
