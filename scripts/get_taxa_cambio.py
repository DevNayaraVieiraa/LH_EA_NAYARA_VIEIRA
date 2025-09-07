# Script para buscar a cotação do Dólar via API do Banco Central do Brasil (BCB)
# Autor: Nayara Vieira

import pandas as pd
import requests
from datetime import datetime, timedelta

print("Buscando dados de taxa de câmbio do Banco Central...")

# Endpoint da API do BCB para a série histórica do dólar comercial (código 1)
url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados"

try:
    # Manda o GET request para a URL
    response = requests.get(url)
    data = response.json()
    
    # O JSON vem numa lista de dicionários, o pandas converte isso fácil
    df_cambio = pd.DataFrame(data)
    df_cambio['data'] = pd.to_datetime(df_cambio['data'], format='%d/%m/%Y')
    df_cambio['valor'] = pd.to_numeric(df_cambio['valor'])
    
    # Filtrando para o período que importa para o desafio
    df_cambio = df_cambio[df_cambio['data'] >= '2023-01-01']
    df_cambio = df_cambio[df_cambio['data'] <= '2024-12-31']
    
    # Renomeando as colunas pra ficar mais fácil de usar no Power BI
    df_cambio = df_cambio.rename(columns={
        'data': 'data_cambio',
        'valor': 'taxa_usd_brl'
    })
    
    # Salva o resultado num arquivo CSV
    df_cambio.to_csv('taxa_cambio_bcb.csv', index=False)
    
    print(f"Arquivo criado com sucesso!")
    print(f"Período: {df_cambio['data_cambio'].min()} a {df_cambio['data_cambio'].max()}")
    print(f"Total de registros: {len(df_cambio)}")
    print("\nPrimeiras linhas:")
    print(df_cambio.head())
    
except Exception as e:
    # Bloco de segurança: se a API falhar ou estiver fora do ar, cria um arquivo de exemplo
    print(f"Erro ao buscar dados: {e}")
    print("Criando dados de exemplo...")
    
    # Criando dados mockados (fake) só para o dashboard não quebrar
    dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
    valores = [5.2 + (i % 100) * 0.01 for i in range(len(dates))]
    
    df_exemplo = pd.DataFrame({
        'data_cambio': dates,
        'taxa_usd_brl': valores
    })
    
    df_exemplo.to_csv('taxa_cambio_bcb.csv', index=False)
    print("Arquivo de exemplo criado!")