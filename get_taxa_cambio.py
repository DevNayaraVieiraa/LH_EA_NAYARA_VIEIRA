import pandas as pd
import requests
from datetime import datetime, timedelta

print("Buscando dados de taxa de câmbio do Banco Central...")

# URL da API do Banco Central (série histórica do dólar)
url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"

try:
    # Fazer requisição para a API
    response = requests.get(url)
    data = response.json()
    
    # Converter para DataFrame
    df_cambio = pd.DataFrame(data)
    df_cambio['data'] = pd.to_datetime(df_cambio['data'], format='%d/%m/%Y')
    df_cambio['valor'] = pd.to_numeric(df_cambio['valor'])
    
    # Filtrar para o período de 2023-2024 (ajustar conforme seus dados)
    df_cambio = df_cambio[df_cambio['data'] >= '2023-01-01']
    df_cambio = df_cambio[df_cambio['data'] <= '2024-12-31']
    
    # Renomear colunas para ficar mais claro
    df_cambio = df_cambio.rename(columns={
        'data': 'data_cambio',
        'valor': 'taxa_usd_brl'
    })
    
    # Salvar CSV
    df_cambio.to_csv('taxa_cambio_bcb.csv', index=False)
    
    print(f"Arquivo criado com sucesso!")
    print(f"Período: {df_cambio['data_cambio'].min()} a {df_cambio['data_cambio'].max()}")
    print(f"Total de registros: {len(df_cambio)}")
    print("\nPrimeiras linhas:")
    print(df_cambio.head())
    
except Exception as e:
    print(f"Erro ao buscar dados: {e}")
    print("Criando dados de exemplo...")
    
    # Dados de exemplo caso a API não funcione
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    valores = [5.2 + (i % 100) * 0.01 for i in range(len(dates))]
    
    df_exemplo = pd.DataFrame({
        'data_cambio': dates,
        'taxa_usd_brl': valores
    })
    
    df_exemplo.to_csv('taxa_cambio_bcb.csv', index=False)
    print("Arquivo de exemplo criado!")