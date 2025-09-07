# Script de ETL para o desafio BanVic - Preparação dos dados para o Power BI
# Autor: Nayara Vieira
# Data: 07/09/2025

import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def safe_date_conversion(date_series, column_name="data"):
    """
    Converte uma coluna de data para o formato datetime, tentando vários formatos.
    """
    print(f"  🔄 Processando {column_name}...")
    
    # Tenta converter a data de forma automática, que é mais rápido
    try:
        converted = pd.to_datetime(date_series, infer_datetime_format=True, errors='coerce')
        valid_count = converted.notna().sum()
        print(f"  ✅ {column_name}: {valid_count}/{len(date_series)} datas convertidas com sucesso")
        return converted
    except Exception as e:
        print(f"  ⚠️ Erro na conversão automática de {column_name}: {e}")
        
        # Se a conversão automática falhar, tenta na mão com os formatos mais comuns
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S UTC',
            '%Y-%m-%d %H:%M:%S.%f UTC', 
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            'mixed'
        ]
        
        for fmt in formats_to_try:
            try:
                if fmt == 'mixed':
                    converted = pd.to_datetime(date_series, format='mixed', errors='coerce')
                else:
                    converted = pd.to_datetime(date_series, format=fmt, errors='coerce')
                
                valid_count = converted.notna().sum()
                if valid_count > 0:
                    print(f"  ✅ {column_name}: {valid_count}/{len(date_series)} datas convertidas (formato: {fmt})")
                    return converted
            except Exception:
                continue
        
        print(f"  ❌ Não foi possível converter {column_name}. Mantendo como string.")
        return date_series

