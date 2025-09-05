"""
Dashboard Interativo BanVic - Versão CSV
Compatível com os arquivos do seu repositório
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BanVicDashboard:
    def __init__(self, data_path=''):
        """
        Inicializa o dashboard com o caminho dos dados
        """
        self.data_path = data_path
        self.load_data()
        self.prepare_data()
        
    def load_data(self):
        """
        Carrega todos os datasets necessários
        """
        print("📂 Carregando dados...")
        
        # Tentando carregar os CSVs primeiro (seus arquivos)
        try:
            # Carregando os CSVs do seu repositório (com os nomes corretos)
            self.df_agencias = pd.read_csv(f'{self.data_path}agencias.csv')
            self.df_clientes = pd.read_csv(f'{self.data_path}clientes.csv')
            self.df_transacoes = pd.read_csv(f'{self.data_path}transacoes.csv')
            # Você pode adicionar os outros arquivos aqui se precisar deles
            # self.df_colaboradores = pd.read_csv(f'{self.data_path}colaboradores.csv')
            # self.df_contas = pd.read_csv(f'{self.data_path}contas.csv')
            
            print("✅ Dados CSV carregados com sucesso!")
            
        except FileNotFoundError:
            print("❌ Arquivos CSV não encontrados.")
            print(f"📋 Verifique se os arquivos estão na pasta: {self.data_path}")
            raise
            
        # Carregando dimensão de datas se existir
        try:
            self.dim_dates = pd.read_csv(f'{self.data_path}dim_dates.csv')
        except:
            self.create_dim_dates()
            
    def create_dim_dates(self):
        """
        Cria a dimensão de datas caso não exista
        """
        # Convertendo data_transacao para datetime, deixando o pandas detectar o formato
        self.df_transacoes['data_transacao'] = pd.to_datetime(self.df_transacoes['data_transacao'])
        
        # Pegando range de datas das transações
        min_date = self.df_transacoes['data_transacao'].min()
        max_date = self.df_transacoes['data_transacao'].max()
        
        # Criando dimensão de datas
        date_range = pd.date_range(start=min_date, end=max_date, freq='D')
        
        self.dim_dates = pd.DataFrame({
            'data': date_range,
            'ano': date_range.year,
            'mes': date_range.month,
            'dia': date_range.day,
            'dia_semana': date_range.dayofweek,
            'nome_dia_semana': date_range.strftime('%A'),
            'nome_mes': date_range.strftime('%B'),
            'trimestre': date_range.quarter,
            'semana_ano': date_range.isocalendar().week,
            'eh_fim_semana': (date_range.dayofweek >= 5).astype(int),
            'mes_par': (date_range.month % 2 == 0).astype(int)
        })
        
    def prepare_data(self):
        """
        Prepara e enriquece os dados para análise
        """
        print("🔧 Preparando dados...")
        
        # Merge das tabelas
        self.df_completo = self.df_transacoes.merge(
            self.df_clientes, 
            on='cliente_id', 
            how='left'
        ).merge(
            self.df_agencias, 
            on='agencia_id', 
            how='left'
        )
        
        # Convertendo data para datetime (já foi feito, mas garantimos)
        self.df_completo['data_transacao'] = pd.to_datetime(self.df_completo['data_transacao'])
        
        # Adicionando informações de data
        self.df_completo['ano'] = self.df_completo['data_transacao'].dt.year
        self.df_completo['mes'] = self.df_completo['data_transacao'].dt.month
        self.df_completo['dia'] = self.df_completo['data_transacao'].dt.day
        self.df_completo['dia_semana'] = self.df_completo['data_transacao'].dt.day_name()
        self.df_completo['mes_nome'] = self.df_completo['data_transacao'].dt.strftime('%B')
        
        # Calculando últimos 6 meses
        data_corte = self.df_completo['data_transacao'].max() - pd.DateOffset(months=6)
        self.df_ultimos_6_meses = self.df_completo[
            self.df_completo['data_transacao'] >= data_corte
        ]
        
        print("✅ Dados preparados!")
        print(f"📊 Total de transações: {len(self.df_completo):,}")
        print(f"👥 Total de clientes: {self.df_completo['cliente_id'].nunique():,}")
        print(f"🏢 Total de agências: {self.df_completo['agencia_id'].nunique()}")
        
    def analise_ultimos_6_meses(self):
        """
        Análise específica dos últimos 6 meses - Item 5 do desafio
        """
        print("\n" + "="*60)
        print("📊 ANÁLISE DOS ÚLTIMOS 6 MESES")
        print("="*60)
        
        # Estatísticas por agência nos últimos 6 meses
        stats_6m = self.df_ultimos_6_meses.groupby('nome_agencia').agg({
            'transacao_id': 'count',
            'valor': 'sum'
        }).round(2)
        
        stats_6m.columns = ['total_transacoes', 'volume_total']
        stats_6m = stats_6m.sort_values('total_transacoes', ascending=False)
        
        # Top 3 melhores
        top3 = stats_6m.head(3)
        print("\n🏆 TOP 3 AGÊNCIAS (Últimos 6 meses):")
        for i, (agencia, dados) in enumerate(top3.iterrows(), 1):
            print(f"{i}. {agencia}: {dados['total_transacoes']:.0f} transações | R$ {dados['volume_total']:,.2f}")
        
        # Bottom 3 piores
        bottom3 = stats_6m.tail(3)
        print("\n📉 BOTTOM 3 AGÊNCIAS (Últimos 6 meses):")
        for i, (agencia, dados) in enumerate(bottom3.iterrows(), len(stats_6m)-2):
            print(f"{i}. {agencia}: {dados['total_transacoes']:.0f} transações | R$ {dados['volume_total']:,.2f}")
        
        # Agência com maior número de transações
        melhor_agencia = stats_6m.index[0]
        melhor_trans = stats_6m.iloc[0]['total_transacoes']
        
        # Agência com menor número de transações
        pior_agencia = stats_6m.index[-1]
        pior_trans = stats_6m.iloc[-1]['total_transacoes']
        
        print(f"\n✅ MAIOR número de transações: {melhor_agencia} ({melhor_trans:.0f} transações)")
        print(f"❌ MENOR número de transações: {pior_agencia} ({pior_trans:.0f} transações)")
        
        return stats_6m
        
    def analise_dia_semana(self):
        """
        Análise por dia da semana - Item 3 do desafio
        """
        print("\n" + "="*60)
        print("📅 ANÁLISE POR DIA DA SEMANA")
        print("="*60)
        
        # Filtrando apenas transações aprovadas
        df_aprovadas = self.df_completo[self.df_completo['status'] == 'Aprovada']
        
        # Agrupando por dia da semana
        stats_dia = df_aprovadas.groupby('dia_semana').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean']
        }).round(2)
        
        stats_dia.columns = ['qtd_aprovadas', 'volume_total', 'media_valor']
        
        # Reordenando dias
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        stats_dia = stats_dia.reindex(dias_ordem)
        
        # Encontrando o dia com maior média
        dia_maior_media = stats_dia['media_valor'].idxmax()
        dia_maior_volume = stats_dia['volume_total'].idxmax()
        
        idx_media = dias_ordem.index(dia_maior_media)
        idx_volume = dias_ordem.index(dia_maior_volume)
        
        print(f"\n📊 Dia com MAIOR MÉDIA de transações aprovadas:")
        print(f"   {dias_pt[idx_media]} - Média: R$ {stats_dia.loc[dia_maior_media, 'media_valor']:,.2f}")
        
        print(f"\n💰 Dia com MAIOR VOLUME movimentado:")
        print(f"   {dias_pt[idx_volume]} - Volume: R$ {stats_dia.loc[dia_maior_volume, 'volume_total']:,.2f}")
        
        return stats_dia
        
    def analise_meses_pares_impares(self):
        """
        Análise de meses pares vs ímpares - Item 3 do desafio
        """
        print("\n" + "="*60)
        print("📊 ANÁLISE: MESES PARES VS ÍMPARES")
        print("="*60)
        
        # Classificando meses
        self.df_completo['mes_tipo'] = self.df_completo['mes'].apply(
            lambda x: 'Par' if x % 2 == 0 else 'Ímpar'
        )
        
        # Estatísticas por tipo de mês
        stats_mes = self.df_completo.groupby('mes_tipo').agg({
            'valor': ['mean', 'sum', 'count']
        }).round(2)
        
        stats_mes.columns = ['volume_medio', 'volume_total', 'qtd_transacoes']
        
        # Comparando médias
        media_pares = stats_mes.loc['Par', 'volume_medio']
        media_impares = stats_mes.loc['Ímpar', 'volume_medio']
        
        print(f"\n📈 Volume médio de transações:")
        print(f"   Meses PARES: R$ {media_pares:,.2f}")
        print(f"   Meses ÍMPARES: R$ {media_impares:,.2f}")
        
        diferenca_percentual = ((media_pares - media_impares) / media_impares * 100)
        
        if abs(diferenca_percentual) > 10:
            print(f"\n⚠️ DIFERENÇA SIGNIFICATIVA DETECTADA!")
            print(f"   Meses pares têm {diferenca_percentual:+.1f}% de diferença")
            print(f"   ❌ A afirmação do analista está PARCIALMENTE CORRETA")
        else:
            print(f"\n✅ Diferença de apenas {diferenca_percentual:+.1f}%")
            print(f"   ❌ A afirmação do analista está INCORRETA")
            print(f"   Não há diferença significativa entre meses pares e ímpares")
        
        return stats_mes
        
    def export_to_powerbi(self):
        """
        Exporta dados preparados para Power BI
        """
        print("\n📤 Exportando dados para Power BI...")
        
        # Criando pasta para exports
        if not os.path.exists('powerbi_data'):
            os.makedirs('powerbi_data')
        
        # Exportando datasets
        self.df_completo.to_csv('powerbi_data/dados_completos.csv', index=False, encoding='utf-8-sig')
        self.dim_dates.to_csv('powerbi_data/dim_dates.csv', index=False, encoding='utf-8-sig')
        
        # Criando resumos
        resumo_agencias = self.df_completo.groupby(['agencia_id', 'nome_agencia']).agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').sum()
        }).reset_index()
        resumo_agencias.columns = ['agencia_id', 'nome_agencia', 'total_trans', 
                                  'volume_total', 'ticket_medio', 'trans_aprovadas']
        resumo_agencias.to_csv('powerbi_data/resumo_agencias.csv', index=False, encoding='utf-8-sig')
        
        print("✅ Dados exportados com sucesso!")
        print("📁 Arquivos criados em: ./powerbi_data/")
        
    def generate_all_dashboards(self):
        """
        Gera todos os dashboards e salva em HTML
        """
        print("\n🎨 Gerando dashboards...")
        
        # Criando pasta
        if not os.path.exists('dashboards'):
            os.makedirs('dashboards')
        
        # 1. Dashboard de Performance das Agências
        fig_agencias = self.create_agency_performance()
        fig_agencias.write_html('dashboards/01_agencias.html')
        
        # 2. Dashboard Temporal
        fig_temporal = self.create_time_analysis()
        fig_temporal.write_html('dashboards/02_temporal.html')
        
        # 3. Dashboard Dia da Semana
        fig_weekday = self.create_weekday_analysis()
        fig_weekday.write_html('dashboards/03_dia_semana.html')
        
        print("✅ Dashboards gerados com sucesso!")
        print("📁 Arquivos HTML salvos em: ./dashboards/")
        
    def create_agency_performance(self):
        """
        Cria gráfico de performance das agências
        """
        # Análise por agência - últimos 6 meses
        agency_stats = self.df_ultimos_6_meses.groupby('nome_agencia').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean']
        }).round(2)
        
        agency_stats.columns = ['total_transacoes', 'volume_total', 'ticket_medio']
        agency_stats = agency_stats.sort_values('total_transacoes', ascending=False)
        
        # Criando visualização
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Top Agências - Número de Transações (6 meses)',
                'Top Agências - Volume Total (6 meses)',
                'Ranking Completo de Agências',
                'Ticket Médio por Agência'
            )
        )
        
        # Top por transações
        top_trans = agency_stats.head(10)
        fig.add_trace(
            go.Bar(
                x=top_trans.index,
                y=top_trans['total_transacoes'],
                text=top_trans['total_transacoes'].astype(int),
                textposition='auto',
                marker_color='#1f77b4',
                name='Transações'
            ),
            row=1, col=1
        )
        
        # Top por volume
        top_volume = agency_stats.nlargest(10, 'volume_total')
        fig.add_trace(
            go.Bar(
                x=top_volume.index,
                y=top_volume['volume_total'],
                text=[f'R$ {v/1000:.1f}K' for v in top_volume['volume_total']],
                textposition='auto',
                marker_color='#ff7f0e',
                name='Volume'
            ),
            row=1, col=2
        )
        
        # Ranking completo
        fig.add_trace(
            go.Bar(
                x=agency_stats.index,
                y=agency_stats['total_transacoes'],
                marker_color=['green' if i < 3 else 'red' if i >= len(agency_stats)-3 else 'gray' 
                              for i in range(len(agency_stats))],
                name='Ranking'
            ),
            row=2, col=1
        )
        
        # Ticket médio
        fig.add_trace(
            go.Bar(
                x=agency_stats.index,
                y=agency_stats['ticket_medio'],
                text=[f'R$ {v:.2f}' for v in agency_stats['ticket_medio']],
                textposition='auto',
                marker_color='#2ca02c',
                name='Ticket Médio'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="🏢 Performance das Agências - Últimos 6 Meses"
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
        
    def create_time_analysis(self):
        """
        Cria análise temporal
        """
        daily_stats = self.df_completo.groupby('data_transacao').agg({
            'transacao_id': 'count',
            'valor': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=daily_stats['data_transacao'],
                y=daily_stats['valor'],
                mode='lines',
                fill='tozeroy',
                name='Volume Diário'
            )
        )
        
        fig.update_layout(
            title="📈 Evolução Temporal do Volume de Transações",
            xaxis_title="Data",
            yaxis_title="Volume (R$)",
            height=500
        )
        
        return fig
        
    def create_weekday_analysis(self):
        """
        Cria análise por dia da semana
        """
        # Preparando dados
        weekday_stats = self.df_completo.groupby('dia_semana').agg({
            'transacao_id': 'count',
            'valor': 'sum'
        })
        
        # Ordenando
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        weekday_stats = weekday_stats.reindex(dias_ordem)
        weekday_stats.index = dias_pt
        
        # Criando gráfico
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Transações por Dia da Semana', 'Volume por Dia da Semana')
        )
        
        fig.add_trace(
            go.Bar(
                x=weekday_stats.index,
                y=weekday_stats['transacao_id'],
                marker_color=['#1f77b4' if i < 5 else '#ff7f0e' for i in range(7)],
                text=weekday_stats['transacao_id'],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=weekday_stats.index,
                y=weekday_stats['valor'],
                marker_color=['#2ca02c' if i < 5 else '#d62728' for i in range(7)],
                text=[f'R$ {v/1000:.1f}K' for v in weekday_stats['valor']],
                textposition='auto'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            title_text="📅 Análise por Dia da Semana"
        )
        
        return fig

def main():
    """
    Função principal
    """
    print("\n" + "="*60)
    print("🏦 DASHBOARD BANVIC - ANÁLISE DE DADOS")
    print("="*60 + "\n")
    
    try:
        # ############################################################### #
        # ## CORREÇÃO PRINCIPAL: Informar o caminho correto dos dados ### #
        # ############################################################### #
        dashboard = BanVicDashboard(data_path='dados/raw/banvic_data/')
        
        # Executando análises específicas do desafio
        dashboard.analise_ultimos_6_meses()
        dashboard.analise_dia_semana()
        dashboard.analise_meses_pares_impares()
        
        # Gerando dashboards
        dashboard.generate_all_dashboards()
        
        # Exportando para Power BI
        dashboard.export_to_powerbi()
        
        print("\n" + "="*60)
        print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print("\n📊 Arquivos gerados:")
        print("   ✅ Dashboards HTML em: ./dashboards/")
        print("   ✅ Dados para Power BI em: ./powerbi_data/")
        print("\n💡 Próximos passos:")
        print("   1. Abra os arquivos HTML para visualizar os dashboards")
        print("   2. Importe os CSVs no Power BI Desktop")
        print("   3. Use as análises geradas para seu relatório")
        
    except FileNotFoundError as e:
        print("\n❌ ERRO: Arquivos de dados não encontrados!")
        print(f"\n📋 Verifique se a pasta e os arquivos existem no caminho especificado.")
        print("\n💡 Dica: Confira se os nomes dos arquivos CSV estão corretos (ex: agencias.csv)")

if __name__ == "__main__":
    main()