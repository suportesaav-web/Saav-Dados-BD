import pandas as pd

# Paths
file_vendas = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\docs\arquivo (8).xlsx"
file_compras = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\docs\Itens de venda por cliente AAD__.xlsx"
file_output = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\docs\Relatorio_Vendas_Compras.xlsx"

# 1. Carregar os dados (Vendas pula as 2 primeiras linhas)
df_vendas = pd.read_excel(file_vendas, skiprows=2)
df_compras = pd.read_excel(file_compras)

# 2. Limpar e padronizar as colunas chave (CNPJ e Ref Prod)
def clean_cnpj(val):
    if pd.isna(val): return ""
    s = str(val).replace('.0', '').strip()
    import re
    s = re.sub(r'\D', '', s)
    return s.zfill(14) if s else ""

df_vendas['CNPJ_Limpo'] = df_vendas['CNPJ_PARCEIRO'].apply(clean_cnpj)
df_compras['CNPJ_Limpo'] = df_compras['CNPJ_PARCEIRO'].apply(clean_cnpj)

# Limpar Ref Prod (Item / REFORN)
df_vendas['Ref_Prod_Limpo'] = df_vendas['Ref Prod'].astype(str).str.strip().str.upper()
df_compras['Ref_Prod_Limpo'] = df_compras['Ref Prod'].astype(str).str.strip().str.upper()

# 3. Agrupar Vendas por Cliente e Item para somar as quantidades
# Colunas que identificam o cliente: CNPJ_PARCEIRO, Razão Social
# Colunas do item: Ref Prod, Descrição
vendas_agrupado = df_vendas.groupby(
    ['CNPJ_Limpo', 'Razão Social', 'Ref_Prod_Limpo', 'Descrição'], 
    as_index=False
)['Qtd Com'].sum()

# 4. Preparar tabela de compras (remover duplicatas de CNPJ + Ref Prod, se houver, pegando a primeira)
# Vamos trazer as colunas de interesse: Preço unitário (sem IPI), Preços (com IPI), e TABELA (Coluna E)
colunas_compras = ['CNPJ_Limpo', 'Ref_Prod_Limpo', 'TABELA', 
                   'Preço unitário\n(sem IPI) FY 26', 'Preços (com IPI) FY 26']
compras_dedup = df_compras[colunas_compras].drop_duplicates(subset=['CNPJ_Limpo', 'Ref_Prod_Limpo'], keep='first')

# 5. Fazer o merge (DE/PARA) entre Vendas (agrupado) e Compras
df_relatorio = pd.merge(
    vendas_agrupado,
    compras_dedup,
    on=['CNPJ_Limpo', 'Ref_Prod_Limpo'],
    how='left' # Mantém todas as vendas e traz a compra se der match no Cliente e Item
)

# 6. Renomear/Organizar as colunas finais
df_relatorio.rename(columns={
    'CNPJ_Limpo': 'CNPJ',
    'Ref_Prod_Limpo': 'REFORN (Item)',
    'Qtd Com': 'Qtd Vendida',
    'TABELA': 'Tabela de Compra (Campo E)',
    'Preço unitário\n(sem IPI) FY 26': 'Valor Compra (Sem IPI)',
    'Preços (com IPI) FY 26': 'Valor Compra (Com IPI)'
}, inplace=True)

df_relatorio = df_relatorio[['CNPJ', 'Razão Social', 'REFORN (Item)', 'Descrição', 'Qtd Vendida', 
                             'Tabela de Compra (Campo E)', 'Valor Compra (Sem IPI)', 'Valor Compra (Com IPI)']]

# 7. Salvar em Excel
df_relatorio.to_excel(file_output, index=False)
print(f"Relatório gerado com sucesso em: {file_output}")
print(f"Total de linhas no relatório (Vendas agrupadas): {len(df_relatorio)}")
matches = df_relatorio['Valor Compra (Sem IPI)'].notna().sum()
print(f"Linhas com match (Encontrou preço de compra para o mesmo cliente e item): {matches}")