def load_banvic_data():
    """
    Função principal que carrega, limpa, junta e salva os dados do BanVic.
    """
    # Definindo os caminhos das pastas pra organizar o projeto
    base_path = Path(r"C:\Users\Nayara\Desktop\LH_EA_NAYARA_VIEIRA")
    data_path = base_path / "dados" / "raw" / "banvic_data"
    processed_path = base_path / "dados" / "processed"
    
    # Garante que a pasta de destino exista
    processed_path.mkdir(parents=True, exist_ok=True)
    
    print("🏦 Carregando dados do BanVic para Power BI...")
    print("="*60)
    
    # 1. Leitura dos arquivos CSV originais
    try:
        # Tabela Fato: transacoes.csv
        df_transacoes = pd.read_csv(data_path / "transacoes.csv")
        print(f"✅ Transações carregadas: {len(df_transacoes):,} registros")
        
        # Dimensões
        df_clientes = pd.read_csv(data_path / "clientes.csv")
        print(f"✅ Clientes carregados: {len(df_clientes):,} registros")
        
        df_agencias = pd.read_csv(data_path / "agencias.csv")
        print(f"✅ Agências carregadas: {len(df_agencias):,} registros")
        
        df_contas = pd.read_csv(data_path / "contas.csv")
        print(f"✅ Contas carregadas: {len(df_contas):,} registros")
        
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e}")
        return None
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None
    
    print("\n📅 PROCESSAMENTO DE DATAS")
    print("="*40)
    
    # 2. Tratamento da coluna de data_transacao
    df_transacoes['data_transacao'] = safe_date_conversion(
        df_transacoes['data_transacao'], 
        "data_transacao"
    )
    
    # O Power BI pode se confundir com timezone, melhor remover
    if pd.api.types.is_datetime64_any_dtype(df_transacoes['data_transacao']):
        if df_transacoes['data_transacao'].dt.tz is not None:
            df_transacoes['data_transacao'] = df_transacoes['data_transacao'].dt.tz_localize(None)
    
    # Checa se a data foi convertida antes de criar novas colunas
    if pd.api.types.is_datetime64_any_dtype(df_transacoes['data_transacao']):
        print("  🔧 Criando colunas derivadas de data...")
        
        # Quebrando a data em várias colunas para facilitar os filtros no PBI
        df_transacoes['ano'] = df_transacoes['data_transacao'].dt.year
        df_transacoes['mes'] = df_transacoes['data_transacao'].dt.month
        df_transacoes['dia'] = df_transacoes['data_transacao'].dt.day
        df_transacoes['dia_semana'] = df_transacoes['data_transacao'].dt.day_name()
        df_transacoes['mes_nome'] = df_transacoes['data_transacao'].dt.month_name()
        df_transacoes['trimestre'] = df_transacoes['data_transacao'].dt.quarter
        df_transacoes['semana_ano'] = df_transacoes['data_transacao'].dt.isocalendar().week
        
        # Traduzindo para português pra ficar mais fácil de ler no relatório
        dias_pt = {
            'Monday': 'Segunda-feira', 'Tuesday': 'Terça-feira', 
            'Wednesday': 'Quarta-feira', 'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        df_transacoes['dia_semana_pt'] = df_transacoes['dia_semana'].map(dias_pt).fillna(df_transacoes['dia_semana'])
        
        meses_pt = {
            'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
            'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
            'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
            'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
        }
        df_transacoes['mes_nome_pt'] = df_transacoes['mes_nome'].map(meses_pt).fillna(df_transacoes['mes_nome'])
        
        # Coluna para a análise de meses pares vs. ímpares
        df_transacoes['mes_tipo'] = df_transacoes['mes'].apply(
            lambda x: 'Par' if pd.notna(x) and x % 2 == 0 else 'Ímpar'
        )
        
    else:
        print("  ⚠️ Datas não foram convertidas. Pulando criação de colunas derivadas.")
    
    print("\n🔗 FAZENDO JOINS DOS DADOS")
    print("="*40)
    
    # 3. Juntando tudo em uma tabela só (modelo desnormalizado para o CSV final)
    try:
        # Transações <- Contas (para pegar cod_agencia e cod_cliente)
        df_transacoes_completo = df_transacoes.merge(
            df_contas[['num_conta', 'cod_agencia', 'cod_cliente']], 
            on='num_conta', 
            how='left'
        )
        print(f"✅ Join transações + contas: {len(df_transacoes_completo):,} registros")
        
        # Join com a tabela de clientes
        colunas_clientes = [col for col in ['cod_cliente', 'primeiro_nome', 'ultimo_nome', 'tipo_cliente', 'endereco'] 
                            if col in df_clientes.columns]
        
        df_transacoes_completo = df_transacoes_completo.merge(
            df_clientes[colunas_clientes], 
            on='cod_cliente', 
            how='left'
        )
        print(f"✅ Join + clientes: {len(df_transacoes_completo):,} registros")
        
        # Join com a tabela de agências
        colunas_agencias = [col for col in ['cod_agencia', 'nome', 'cidade', 'uf', 'tipo_agencia'] 
                            if col in df_agencias.columns]
        
        df_transacoes_completo = df_transacoes_completo.merge(
            df_agencias[colunas_agencias], 
            on='cod_agencia', 
            how='left',
            suffixes=('', '_agencia')
        )
        print(f"✅ Join + agências: {len(df_transacoes_completo):,} registros")
        
        # Renomeando colunas para evitar conflitos de nome e melhorar a clareza
        if 'nome' in df_transacoes_completo.columns:
            df_transacoes_completo = df_transacoes_completo.rename(columns={'nome': 'nome_agencia'})
        if 'endereco' in df_transacoes_completo.columns:
            df_transacoes_completo = df_transacoes_completo.rename(columns={'endereco': 'endereco_cliente'})
            
    except Exception as e:
        print(f"⚠️ Erro no join: {e}")
        df_transacoes_completo = df_transacoes.copy()
    
    print("\n📊 CRIANDO MÉTRICAS CALCULADAS")
    print("="*40)
    
    # 4. Criando algumas colunas calculadas direto no script
    try:
        # Criando faixas de valor pra facilitar a análise
        if 'valor_transacao' in df_transacoes_completo.columns:
            df_transacoes_completo['categoria_valor'] = pd.cut(
                df_transacoes_completo['valor_transacao'],
                bins=[0, 100, 500, 1000, 5000, float('inf')],
                labels=['Até R$ 100', 'R$ 101-500', 'R$ 501-1000', 'R$ 1001-5000', 'Acima de R$ 5000'],
                include_lowest=True
            )
            print("✅ Categoria de valor criada")
            
    except Exception as e:
        print(f"⚠️ Erro ao criar métricas: {e}")
    
    print("\n📅 CRIANDO DIMENSÃO DE DATAS")
    print("="*40)
    
    # 5. Criando a dim_datas separada (melhor prática de BI)
    if pd.api.types.is_datetime64_any_dtype(df_transacoes_completo['data_transacao']):
        try:
            # Pega a data mínima e máxima das transações pra criar o range
            data_min = df_transacoes_completo['data_transacao'].min()
            data_max = df_transacoes_completo['data_transacao'].max()
            
            print(f"  📅 Período: {data_min.date()} a {data_max.date()}")
            
            # Cria um range de todas as datas no período, sem faltar nenhuma
            datas_completas = pd.date_range(start=data_min.date(), end=data_max.date(), freq='D')
            
            # Monta o DataFrame da dimensão de datas
            dim_dates = pd.DataFrame({
                'data': datas_completas,
                'ano': datas_completas.year,
                'mes': datas_completas.month,
                'dia': datas_completas.day,
                'dia_semana': datas_completas.day_name(),
                'mes_nome': datas_completas.month_name(),
                'trimestre': datas_completas.quarter,
                'semana_ano': datas_completas.isocalendar().week,
                'dia_ano': datas_completas.dayofyear,
                'semestre': ((datas_completas.quarter + 1) // 2).astype(int)
            })
            
            # Traduz as colunas de data para português
            dim_dates['dia_semana_pt'] = dim_dates['dia_semana'].map(dias_pt)
            dim_dates['mes_nome_pt'] = dim_dates['mes_nome'].map(meses_pt)
            dim_dates['mes_tipo'] = dim_dates['mes'].apply(lambda x: 'Par' if x % 2 == 0 else 'Ímpar')
            
            print(f"✅ Dimensão de datas criada: {len(dim_dates):,} registros")
            
        except Exception as e:
            print(f"⚠️ Erro ao criar dimensão de datas: {e}")
            dim_dates = pd.DataFrame()
    else:
        print("⚠️ Não foi possível criar dimensão de datas (data_transacao não é datetime)")
        dim_dates = pd.DataFrame()
    
    print("\n💾 SALVANDO ARQUIVOS PARA POWER BI")
    print("="*40)
    
    # 6. Exportando os arquivos CSV que serão usados no Power BI
    try:
        # Tabela principal com tudo junto
        output_file = processed_path / "transacoes_powerbi.csv"
        df_transacoes_completo.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ {output_file.name}: {len(df_transacoes_completo):,} registros")
        
        # Dimensões separadas para montar o modelo estrela no PBI
        df_clientes.to_csv(processed_path / "dim_clientes.csv", index=False, encoding='utf-8-sig')
        print(f"✅ dim_clientes.csv: {len(df_clientes):,} registros")
        
        df_agencias.to_csv(processed_path / "dim_agencias.csv", index=False, encoding='utf-8-sig')
        print(f"✅ dim_agencias.csv: {len(df_agencias):,} registros")
        
        if not dim_dates.empty:
            dim_dates.to_csv(processed_path / "dim_datas.csv", index=False, encoding='utf-8-sig')
            print(f"✅ dim_datas.csv: {len(dim_dates):,} registros")
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivos: {e}")
        return None
    
    print("\n📈 CRIANDO RESUMOS EXECUTIVOS")
    print("="*40)
    
    # 7. Gerando alguns resumos pré-calculados (opcional, mas pode ser útil para validar)
    try:
        if 'dia_semana_pt' in df_transacoes_completo.columns and 'valor_transacao' in df_transacoes_completo.columns:
            # Resumo por dia da semana
            resumo_dias = df_transacoes_completo.groupby('dia_semana_pt').agg({
                'cod_transacao': 'count',
                'valor_transacao': ['sum', 'mean']
            }).round(2)
            resumo_dias.columns = ['Qtd_Transacoes', 'Volume_Total', 'Valor_Medio']
            resumo_dias.to_csv(processed_path / "resumo_dias_semana.csv", encoding='utf-8-sig')
            print("✅ resumo_dias_semana.csv")
        
        if 'mes_tipo' in df_transacoes_completo.columns:
            # Resumo por mês (par/ímpar)
            resumo_meses = df_transacoes_completo.groupby('mes_tipo').agg({
                'cod_transacao': 'count',
                'valor_transacao': ['sum', 'mean']
            }).round(2)
            resumo_meses.columns = ['Qtd_Transacoes', 'Volume_Total', 'Valor_Medio']
            resumo_meses.to_csv(processed_path / "resumo_meses_tipo.csv", encoding='utf-8-sig')
            print("✅ resumo_meses_tipo.csv")
        
        # Resumo por agência (últimos 6 meses)
        if pd.api.types.is_datetime64_any_dtype(df_transacoes_completo['data_transacao']):
            data_max = df_transacoes_completo['data_transacao'].max()
            data_corte = data_max - pd.DateOffset(months=6)
            dados_recentes = df_transacoes_completo[df_transacoes_completo['data_transacao'] >= data_corte]
            
            if 'cod_agencia' in dados_recentes.columns and len(dados_recentes) > 0:
                agencia_cols = ['cod_agencia']
                if 'nome_agencia' in dados_recentes.columns:
                    agencia_cols.append('nome_agencia')
                
                resumo_agencias = dados_recentes.groupby(agencia_cols).agg({
                    'cod_transacao': 'count',
                    'valor_transacao': ['sum', 'mean']
                }).round(2)
                resumo_agencias.columns = ['Qtd_Transacoes', 'Volume_Total', 'Valor_Medio']
                resumo_agencias = resumo_agencias.sort_values('Qtd_Transacoes', ascending=False)
                resumo_agencias.to_csv(processed_path / "resumo_agencias_6m.csv", encoding='utf-8-sig')
                print("✅ resumo_agencias_6m.csv")
                
    except Exception as e:
        print(f"⚠️ Erro ao criar resumos: {e}")
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("="*60)
    
    # Algumas estatísticas pra conferir no final
    if pd.api.types.is_datetime64_any_dtype(df_transacoes_completo['data_transacao']):
        data_min = df_transacoes_completo['data_transacao'].min()
        data_max = df_transacoes_completo['data_transacao'].max()
        print(f"📊 Período dos dados: {data_min.strftime('%d/%m/%Y')} a {data_max.strftime('%d/%m/%Y')}")
    
    print(f"💳 Total de transações: {len(df_transacoes_completo):,}")
    
    if 'valor_transacao' in df_transacoes_completo.columns:
        volume_total = df_transacoes_completo['valor_transacao'].sum()
        print(f"💰 Volume total: R$ {volume_total:,.2f}")
    
    print(f"👥 Total de clientes: {len(df_clientes):,}")
    print(f"🏢 Total de agências: {len(df_agencias):,}")
    
    print(f"\n📁 Arquivos criados em: {processed_path}")
    print("  - transacoes_powerbi.csv (arquivo principal)")
    print("  - dim_clientes.csv")
    print("  - dim_agencias.csv") 
    if not dim_dates.empty:
        print("  - dim_datas.csv")
    print("  - resumo_dias_semana.csv")
    print("  - resumo_meses_tipo.csv")
    print("  - resumo_agencias_6m.csv")
    print("="*60)
    
    return df_transacoes_completo

# Bloco principal para rodar o script todo
if __name__ == "__main__":
    print("🚀 INICIANDO INTEGRAÇÃO BANVIC + POWER BI")
    print("="*60)
    
    try:
        dados = load_banvic_data()
        if dados is not None:
            print("\n🎉 SUCESSO! Dados prontos para importação no Power BI")
        else:
            print("\n❌ FALHA no processamento dos dados")
    except Exception as e:
        print(f"\n❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()