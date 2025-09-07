# Ferramenta de diagnóstico e correção de CSVs para o Desafio BanVic
# Autor: Nayara Vieira

import pandas as pd
import os
import numpy as np
from datetime import datetime

def diagnosticar_arquivos():
    """Faz uma varredura na pasta do projeto para encontrar os arquivos CSV."""
    
    print("🔍 DIAGNÓSTICO DO PROJETO")
    print("="*50)
    
    # Varre o diretório atual e todas as subpastas atrás de arquivos .csv
    csv_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    print(f"📁 Pasta atual: {os.path.abspath('.')}")
    print(f"📄 Arquivos CSV encontrados: {len(csv_files)}")
    
    for file in csv_files:
        print(f"   📎 {file}")
    
    # Checa se a estrutura de pastas que o script principal espera está no lugar
    expected_path = 'dados/raw/banvic_data/'
    print(f"\n📂 Estrutura esperada: {os.path.abspath(expected_path)}")
    print(f"📂 Existe? {os.path.exists(expected_path)}")
    
    return csv_files

def analisar_csv(file_path):
    """Abre um CSV, lê as primeiras linhas e mostra um resumo das colunas."""
    
    print(f"\n🔍 ANALISANDO: {file_path}")
    print("-" * 40)
    
    try:
        # Lendo só o comecinho do arquivo pra não carregar tudo na memória
        df = pd.read_csv(file_path, nrows=5)
        
        print(f"📊 Colunas: {list(df.columns)}")
        print(f"📏 Tamanho da amostra: {df.shape}")
        
        # Procura por colunas que parecem ser de data e mostra uns exemplos
        date_columns = [col for col in df.columns if 'data' in col.lower() or 'date' in col.lower()]
        
        for date_col in date_columns:
            print(f"\n📅 Coluna de data encontrada: {date_col}")
            sample_dates = df[date_col].dropna().head(3).tolist()
            print(f"📋 Exemplos de datas:")
            for date in sample_dates:
                print(f"   {date}")
                
        return df.columns.tolist()
        
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")
        return []

def corrigir_formato_data(file_path, date_column, output_path=None):
    """Tenta corrigir formatos de data 'quebrados' em um arquivo CSV completo."""
    
    print(f"\n🔧 CORRIGINDO DATAS: {file_path}")
    print("-" * 40)
    
    try:
        # Dessa vez, carrega o arquivo inteiro pra valer
        df = pd.read_csv(file_path)
        print(f"📊 Registros carregados: {len(df)}")
        
        if date_column not in df.columns:
            print(f"❌ Coluna '{date_column}' não encontrada!")
            return False
        
        # Minha função para tentar arrumar a bagunça das datas
        def clean_date(date_str):
            if pd.isna(date_str):
                return pd.NaT
            
            try:
                # Garante que é string pra poder manipular
                date_str = str(date_str)
                
                # O formato com 'UTC' e microssegundos costuma dar problema, então limpo ele
                if '.' in date_str and 'UTC' in date_str:
                    date_part = date_str.split('.')[0]
                    date_str = date_part + ' UTC'
                
                # Tenta a conversão
                return pd.to_datetime(date_str, utc=True)
                
            except Exception as e:
                print(f"⚠️ Erro ao processar data '{date_str}': {e}")
                return pd.NaT
        
        # Aplica a função de limpeza na coluna
        print("🔄 Processando datas...")
        original_count = len(df)
        df[date_column] = df[date_column].apply(clean_date)
        
        # Joga fora as linhas que não foi possível converter
        df = df.dropna(subset=[date_column])
        final_count = len(df)
        
        print(f"✅ Datas processadas!")
        print(f"📊 Registros originais: {original_count}")
        print(f"📊 Registros válidos: {final_count}")
        print(f"📊 Registros removidos: {original_count - final_count}")
        
        # Salva uma nova versão do arquivo com o sufixo _corrigido
        if output_path is None:
            output_path = file_path.replace('.csv', '_corrigido.csv')
        
        df.to_csv(output_path, index=False)
        print(f"💾 Arquivo salvo: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir arquivo: {e}")
        return False

def criar_estrutura_pastas():
    """Garante que as pastas /dados/raw e /dados/processed existam."""
    
    print("\n📁 CRIANDO ESTRUTURA DE PASTAS")
    print("="*40)
    
    folders = [
        'dados',
        'dados/raw',
        'dados/raw/banvic_data',
        'dados/processed'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ {folder}/")
    
    print("✅ Estrutura criada com sucesso!")

def mover_csvs_para_estrutura():
    """Pega os CSVs da raiz do projeto e copia para dados/raw/banvic_data."""
    
    print("\n🚚 ORGANIZANDO ARQUIVOS CSV")
    print("="*40)
    
    target_dir = 'dados/raw/banvic_data/'
    
    # Procura arquivos CSV soltos na pasta principal
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("ℹ️ Nenhum arquivo CSV encontrado na pasta atual")
        return
    
    for csv_file in csv_files:
        source = csv_file
        destination = os.path.join(target_dir, csv_file)
        
        try:
            # Copiando em vez de mover, pra ter um backup do original
            import shutil
            shutil.copy2(source, destination)
            print(f"📋 Copiado: {source} → {destination}")
        except Exception as e:
            print(f"❌ Erro ao copiar {source}: {e}")

def main():
    """Orquestra todo o processo: diagnostica, organiza e corrige os arquivos."""
    
    print("🛠️ FERRAMENTA DE CORREÇÃO - DASHBOARD BANVIC")
    print("="*55)
    
    # Passo 1: Vê o que tem de arquivo na pasta
    csv_files = diagnosticar_arquivos()
    
    # Passo 2: Cria as pastas se precisar
    criar_estrutura_pastas()
    
    # Passo 3: Move os arquivos pra pasta certa
    if csv_files:
        mover_csvs_para_estrutura()
    
    # Passo 4: Analisa cada arquivo encontrado
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            columns = analisar_csv(csv_file)
            
            # Se o arquivo parece ter datas, tenta aplicar a correção
            date_columns = [col for col in columns if 'data' in col.lower() or 'date' in col.lower()]
            
            if date_columns:
                print(f"\n🔧 Tentando corrigir as datas em {csv_file}...")
                for date_col in date_columns:
                    try:
                        corrigir_formato_data(csv_file, date_col)
                    except Exception as e:
                        print(f"❌ Erro ao corrigir {date_col}: {e}")
    
    print("\n" + "="*55)
    print("✅ CORREÇÃO CONCLUÍDA!")
    print("💡 PRÓXIMOS PASSOS:")
    print("1. Execute o script principal de análise/ETL novamente")
    print("2. Verifique os logs acima para ver se algo deu errado")
    print("3. Considere usar os arquivos '_corrigido.csv' se foram criados")

# Ponto de entrada do script
if __name__ == "__main__":
    main()