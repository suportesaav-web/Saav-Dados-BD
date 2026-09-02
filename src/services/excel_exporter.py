"""Serviço de geração e formatação contábil do relatório consolidado em Excel (XlsxWriter)."""

import io
import pandas as pd
from src.config.settings import PRIMARY_COLOR, SECONDARY_COLOR, BG_CARD_COLOR


def gerar_planilha_consolidada(df: pd.DataFrame) -> bytes:
    """Gera o arquivo Excel final consolidado com estilos corporativos Saavedra, Aba RESUMO e Abas Individuais."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Estilos Corporativos Saavedra
        formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
        formato_percentual = workbook.add_format({'num_format': '0.0%'})
        formato_cabecalho = workbook.add_format({
            'bold': True,
            'bg_color': PRIMARY_COLOR,
            'font_color': 'white',
            'border': 1
        })
        formato_subtotal = workbook.add_format({
            'bold': True,
            'bg_color': BG_CARD_COLOR,
            'border': 1
        })
        formato_total_geral = workbook.add_format({
            'bold': True,
            'bg_color': SECONDARY_COLOR,
            'font_color': 'white',
            'border': 1
        })
        formato_cabecalho_aba = workbook.add_format({
            'bold': True,
            'bg_color': SECONDARY_COLOR,
            'font_color': 'white',
            'border': 1
        })
        
        # 1. ABA RESUMO
        df_resumo_export = df.groupby(['ABA_DESTINO', 'GRUPO_CLIENTE', 'REFPROD', 'DESCRICAO']).agg({
            'CONTRATO_FINAL': 'first',
            'SIGLA_RESUMO': 'first',
            'QTDCOM': 'sum',
            'VLRTOTAL': 'sum',
            'PRECO_COMPRA_FINAL': 'first'
        }).reset_index()
        
        df_resumo_export = df_resumo_export.sort_values(by=['ABA_DESTINO', 'GRUPO_CLIENTE', 'REFPROD'])
        linhas_resumo = []
        
        total_geral_venda = 0.0
        total_geral_compra = 0.0

        for destino, group in df_resumo_export.groupby('ABA_DESTINO', sort=False):
            subtotal_venda = 0.0
            subtotal_compra = 0.0
            
            for _, row in group.iterrows():
                vlr_unit_venda = row['VLRTOTAL'] / row['QTDCOM'] if row['QTDCOM'] > 0 else 0
                tem_compra = pd.notna(row['PRECO_COMPRA_FINAL'])
                vlr_total_compra = row['QTDCOM'] * row['PRECO_COMPRA_FINAL'] if tem_compra else 0
                margem_linha = (row['VLRTOTAL'] - vlr_total_compra) if tem_compra else None
                pct_margem_linha = (margem_linha / row['VLRTOTAL']) if (margem_linha is not None and row['VLRTOTAL'] > 0) else None
                
                linhas_resumo.append([
                    row['CONTRATO_FINAL'], 
                    row['SIGLA_RESUMO'], 
                    row['GRUPO_CLIENTE'], 
                    row['REFPROD'], 
                    row['DESCRICAO'], 
                    row['QTDCOM'], 
                    vlr_unit_venda, 
                    row['VLRTOTAL'], 
                    row['PRECO_COMPRA_FINAL'] if tem_compra else None, 
                    vlr_total_compra if tem_compra else None,
                    margem_linha,
                    pct_margem_linha
                ])
                subtotal_venda += row['VLRTOTAL']
                subtotal_compra += vlr_total_compra
            
            subtotal_margem = subtotal_venda - subtotal_compra
            subtotal_pct_margem = (subtotal_margem / subtotal_venda) if subtotal_venda > 0 else 0
            
            linhas_resumo.append([
                '', '', f'TOTAL ACUMULADO {destino}', '', '', '', '', subtotal_venda, '', subtotal_compra if subtotal_compra > 0 else None, subtotal_margem, subtotal_pct_margem
            ])
            total_geral_venda += subtotal_venda
            total_geral_compra += subtotal_compra
        
        # Linha de Fechamento: TOTAL GERAL CONSOLIDADO
        total_geral_margem = total_geral_venda - total_geral_compra
        total_geral_pct = (total_geral_margem / total_geral_venda) if total_geral_venda > 0 else 0
        linhas_resumo.append([
            '', '', 'TOTAL GERAL CONSOLIDADO', '', '', '', '', total_geral_venda, '', total_geral_compra if total_geral_compra > 0 else None, total_geral_margem, total_geral_pct
        ])
            
        df_excel_resumo = pd.DataFrame(linhas_resumo, columns=[
            'CONTRATO', 'SIGLA/GRUPO', 'PEDIDO', 'Ref Prod', 'Descrição', 'Qtd Com', 'VLR UNIT', 'VLR TOTAL', 'VLR UNIT COMPRA', 'VLR TOTAL COMPRA', 'MARGEM BRUTA', '% MARGEM'
        ])
        
        df_excel_resumo.to_excel(writer, sheet_name='RESUMO', index=False)
        ws_resumo = writer.sheets['RESUMO']
        ws_resumo.set_column('A:B', 16)
        ws_resumo.set_column('C:E', 36)
        ws_resumo.set_column('F:F', 12)
        ws_resumo.set_column('G:J', 18, formato_moeda)
        ws_resumo.set_column('K:K', 18, formato_moeda)
        ws_resumo.set_column('L:L', 14, formato_percentual)
        
        for col_num, value in enumerate(df_excel_resumo.columns.values):
            ws_resumo.write(0, col_num, value, formato_cabecalho)
        
        for row_num, row_data in enumerate(linhas_resumo):
            txt = str(row_data[2])
            if 'TOTAL GERAL CONSOLIDADO' in txt:
                ws_resumo.set_row(row_num + 1, None, formato_total_geral)
            elif 'TOTAL ACUMULADO' in txt:
                ws_resumo.set_row(row_num + 1, None, formato_subtotal)
        
        # 2. ABAS INDIVIDUAIS
        abas_para_criar = df['ABA_DESTINO'].dropna().unique().tolist()
        
        for aba in abas_para_criar:
            df_aba = df[df['ABA_DESTINO'] == aba].copy()
            
            colunas_aba = []
            for _, r in df_aba.iterrows():
                contrato_str = str(r.get('CONTRATO_ORIGINAL', ''))
                cnpj_p = r.get('CNPJPARCEIRO', '')
                uf = r.get('UF', '')
                cod_cli = r.get('CODCLIUSO', '')
                razao = r.get('RAZAOSOCIAL', '')
                cnpj_u = r.get('CNPJPARCUSO', '')
                conv = r.get('CONVENIO', '')
                ref = r.get('REFPROD', '')
                desc = r.get('DESCRICAO', '')
                qtd = r.get('QTDCOM', '')
                colunas_aba.append([contrato_str, f"'{cnpj_p}", uf, cod_cli, razao, f"'{cnpj_u}", conv, ref, desc, qtd])
            
            df_excel_aba = pd.DataFrame(colunas_aba, columns=[
                'CONTRATO', 'CNPJ_PARCEIRO', 'UF', 'COD_CLI_USO', 'RAZÃO SOCIAL', 'CNPJ_PARC_USO', 'CONVENIO', 'Ref Prod', 'Descrição', 'Qtd'
            ])
            
            nome_sheet = str(aba)[:31].replace(':', '').replace('/', '')
            df_excel_aba.to_excel(writer, sheet_name=nome_sheet, index=False)
            ws_aba = writer.sheets[nome_sheet]
            ws_aba.set_column('A:D', 15)
            ws_aba.set_column('E:E', 35)
            ws_aba.set_column('F:J', 18)
            
            for col_num, value in enumerate(df_excel_aba.columns.values):
                ws_aba.write(0, col_num, value, formato_cabecalho_aba)
            
            start_r = len(df_excel_aba) + 4
            ws_aba.write_row(start_r - 1, 0, ['Ref Prod', 'Descrição', 'Qtd Com', 'VLR UNIT VENDA', 'VLR TOTAL VENDA'], formato_subtotal)
            
            resumo_cli = df_aba.groupby(['REFPROD', 'DESCRICAO']).agg({'QTDCOM': 'sum', 'VLRTOTAL': 'sum'}).reset_index()
            
            for idx, rcli in resumo_cli.iterrows():
                v_unit = rcli['VLRTOTAL'] / rcli['QTDCOM'] if rcli['QTDCOM'] > 0 else 0
                ws_aba.write_row(start_r + idx, 0, [rcli['REFPROD'], rcli['DESCRICAO'], rcli['QTDCOM'], v_unit, rcli['VLRTOTAL']])
            
            total_geral = resumo_cli['VLRTOTAL'].sum()
            ws_aba.write_row(start_r + len(resumo_cli), 0, ['TOTAL GERAL', '', '', '', total_geral], formato_subtotal)
            ws_aba.set_column('D:E', 18, formato_moeda)

    return output.getvalue()
