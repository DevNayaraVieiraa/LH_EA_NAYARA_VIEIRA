import pandas as pd
import os
import numpy as np
from datetime import datetime

def diagnosticar_arquivos():
    """Diagnostica os arquivos CSV e a estrutura do projeto"""
    
    print("🔍 DIAGNÓSTICO DO PROJETO")
    print("="*50)
    
    # Lista todos os arquivos CSV na pasta atual e subpastas
    csv_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.csv'):
                csv_files.append(os.path.join(root, file))
    
    print(f"📁 Pasta atual: {os.path.abspath('.')}")
    print(f"📄 Arquivos CSV encontrados: {len(csv_files)}")
    
    for file in csv_files:
        print(f"   📎 {file}")
    
    # Verifica a estrutura esperada
    expected_path = 'dados/raw/banvic_data/'
    print(f"\n📂 Estrutura esperada: {os.path.abspath(expected_path)}")
    print(f"📂 Existe? {os.path.exists(expected_path)}")
    
    return csv_files

def analisar_csv(file_path):
    """Analisa um arquivo CSV específico"""
    
    print(f"\n🔍 ANALISANDO: {file_path}")
    print("-" * 40)
    
    try:
        # Carrega apenas as primeiras linhas para análise
        df = pd.read_csv(file_path, nrows=5)
        
        print(f"📊 Colunas: {list(df.columns)}")
        print(f"📏 Tamanho da amostra: {df.shape}")
        
        # Se tiver coluna de data, analisa o formato
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
    """Corrige o formato da data em um arquivo CSV"""
    
    print(f"\n🔧 CORRIGINDO DATAS: {file_path}")
    print("-" * 40)
    
    try:
        # Carrega o arquivo
        df = pd.read_csv(file_path)
        print(f"📊 Registros carregados: {len(df)}")
        
        if date_column not in df.columns:
            print(f"❌ Coluna '{date_column}' não encontrada!")
            return False
        
        # Função para limpar e converter datas
        def clean_date(date_str):
            if pd.isna(date_str):
                return pd.NaT
            
            try:
                # Converte para string se não for
                date_str = str(date_str)
                
                # Remove microssegundos problemáticos
                if '.' in date_str and 'UTC' in date_str:
                    # Pega apenas até os segundos
                    date_part = date_str.split('.')[0]
                    # Adiciona UTC de volta
                    date_str = date_part + ' UTC'
                
                # Tenta converter
                return pd.to_datetime(date_str, utc=True)
                
            except Exception as e:
                print(f"⚠️ Erro ao processar data '{date_str}': {e}")
                return pd.NaT
        
        # Aplica a correção
        print("🔄 Processando datas...")
        original_count = len(df)
        df[date_column] = df[date_column].apply(clean_date)
        
        # Remove registros com datas inválidas
        df = df.dropna(subset=[date_column])
        final_count = len(df)
        
        print(f"✅ Datas processadas!")
        print(f"📊 Registros originais: {original_count}")
        print(f"📊 Registros válidos: {final_count}")
        print(f"📊 Registros removidos: {original_count - final_count}")
        
        # Salva o arquivo corrigido
        if output_path is None:
            output_path = file_path.replace('.csv', '_corrigido.csv')
        
        df.to_csv(output_path, index=False)
        print(f"💾 Arquivo salvo: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir arquivo: {e}")
        return False

def criar_estrutura_pastas():
    """Cria a estrutura de pastas necessária"""
    
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
    """Move arquivos CSV para a estrutura correta"""
    
    print("\n🚚 ORGANIZANDO ARQUIVOS CSV")
    print("="*40)
    
    target_dir = 'dados/raw/banvic_data/'
    
    # Encontra CSVs na raiz
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("ℹ️ Nenhum arquivo CSV encontrado na pasta atual")
        return
    
    for csv_file in csv_files:
        source = csv_file
        destination = os.path.join(target_dir, csv_file)
        
        try:
            # Copia o arquivo (mantém o original)
            import shutil
            shutil.copy2(source, destination)
            print(f"📋 Copiado: {source} → {destination}")
        except Exception as e:
            print(f"❌ Erro ao copiar {source}: {e}")

def main():
    """Função principal de correção"""
    
    print("🛠️ FERRAMENTA DE CORREÇÃO - DASHBOARD BANVIC")
    print("="*55)
    
    # 1. Diagnostica arquivos
    csv_files = diagnosticar_arquivos()
    
    # 2. Cria estrutura se não existir
    criar_estrutura_pastas()
    
    # 3. Move CSVs se necessário
    if csv_files:
        mover_csvs_para_estrutura()
    
    # 4. Analisa cada CSV encontrado
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            columns = analisar_csv(csv_file)
            
            # Se encontrar colunas de data, oferece correção
            date_columns = [col for col in columns if 'data' in col.lower() or 'date' in col.lower()]
            
            if date_columns:
                print(f"\n🔧 Deseja corrigir as datas em {csv_file}?")
                for date_col in date_columns:
                    try:
                        corrigir_formato_data(csv_file, date_col)
                    except Exception as e:
                        print(f"❌ Erro ao corrigir {date_col}: {e}")
    
    print("\n" + "="*55)
    print("✅ CORREÇÃO CONCLUÍDA!")
    print("💡 PRÓXIMOS PASSOS:")
    print("1. Execute o dashboard novamente")
    print("2. Se ainda houver erros, verifique os logs acima")
    print("3. Considere usar os arquivos '_corrigido.csv' se foram criados")

if __name__ == "__main__":
    main()