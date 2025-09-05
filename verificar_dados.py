import os
import pandas as pd

# Verifica quais arquivos existem
print("Arquivos na pasta atual:")
for arquivo in os.listdir('.'):
    if arquivo.endswith('.csv'):
        print(f"  ✅ {arquivo}")

# Tenta carregar os CSVs
try:
    df_agencias = pd.read_csv('tb_agencias.csv')
    df_clientes = pd.read_csv('tb_clientes.csv')
    df_transacoes = pd.read_csv('tb_transacoes.csv')
    
    print("\n✅ Dados carregados com sucesso!")
    print(f"Agências: {len(df_agencias)} registros")
    print(f"Clientes: {len(df_clientes)} registros")
    print(f"Transações: {len(df_transacoes)} registros")
    
except FileNotFoundError as e:
    print(f"\n❌ Erro: {e}")
    print("Certifique-se de que os arquivos CSV estão na pasta")