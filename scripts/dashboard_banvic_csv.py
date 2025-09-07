import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

class BanVicDashboard:
    def __init__(self, data_path='dados/raw/banvic_data/'):
        self.data_path = data_path
        self.df_transacoes = None
        self.df_clientes = None
        self.df_agencias = None
        self.dim_dates = None
        
        print("============================================================")
        print("🏦 DASHBOARD BANVIC - ANÁLISE DE DADOS")
        print("============================================================")
        
        self.load_data()

    def load_data(self):
        """Carrega os dados CSV"""
        print("\n📂 Carregando dados...")
        
        try:
            # Carrega transações (arquivo principal)
            print("📊 Carregando transações...")
            self.df_transacoes = pd.read_csv(f'{self.data_path}transacoes.csv')
            print("✅ Transações carregadas!")
            
            # Carrega outros arquivos se existirem
            if os.path.exists(f'{self.data_path}clientes.csv'):
                self.df_clientes = pd.read_csv(f'{self.data_path}clientes.csv')
                print("✅ Clientes carregados!")
            
            if os.path.exists(f'{self.data_path}agencias.csv'):
                self.df_agencias = pd.read_csv(f'{self.data_path}agencias.csv')
                print("✅ Agências carregadas!")
            
            # Processa as datas IMEDIATAMENTE após carregar
            self.processar_datas()
            
            # Tenta carregar dim_dates, se não existir, cria
            try:
                self.dim_dates = pd.read_csv(f'{self.data_path}dim_dates.csv')
                print("✅ Dimensão de datas carregada!")
            except FileNotFoundError:
                print("⚠️ dim_dates.csv não encontrado - criando...")
                self.create_dim_dates()
                
        except FileNotFoundError as e:
            print(f"❌ Erro ao carregar dados: {e}")
            print("📁 Verifique se os arquivos estão no caminho:")
            print(f"   {os.path.abspath(self.data_path)}")
            raise
        
        print("✅ Dados CSV carregados com sucesso!")

    def processar_datas(self):
        """Processa e corrige todas as datas dos DataFrames"""
        print("🔄 Processando datas...")
        
        # Função universal para corrigir datas
        def corrigir_data(date_str):
            if pd.isna(date_str):
                return pd.NaT
            
            try:
                date_str = str(date_str)
                
                # Remove microssegundos se existirem
                if '.' in date_str and 'UTC' in date_str:
                    date_str = date_str.split('.')[0] + ' UTC'
                
                # Converte para datetime
                return pd.to_datetime(date_str, utc=True)
                
            except Exception:
                return pd.NaT
        
        # Processa transações
        if self.df_transacoes is not None and 'data_transacao' in self.df_transacoes.columns:
            original_count = len(self.df_transacoes)
            self.df_transacoes['data_transacao'] = self.df_transacoes['data_transacao'].apply(corrigir_data)
            self.df_transacoes = self.df_transacoes.dropna(subset=['data_transacao'])
            
            # Converte para timezone do Brasil
            self.df_transacoes['data_transacao'] = self.df_transacoes['data_transacao'].dt.tz_convert('America/Sao_Paulo')
            
            final_count = len(self.df_transacoes)
            if original_count > final_count:
                print(f"⚠️ Removidas {original_count - final_count} transações com datas inválidas")
        
        # Processa clientes
        if self.df_clientes is not None:
            for col in ['data_inclusao', 'data_nascimento']:
                if col in self.df_clientes.columns:
                    self.df_clientes[col] = self.df_clientes[col].apply(corrigir_data)
        
        print("✅ Datas processadas!")

    def create_dim_dates(self):
        """Cria a dimensão de datas"""
        if self.df_transacoes is None:
            print("❌ Não é possível criar dim_dates sem dados de transações")
            return
            
        print("📅 Criando dimensão de datas...")
        
        # Cria range de datas
        min_date = self.df_transacoes['data_transacao'].min()
        max_date = self.df_transacoes['data_transacao'].max()
        
        print(f"📅 Período dos dados: {min_date.strftime('%d/%m/%Y')} a {max_date.strftime('%d/%m/%Y')}")
        
        # Cria a dimensão
        date_range = pd.date_range(start=min_date.date(), end=max_date.date(), freq='D')
        
        self.dim_dates = pd.DataFrame({
            'data': date_range,
            'ano': date_range.year,
            'mes': date_range.month,
            'dia': date_range.day,
            'dia_semana': date_range.dayofweek + 1,
            'nome_dia_semana': date_range.day_name(),
            'nome_mes': date_range.month_name(),
            'trimestre': date_range.quarter,
            'eh_fim_semana': (date_range.dayofweek >= 5).astype(int),
            'eh_mes_par': (date_range.month % 2 == 0).astype(int)
        })
        
        # Salva a dimensão
        self.dim_dates.to_csv(f'{self.data_path}dim_dates.csv', index=False)
        print("✅ Dimensão de datas criada e salva!")

    def show_data_info(self):
        """Mostra informações básicas dos dados"""
        print("\n📊 INFORMAÇÕES DOS DADOS")
        print("="*50)
        
        if self.df_transacoes is not None:
            print(f"💳 Transações: {len(self.df_transacoes):,} registros")
            
            # Verifica se a data é datetime
            if pd.api.types.is_datetime64_any_dtype(self.df_transacoes['data_transacao']):
                min_date = self.df_transacoes['data_transacao'].min().strftime('%d/%m/%Y')
                max_date = self.df_transacoes['data_transacao'].max().strftime('%d/%m/%Y')
                print(f"📅 Período: {min_date} a {max_date}")
            else:
                print("⚠️ Datas não estão no formato correto")
            
            print(f"💰 Valor total: R$ {self.df_transacoes['valor_transacao'].sum():,.2f}")
            print(f"💰 Valor médio: R$ {self.df_transacoes['valor_transacao'].mean():.2f}")
            
        if self.df_clientes is not None:
            print(f"👥 Clientes: {len(self.df_clientes):,} registros")
            
        if self.df_agencias is not None:
            print(f"🏢 Agências: {len(self.df_agencias):,} registros")
            
        if self.dim_dates is not None:
            print(f"📅 Dimensão de datas: {len(self.dim_dates):,} registros")

    def analise_transacoes_por_dia_semana(self):
        """Análise de transações por dia da semana - CORRIGIDA"""
        if self.df_transacoes is None:
            print("❌ Dados de transações não disponíveis")
            return
            
        print("\n📈 ANÁLISE: TRANSAÇÕES POR DIA DA SEMANA")
        print("="*50)
        
        try:
            # Verifica se as datas estão no formato correto
            if not pd.api.types.is_datetime64_any_dtype(self.df_transacoes['data_transacao']):
                print("❌ Datas não estão no formato datetime correto")
                return
            
            # Cria análise
            df_analise = self.df_transacoes.copy()
            df_analise['nome_dia_semana'] = df_analise['data_transacao'].dt.day_name()
            df_analise['dia_semana_num'] = df_analise['data_transacao'].dt.dayofweek
            
            # Mapeamento para português
            dias_semana_pt = {
                'Monday': 'Segunda-feira',
                'Tuesday': 'Terça-feira', 
                'Wednesday': 'Quarta-feira',
                'Thursday': 'Quinta-feira',
                'Friday': 'Sexta-feira',
                'Saturday': 'Sábado',
                'Sunday': 'Domingo'
            }
            
            df_analise['nome_dia_semana_pt'] = df_analise['nome_dia_semana'].map(dias_semana_pt)
            
            # Agrupa por dia da semana
            resumo_dias = df_analise.groupby(['nome_dia_semana_pt', 'dia_semana_num']).agg({
                'valor_transacao': ['count', 'sum', 'mean']
            }).round(2)
            
            # Achata colunas
            resumo_dias.columns = ['Qtd_Transacoes', 'Volume_Total', 'Valor_Medio']
            resumo_dias = resumo_dias.reset_index()
            resumo_dias = resumo_dias.sort_values('dia_semana_num')
            resumo_dias = resumo_dias.set_index('nome_dia_semana_pt')
            resumo_dias = resumo_dias.drop('dia_semana_num', axis=1)
            
            print("📊 Resumo por dia da semana:")
            print(resumo_dias)
            
            # Identifica os melhores dias
            melhor_dia_qtd = resumo_dias['Qtd_Transacoes'].idxmax()
            melhor_dia_volume = resumo_dias['Volume_Total'].idxmax()
            
            print(f"\n🏆 DESTAQUES:")
            print(f"📈 Maior quantidade de transações: {melhor_dia_qtd} ({resumo_dias.loc[melhor_dia_qtd, 'Qtd_Transacoes']:,.0f} transações)")
            print(f"💰 Maior volume financeiro: {melhor_dia_volume} (R$ {resumo_dias.loc[melhor_dia_volume, 'Volume_Total']:,.2f})")
            
        except Exception as e:
            print(f"❌ Erro na análise por dia da semana: {e}")

    def verificar_hipotese_meses_pares(self):
        """Verifica se meses pares têm mais transações - CORRIGIDA"""
        if self.df_transacoes is None:
            print("❌ Dados de transações não disponíveis")
            return
            
        print("\n🔍 ANÁLISE: HIPÓTESE DOS MESES PARES")
        print("="*50)
        
        try:
            # Verifica se as datas estão corretas
            if not pd.api.types.is_datetime64_any_dtype(self.df_transacoes['data_transacao']):
                print("❌ Datas não estão no formato datetime correto")
                return
            
            df_analise = self.df_transacoes.copy()
            df_analise['mes'] = df_analise['data_transacao'].dt.month
            df_analise['eh_mes_par'] = (df_analise['mes'] % 2 == 0)
            
            # Análise por tipo de mês
            resumo_meses = df_analise.groupby('eh_mes_par').agg({
                'valor_transacao': ['count', 'sum', 'mean']
            }).round(2)
            
            resumo_meses.columns = ['Qtd_Transacoes', 'Volume_Total', 'Valor_Medio']
            resumo_meses.index = ['Meses Ímpares', 'Meses Pares']
            
            print("📊 Comparação Meses Ímpares vs Pares:")
            print(resumo_meses)
            
            # Calcula diferenças
            if len(resumo_meses) >= 2:
                qtd_pares = resumo_meses.loc['Meses Pares', 'Qtd_Transacoes']
                qtd_impares = resumo_meses.loc['Meses Ímpares', 'Qtd_Transacoes']
                vol_pares = resumo_meses.loc['Meses Pares', 'Volume_Total']
                vol_impares = resumo_meses.loc['Meses Ímpares', 'Volume_Total']
                
                diff_qtd = qtd_pares - qtd_impares
                diff_volume = vol_pares - vol_impares
                
                print(f"\n📊 DIFERENÇAS (Pares - Ímpares):")
                print(f"📈 Quantidade: {diff_qtd:,.0f} transações")
                print(f"💰 Volume: R$ {diff_volume:,.2f}")
                
                # Resultado da hipótese
                if diff_qtd > 0:
                    print("✅ HIPÓTESE CONFIRMADA: Meses pares têm mais transações!")
                    print(f"📊 Meses pares têm {abs(diff_qtd):,.0f} transações a mais ({(diff_qtd/qtd_impares*100):.1f}% mais)")
                else:
                    print("❌ HIPÓTESE REJEITADA: Meses ímpares têm mais transações!")
                    print(f"📊 Meses ímpares têm {abs(diff_qtd):,.0f} transações a mais ({(abs(diff_qtd)/qtd_pares*100):.1f}% mais)")
            
        except Exception as e:
            print(f"❌ Erro na análise de meses pares: {e}")

    def ranking_agencias(self):
        """Análise de performance das agências - MELHORADA"""
        if self.df_transacoes is None:
            print("❌ Dados de transações não disponíveis")
            return
            
        print("\n🏢 ANÁLISE: RANKING DE AGÊNCIAS")
        print("="*50)
        
        try:
            # Verifica se precisa fazer join com contas para obter agências
            if 'cod_agencia' not in self.df_transacoes.columns:
                contas_file = f'{self.data_path}contas.csv'
                if os.path.exists(contas_file):
                    print("🔗 Fazendo join com dados de contas para obter agências...")
                    df_contas = pd.read_csv(contas_file)
                    df_analise = self.df_transacoes.merge(
                        df_contas[['num_conta', 'cod_agencia']], 
                        on='num_conta', 
                        how='left'
                    )
                    print(f"✅ Join realizado: {len(df_analise)} registros")
                else:
                    print("⚠️ Arquivo contas.csv não encontrado para fazer o join")
                    return
            else:
                df_analise = self.df_transacoes.copy()
            
            # Filtra últimos 6 meses
            if pd.api.types.is_datetime64_any_dtype(df_analise['data_transacao']):
                data_limite = df_analise['data_transacao'].max() - pd.DateOffset(months=6)
                df_recente = df_analise[df_analise['data_transacao'] >= data_limite]
                print(f"📅 Analisando dados dos últimos 6 meses (desde {data_limite.strftime('%d/%m/%Y')})")
                print(f"📊 Registros no período: {len(df_recente):,}")
            else:
                df_recente = df_analise
                print("⚠️ Usando todos os dados (não foi possível filtrar por data)")
            
            # Remove registros sem agência
            df_recente = df_recente.dropna(subset=['cod_agencia'])
            print(f"📊 Registros com agência identificada: {len(df_recente):,}")
            
            if len(df_recente) == 0:
                print("❌ Nenhum registro com agência encontrado")
                return
            
            # Ranking por agência
            ranking = df_recente.groupby('cod_agencia').agg({
                'valor_transacao': ['count', 'sum', 'mean']
            }).round(2)
            
            ranking.columns = ['Qtd_Transacoes', 'Volume_Total', 'Valor_Medio']
            ranking = ranking.sort_values('Qtd_Transacoes', ascending=False)
            
            print(f"\n🏆 TOP 3 MELHORES AGÊNCIAS (por quantidade de transações):")
            print(ranking.head(3))
            
            print(f"\n⚠️ TOP 3 PIORES AGÊNCIAS:")
            print(ranking.tail(3))
            
            # Estatísticas gerais
            media_geral = ranking['Qtd_Transacoes'].mean()
            print(f"\n📊 ESTATÍSTICAS GERAIS:")
            print(f"📈 Média geral de transações por agência: {media_geral:.0f}")
            print(f"🏢 Total de agências ativas: {len(ranking)}")
            
            acima_media = ranking[ranking['Qtd_Transacoes'] > media_geral]
            abaixo_media = ranking[ranking['Qtd_Transacoes'] <= media_geral]
            
            print(f"📈 Agências acima da média: {len(acima_media)} ({len(acima_media)/len(ranking)*100:.1f}%)")
            print(f"📉 Agências abaixo da média: {len(abaixo_media)} ({len(abaixo_media)/len(ranking)*100:.1f}%)")
            
            # Salva o ranking
            ranking.to_csv(f'{self.data_path}ranking_agencias.csv')
            print(f"💾 Ranking salvo em: ranking_agencias.csv")
            
        except Exception as e:
            print(f"❌ Erro na análise de agências: {e}")
            import traceback
            traceback.print_exc()

