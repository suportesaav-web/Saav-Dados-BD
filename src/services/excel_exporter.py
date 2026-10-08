import io
import pandas as pd
from src.config.settings import PRIMARY_COLOR, SECONDARY_COLOR, BG_CARD_COLOR

def gerar_planilha_consolidada(df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
        formato_cabecalho = workbook.add_format({
            'bold': True, 'bg_color': PRIMARY_COLOR, 'font_color': 'white', 'border': 1
        })
        formato_subtotal = workbook.add_format({'bold': True, 'bg_color': BG_CARD_COLOR, 'border': 1})
        formato_total_geral = workbook.add_format({'bold': True, 'bg_color': SECONDARY_COLOR, 'font_color': 'white', 'border': 1})
        formato_cabecalho_aba = workbook.add_format({'bold': True, 'bg_color': SECONDARY_COLOR, 'font_color': 'white', 'border': 1})
        
        # 1. ABA RESUMO
        df_resumo_export = df.groupby(['ABA_DESTINO', 'REFPROD', 'DESCRICAO']).agg({
            'SIGLA_RESUMO': 'first',
            'QTDCOM': 'sum',
            'VLRTOTAL': 'sum'
        }).reset_index()
        
        df_resumo_export = df_resumo_export.sort_values(by=['ABA_DESTINO', 'REFPROD'])
        linhas_resumo = []
        total_geral_venda = 0.0

        for destino, group in df_resumo_export.groupby('ABA_DESTINO', sort=False):
            subtotal_venda = 0.0
            for _, row in group.iterrows():
                vlr_unit_venda = row['VLRTOTAL'] / row['QTDCOM'] if row['QTDCOM'] > 0 else 0
                linhas_resumo.append([
                    row['SIGLA_RESUMO'], 
                    row['REFPROD'], 
                    row['DESCRICAO'], 
                    row['QTDCOM'], 
                    vlr_unit_venda, 
                    f'=D{len(linhas_resumo)+2}*E{len(linhas_resumo)+2}' # Excel formula
                ])
                subtotal_venda += row['VLRTOTAL']
            
            # Using formulas for subtotals is tricky since we'd need to know the range, so we just put the python sum, or a SUM formula.
            # Let's stick to the python calculated sum for subtotals, or SUM(range).
            linhas_resumo.append(['', f'TOTAL ACUMULADO {destino}', '', '', '', subtotal_venda])
            total_geral_venda += subtotal_venda
        
        linhas_resumo.append(['', 'TOTAL GERAL CONSOLIDADO', '', '', '', total_geral_venda])
            
        df_excel_resumo = pd.DataFrame(linhas_resumo, columns=[
            'Aba Destino', 'Ref Prod', 'Descrição', 'Qtd Com', 'VLR UNIT', 'VLR TOTAL'
        ])
        
        df_excel_resumo.to_excel(writer, sheet_name='RESUMO', index=False)
        ws_resumo = writer.sheets['RESUMO']
        ws_resumo.set_column('A:B', 16)
        ws_resumo.set_column('C:C', 36)
        ws_resumo.set_column('D:D', 12)
        ws_resumo.set_column('E:F', 18, formato_moeda)
        
        for col_num, value in enumerate(df_excel_resumo.columns.values):
            ws_resumo.write(0, col_num, value, formato_cabecalho)
        
        for row_num, row_data in enumerate(linhas_resumo):
            txt = str(row_data[1])
            if 'TOTAL GERAL CONSOLIDADO' in txt:
                ws_resumo.write_row(row_num + 1, 0, row_data, formato_total_geral)
            elif 'TOTAL ACUMULADO' in txt:
                ws_resumo.write_row(row_num + 1, 0, row_data, formato_subtotal)
            else:
                # Write row data up to column E
                ws_resumo.write_row(row_num + 1, 0, row_data[:5])
                # Write formula for column F
                ws_resumo.write_formula(row_num + 1, 5, row_data[5], formato_moeda)
        
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
            
            import re
            nome_sheet = re.sub(r'[\\\\*?:/\\[\\]]', '', str(aba))[:31].strip()
            if not nome_sheet: nome_sheet = 'CLIENTE_DESCONHECIDO'
            
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
                row_idx = start_r + idx
                # Write data columns
                ws_aba.write_row(row_idx, 0, [rcli['REFPROD'], rcli['DESCRICAO'], rcli['QTDCOM'], v_unit])
                # Write formula for total
                ws_aba.write_formula(row_idx, 4, f'=C{row_idx+1}*D{row_idx+1}')
            
            total_geral = resumo_cli['VLRTOTAL'].sum()
            ws_aba.write_row(start_r + len(resumo_cli), 0, ['TOTAL GERAL', '', '', '', total_geral], formato_subtotal)
            ws_aba.set_column('D:E', 18, formato_moeda)

    return output.getvalue()
