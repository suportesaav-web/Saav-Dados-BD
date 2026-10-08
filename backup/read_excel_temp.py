import pandas as pd

file1_path = r"C:\Users\SAAV054\Documents\Desenvolvimento\Saav-Dados-BD\docs\arquivo (8).xlsx"

for skip in range(5):
    try:
        df1 = pd.read_excel(file1_path, skiprows=skip, nrows=0)
        print(f"--- file 1: arquivo (8).xlsx (skiprows={skip}) ---")
        print(df1.columns.tolist())
    except Exception as e:
        pass
