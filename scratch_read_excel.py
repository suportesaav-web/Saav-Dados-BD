import pandas as pd
from src.services.table_service import ler_arquivo_tabela

class DummyFile:
    def __init__(self, path):
        self.name = path
        with open(path, 'rb') as f:
            self.content = f.read()
    def read(self):
        return self.content
    def seek(self, pos): pass
    def getvalue(self): return self.content

try:
    df = ler_arquivo_tabela(DummyFile('docs/arquivo (8).xlsx'))
    print("Colunas:")
    print(df.columns.tolist())
    print("\nAmostra:")
    print(df[['Cod. Parc', 'CNPJ_PARCEIRO']].head())
except Exception as e:
    print(e)
