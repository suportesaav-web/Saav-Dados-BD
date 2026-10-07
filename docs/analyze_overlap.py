import pandas as pd

file1_path = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\docs\arquivo (8).xlsx"
file2_path = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\docs\Itens de venda por cliente AAD__.xlsx"

try:
    df_vendas = pd.read_excel(file1_path, skiprows=2)
    df_fornecedor = pd.read_excel(file2_path)

    print(f"Total registros Vendas: {len(df_vendas)}")
    print(f"Total registros Fornecedor (Tabela): {len(df_fornecedor)}")
    
    # Let's check overlaps
    # Clean the CNPJ to be string
    df_vendas['CNPJ_str'] = df_vendas['CNPJ_PARCEIRO'].astype(str).str.replace(r'\D', '', regex=True)
    df_fornecedor['CNPJ_str'] = df_fornecedor['CNPJ_PARCEIRO'].astype(str).str.replace(r'\D', '', regex=True)
    
    # Clean Ref Prod
    df_vendas['Ref Prod_str'] = df_vendas['Ref Prod'].astype(str).str.strip()
    df_fornecedor['Ref Prod_str'] = df_fornecedor['Ref Prod'].astype(str).str.strip()
    
    # Overlap by CNPJ
    cnpjs_vendas = set(df_vendas['CNPJ_str'].unique())
    cnpjs_fornecedor = set(df_fornecedor['CNPJ_str'].unique())
    print(f"CNPJs únicos Vendas: {len(cnpjs_vendas)}")
    print(f"CNPJs únicos Fornecedor: {len(cnpjs_fornecedor)}")
    print(f"CNPJs em comum: {len(cnpjs_vendas.intersection(cnpjs_fornecedor))}")
    
    # Overlap by Ref Prod
    refs_vendas = set(df_vendas['Ref Prod_str'].unique())
    refs_fornecedor = set(df_fornecedor['Ref Prod_str'].unique())
    print(f"Ref Prod únicos Vendas: {len(refs_vendas)}")
    print(f"Ref Prod únicos Fornecedor: {len(refs_fornecedor)}")
    print(f"Ref Prod em comum: {len(refs_vendas.intersection(refs_fornecedor))}")
    
    # Merge trying to match both CNPJ and Ref Prod
    df_merge = pd.merge(
        df_vendas, 
        df_fornecedor, 
        how='inner', 
        left_on=['CNPJ_str', 'Ref Prod_str'], 
        right_on=['CNPJ_str', 'Ref Prod_str'],
        suffixes=('_vendas', '_fornecedor')
    )
    print(f"\nRegistros com match exato de CNPJ e Ref Prod: {len(df_merge)}")

except Exception as e:
    print(f"Error: {e}")