def limpar_arquivos_duplicados(data_path):
    """Remove arquivos _corrigido duplicados se os originais funcionarem"""
    print("\n🧹 LIMPEZA DE ARQUIVOS DUPLICADOS")
    print("="*40)
    
    arquivos_corrigidos = [f for f in os.listdir(data_path) if f.endswith('_corrigido.csv')]
    
    for arquivo in arquivos_corrigidos:
        arquivo_original = arquivo.replace('_corrigido', '')
        
        if os.path.exists(os.path.join(data_path, arquivo_original)):
            try:
                # Testa se consegue carregar o original
                pd.read_csv(os.path.join(data_path, arquivo_original), nrows=1)
                print(f"🗑️ Removendo: {arquivo} (original funciona)")
                os.remove(os.path.join(data_path, arquivo))
            except:
                print(f"📋 Mantendo: {arquivo} (original tem problemas)")
        else:
            # Renomeia o corrigido para original
            os.rename(
                os.path.join(data_path, arquivo),
                os.path.join(data_path, arquivo_original)
            )
            print(f"📝 Renomeado: {arquivo} → {arquivo_original}")

def main():
    """Função principal"""
    
    data_path = 'dados/raw/banvic_data/'
    
    # Verifica se o diretório existe
    if not os.path.exists(data_path):
        print(f"❌ Diretório não encontrado: {os.path.abspath(data_path)}")
        print("💡 Execute primeiro: python fix_csv_issues.py")
        return
    
    # Limpa arquivos duplicados
    limpar_arquivos_duplicados(data_path)
    
    try:
        # Cria o dashboard
        dashboard = BanVicDashboard(data_path=data_path)
        
        # Executa as análises
        dashboard.show_data_info()
        dashboard.analise_transacoes_por_dia_semana()
        dashboard.verificar_hipotese_meses_pares()
        dashboard.ranking_agencias()
        
        print("\n" + "="*60)
        print("✅ DASHBOARD EXECUTADO COM SUCESSO!")
        print("📊 Todas as análises foram concluídas.")
        print("💾 Arquivos gerados:")
        print("   - dim_dates.csv")
        print("   - ranking_agencias.csv")
        print("🧹 Arquivos duplicados foram limpos automaticamente.")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()