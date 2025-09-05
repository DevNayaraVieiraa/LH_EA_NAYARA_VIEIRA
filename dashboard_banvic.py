"""
Dashboard Interativo BanVic
Autor: Análise de Dados BanVic
Data: 2025
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BanVicDashboard:
    def __init__(self, data_path='data/'):
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
        
        # Carregando as tabelas
        self.df_agencias = pd.read_excel(f'{self.data_path}tb_agencias.xlsx')
        self.df_clientes = pd.read_excel(f'{self.data_path}tb_clientes.xlsx')
        self.df_transacoes = pd.read_excel(f'{self.data_path}tb_transacoes.xlsx')
        
        # Carregando dimensão de datas se existir
        try:
            self.dim_dates = pd.read_excel(f'{self.data_path}dim_dates.xlsx')
        except:
            self.create_dim_dates()
            
        print("✅ Dados carregados com sucesso!")
        
    def create_dim_dates(self):
        """
        Cria a dimensão de datas caso não exista
        """
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
        
        # Convertendo data para datetime
        self.df_completo['data_transacao'] = pd.to_datetime(self.df_completo['data_transacao'])
        
        # Adicionando informações de data
        self.df_completo['ano'] = self.df_completo['data_transacao'].dt.year
        self.df_completo['mes'] = self.df_completo['data_transacao'].dt.month
        self.df_completo['dia_semana'] = self.df_completo['data_transacao'].dt.day_name()
        self.df_completo['mes_nome'] = self.df_completo['data_transacao'].dt.strftime('%B')
        
        # Calculando últimos 6 meses
        data_corte = self.df_completo['data_transacao'].max() - pd.DateOffset(months=6)
        self.df_ultimos_6_meses = self.df_completo[
            self.df_completo['data_transacao'] >= data_corte
        ]
        
        print("✅ Dados preparados!")
        
    def create_kpi_cards(self):
        """
        Cria cartões de KPIs principais
        """
        # Calculando KPIs
        total_transacoes = len(self.df_completo)
        transacoes_aprovadas = len(self.df_completo[self.df_completo['status'] == 'Aprovada'])
        taxa_aprovacao = (transacoes_aprovadas / total_transacoes * 100) if total_transacoes > 0 else 0
        volume_total = self.df_completo['valor'].sum()
        ticket_medio = self.df_completo['valor'].mean()
        total_clientes = self.df_completo['cliente_id'].nunique()
        total_agencias = self.df_completo['agencia_id'].nunique()
        
        # Criando figura com subplots para KPIs
        fig = make_subplots(
            rows=2, cols=4,
            subplot_titles=(
                f'Total de Transações<br><b>{total_transacoes:,}</b>',
                f'Taxa de Aprovação<br><b>{taxa_aprovacao:.1f}%</b>',
                f'Volume Total<br><b>R$ {volume_total/1e6:.2f}M</b>',
                f'Ticket Médio<br><b>R$ {ticket_medio:.2f}</b>',
                f'Total de Clientes<br><b>{total_clientes:,}</b>',
                f'Total de Agências<br><b>{total_agencias}</b>',
                'Transações/Dia<br><b>{:.0f}</b>'.format(total_transacoes/365),
                f'Transações Aprovadas<br><b>{transacoes_aprovadas:,}</b>'
            ),
            specs=[[{'type': 'indicator'}] * 4] * 2,
            vertical_spacing=0.3,
            horizontal_spacing=0.1
        )
        
        # Configurando layout
        fig.update_layout(
            height=300,
            showlegend=False,
            title_text="📊 KPIs Principais - BanVic",
            title_font_size=20,
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
        
    def create_agency_performance(self):
        """
        Cria gráfico de performance das agências
        """
        # Análise por agência
        agency_stats = self.df_ultimos_6_meses.groupby('nome_agencia').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').sum()
        }).round(2)
        
        agency_stats.columns = ['total_transacoes', 'volume_total', 'ticket_medio', 'transacoes_aprovadas']
        agency_stats['taxa_aprovacao'] = (
            agency_stats['transacoes_aprovadas'] / agency_stats['total_transacoes'] * 100
        ).round(1)
        agency_stats = agency_stats.sort_values('volume_total', ascending=False)
        
        # Criando gráfico de barras
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Top 5 Agências - Volume Total (R$)',
                'Top 5 Agências - Número de Transações',
                'Taxa de Aprovação por Agência (%)',
                'Ticket Médio por Agência (R$)'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        # Top 5 Volume
        top5_volume = agency_stats.nlargest(5, 'volume_total')
        fig.add_trace(
            go.Bar(
                x=top5_volume.index,
                y=top5_volume['volume_total'],
                text=[f'R$ {v/1000:.1f}K' for v in top5_volume['volume_total']],
                textposition='auto',
                marker_color='#1f77b4',
                name='Volume'
            ),
            row=1, col=1
        )
        
        # Top 5 Transações
        top5_trans = agency_stats.nlargest(5, 'total_transacoes')
        fig.add_trace(
            go.Bar(
                x=top5_trans.index,
                y=top5_trans['total_transacoes'],
                text=top5_trans['total_transacoes'],
                textposition='auto',
                marker_color='#ff7f0e',
                name='Transações'
            ),
            row=1, col=2
        )
        
        # Taxa de Aprovação
        fig.add_trace(
            go.Bar(
                x=agency_stats.index,
                y=agency_stats['taxa_aprovacao'],
                text=[f'{v:.1f}%' for v in agency_stats['taxa_aprovacao']],
                textposition='auto',
                marker_color='#2ca02c',
                name='Taxa Aprovação'
            ),
            row=2, col=1
        )
        
        # Ticket Médio
        fig.add_trace(
            go.Bar(
                x=agency_stats.index,
                y=agency_stats['ticket_medio'],
                text=[f'R$ {v:.2f}' for v in agency_stats['ticket_medio']],
                textposition='auto',
                marker_color='#d62728',
                name='Ticket Médio'
            ),
            row=2, col=2
        )
        
        # Atualizando layout
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="🏢 Performance das Agências - Últimos 6 Meses",
            title_font_size=20
        )
        
        fig.update_xaxes(tickangle=45)
        
        return fig
        
    def create_time_analysis(self):
        """
        Cria análise temporal das transações
        """
        # Agrupando por data
        daily_stats = self.df_completo.groupby('data_transacao').agg({
            'transacao_id': 'count',
            'valor': 'sum',
            'status': lambda x: (x == 'Aprovada').sum()
        }).reset_index()
        daily_stats.columns = ['data', 'total_transacoes', 'volume', 'aprovadas']
        
        # Criando gráfico de linha temporal
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=(
                'Volume de Transações Diário (R$)',
                'Número de Transações por Dia',
                'Taxa de Aprovação Diária (%)'
            ),
            shared_xaxes=True,
            vertical_spacing=0.08
        )
        
        # Volume diário
        fig.add_trace(
            go.Scatter(
                x=daily_stats['data'],
                y=daily_stats['volume'],
                mode='lines',
                name='Volume',
                line=dict(color='#1f77b4', width=2),
                fill='tozeroy',
                fillcolor='rgba(31, 119, 180, 0.3)'
            ),
            row=1, col=1
        )
        
        # Número de transações
        fig.add_trace(
            go.Scatter(
                x=daily_stats['data'],
                y=daily_stats['total_transacoes'],
                mode='lines',
                name='Transações',
                line=dict(color='#ff7f0e', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 127, 14, 0.3)'
            ),
            row=2, col=1
        )
        
        # Taxa de aprovação
        daily_stats['taxa_aprovacao'] = (
            daily_stats['aprovadas'] / daily_stats['total_transacoes'] * 100
        )
        fig.add_trace(
            go.Scatter(
                x=daily_stats['data'],
                y=daily_stats['taxa_aprovacao'],
                mode='lines+markers',
                name='Taxa Aprovação',
                line=dict(color='#2ca02c', width=2),
                marker=dict(size=4)
            ),
            row=3, col=1
        )
        
        # Atualizando layout
        fig.update_layout(
            height=700,
            showlegend=False,
            title_text="📈 Análise Temporal das Transações",
            title_font_size=20
        )
        
        fig.update_xaxes(title_text="Data", row=3, col=1)
        fig.update_yaxes(title_text="R$", row=1, col=1)
        fig.update_yaxes(title_text="Qtd", row=2, col=1)
        fig.update_yaxes(title_text="%", row=3, col=1)
        
        return fig
        
    def create_weekday_analysis(self):
        """
        Análise por dia da semana
        """
        # Ordenando dias da semana
        dias_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        # Agrupando por dia da semana
        weekday_stats = self.df_completo.groupby('dia_semana').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').mean() * 100
        }).round(2)
        
        weekday_stats.columns = ['total_trans', 'volume_total', 'valor_medio', 'taxa_aprovacao']
        
        # Reordenando
        weekday_stats = weekday_stats.reindex(dias_ordem)
        weekday_stats.index = dias_pt
        
        # Criando gráfico
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Transações por Dia da Semana',
                'Volume Total por Dia (R$)',
                'Valor Médio por Transação (R$)',
                'Taxa de Aprovação por Dia (%)'
            ),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'scatter'}, {'type': 'scatter'}]]
        )
        
        # Transações totais
        fig.add_trace(
            go.Bar(
                x=weekday_stats.index,
                y=weekday_stats['total_trans'],
                text=weekday_stats['total_trans'],
                textposition='auto',
                marker_color=['#1f77b4' if i < 5 else '#ff7f0e' for i in range(7)],
                name='Transações'
            ),
            row=1, col=1
        )
        
        # Volume total
        fig.add_trace(
            go.Bar(
                x=weekday_stats.index,
                y=weekday_stats['volume_total'],
                text=[f'R$ {v/1000:.1f}K' for v in weekday_stats['volume_total']],
                textposition='auto',
                marker_color=['#2ca02c' if i < 5 else '#d62728' for i in range(7)],
                name='Volume'
            ),
            row=1, col=2
        )
        
        # Valor médio
        fig.add_trace(
            go.Scatter(
                x=weekday_stats.index,
                y=weekday_stats['valor_medio'],
                mode='lines+markers',
                text=[f'R$ {v:.2f}' for v in weekday_stats['valor_medio']],
                marker=dict(size=10, color='#9467bd'),
                line=dict(width=3, color='#9467bd'),
                name='Valor Médio'
            ),
            row=2, col=1
        )
        
        # Taxa de aprovação
        fig.add_trace(
            go.Scatter(
                x=weekday_stats.index,
                y=weekday_stats['taxa_aprovacao'],
                mode='lines+markers',
                text=[f'{v:.1f}%' for v in weekday_stats['taxa_aprovacao']],
                marker=dict(size=10, color='#e377c2'),
                line=dict(width=3, color='#e377c2'),
                name='Taxa Aprovação'
            ),
            row=2, col=2
        )
        
        # Atualizando layout
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="📅 Análise por Dia da Semana",
            title_font_size=20
        )
        
        return fig
        
    def create_customer_segmentation(self):
        """
        Cria análise de segmentação de clientes
        """
        # Análise por cliente
        customer_stats = self.df_completo.groupby('cliente_id').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').sum()
        }).round(2)
        
        customer_stats.columns = ['total_trans', 'volume_total', 'ticket_medio', 'trans_aprovadas']
        
        # Criando segmentos baseados em volume
        customer_stats['segmento'] = pd.qcut(
            customer_stats['volume_total'], 
            q=4, 
            labels=['Bronze', 'Prata', 'Ouro', 'Diamante']
        )
        
        # Estatísticas por segmento
        segment_stats = customer_stats.groupby('segmento').agg({
            'total_trans': ['count', 'mean'],
            'volume_total': ['sum', 'mean'],
            'ticket_medio': 'mean'
        }).round(2)
        
        segment_stats.columns = ['qtd_clientes', 'media_trans', 'volume_total', 'volume_medio', 'ticket_medio']
        
        # Criando gráfico de pizza e barras
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Distribuição de Clientes por Segmento',
                'Volume Total por Segmento (R$)',
                'Ticket Médio por Segmento (R$)',
                'Média de Transações por Cliente'
            ),
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Pizza - Distribuição de clientes
        fig.add_trace(
            go.Pie(
                labels=segment_stats.index,
                values=segment_stats['qtd_clientes'],
                hole=0.4,
                marker_colors=['#8B4513', '#C0C0C0', '#FFD700', '#B9F2FF']
            ),
            row=1, col=1
        )
        
        # Volume por segmento
        fig.add_trace(
            go.Bar(
                x=segment_stats.index,
                y=segment_stats['volume_total'],
                text=[f'R$ {v/1e6:.2f}M' for v in segment_stats['volume_total']],
                textposition='auto',
                marker_color=['#8B4513', '#C0C0C0', '#FFD700', '#B9F2FF']
            ),
            row=1, col=2
        )
        
        # Ticket médio
        fig.add_trace(
            go.Bar(
                x=segment_stats.index,
                y=segment_stats['ticket_medio'],
                text=[f'R$ {v:.2f}' for v in segment_stats['ticket_medio']],
                textposition='auto',
                marker_color=['#8B4513', '#C0C0C0', '#FFD700', '#B9F2FF']
            ),
            row=2, col=1
        )
        
        # Média de transações
        fig.add_trace(
            go.Bar(
                x=segment_stats.index,
                y=segment_stats['media_trans'],
                text=[f'{v:.0f}' for v in segment_stats['media_trans']],
                textposition='auto',
                marker_color=['#8B4513', '#C0C0C0', '#FFD700', '#B9F2FF']
            ),
            row=2, col=2
        )
        
        # Atualizando layout
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="👥 Segmentação de Clientes",
            title_font_size=20
        )
        
        return fig
        
    def create_monthly_comparison(self):
        """
        Cria comparação entre meses pares e ímpares
        """
        # Adicionando coluna de mês par/ímpar
        self.df_completo['mes_tipo'] = self.df_completo['mes'].apply(
            lambda x: 'Par' if x % 2 == 0 else 'Ímpar'
        )
        
        # Agrupando por tipo de mês
        month_type_stats = self.df_completo.groupby('mes_tipo').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').mean() * 100
        }).round(2)
        
        month_type_stats.columns = ['total_trans', 'volume_total', 'valor_medio', 'taxa_aprovacao']
        
        # Agrupando por mês individual
        monthly_stats = self.df_completo.groupby(['mes', 'mes_nome']).agg({
            'transacao_id': 'count',
            'valor': 'sum'
        }).reset_index()
        monthly_stats.columns = ['mes', 'mes_nome', 'total_trans', 'volume']
        monthly_stats['tipo'] = monthly_stats['mes'].apply(lambda x: 'Par' if x % 2 == 0 else 'Ímpar')
        
        # Criando visualização
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Comparação: Meses Pares vs Ímpares',
                'Volume Mensal de Transações',
                'Distribuição de Volume (R$)',
                'Taxa de Aprovação (%)'
            ),
            specs=[[{'type': 'bar'}, {'type': 'bar'}],
                   [{'type': 'box'}, {'type': 'bar'}]]
        )
        
        # Comparação geral
        fig.add_trace(
            go.Bar(
                x=['Total Transações', 'Volume Total (K)', 'Valor Médio'],
                y=[
                    month_type_stats.loc['Par', 'total_trans'],
                    month_type_stats.loc['Par', 'volume_total']/1000,
                    month_type_stats.loc['Par', 'valor_medio']
                ],
                name='Meses Pares',
                marker_color='#1f77b4'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=['Total Transações', 'Volume Total (K)', 'Valor Médio'],
                y=[
                    month_type_stats.loc['Ímpar', 'total_trans'],
                    month_type_stats.loc['Ímpar', 'volume_total']/1000,
                    month_type_stats.loc['Ímpar', 'valor_medio']
                ],
                name='Meses Ímpares',
                marker_color='#ff7f0e'
            ),
            row=1, col=1
        )
        
        # Volume por mês
        colors = ['#1f77b4' if m % 2 == 0 else '#ff7f0e' for m in monthly_stats['mes']]
        fig.add_trace(
            go.Bar(
                x=monthly_stats['mes_nome'],
                y=monthly_stats['volume'],
                text=[f'R$ {v/1000:.1f}K' for v in monthly_stats['volume']],
                textposition='auto',
                marker_color=colors
            ),
            row=1, col=2
        )
        
        # Box plot de distribuição
        for tipo in ['Par', 'Ímpar']:
            dados = self.df_completo[self.df_completo['mes_tipo'] == tipo]['valor']
            fig.add_trace(
                go.Box(
                    y=dados,
                    name=f'Meses {tipo}s',
                    boxmean='sd'
                ),
                row=2, col=1
            )
        
        # Taxa de aprovação
        fig.add_trace(
            go.Bar(
                x=month_type_stats.index,
                y=month_type_stats['taxa_aprovacao'],
                text=[f'{v:.1f}%' for v in month_type_stats['taxa_aprovacao']],
                textposition='auto',
                marker_color=['#1f77b4', '#ff7f0e']
            ),
            row=2, col=2
        )
        
        # Atualizando layout
        fig.update_layout(
            height=700,
            showlegend=True,
            title_text="📊 Análise: Meses Pares vs Ímpares",
            title_font_size=20
        )
        
        return fig
        
    def export_to_powerbi(self):
        """
        Exporta dados preparados para Power BI
        """
        print("📤 Exportando dados para Power BI...")
        
        # Criando pasta para exports
        import os
        if not os.path.exists('powerbi_data'):
            os.makedirs('powerbi_data')
        
        # Exportando dataset principal
        self.df_completo.to_csv('powerbi_data/dados_completos.csv', index=False, encoding='utf-8-sig')
        
        # Exportando dimensão de datas
        self.dim_dates.to_csv('powerbi_data/dim_dates.csv', index=False, encoding='utf-8-sig')
        
        # Criando tabela resumo por agência
        resumo_agencias = self.df_completo.groupby(['agencia_id', 'nome_agencia']).agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').sum()
        }).reset_index()
        resumo_agencias.columns = ['agencia_id', 'nome_agencia', 'total_trans', 
                                   'volume_total', 'ticket_medio', 'trans_aprovadas']
        resumo_agencias.to_csv('powerbi_data/resumo_agencias.csv', index=False, encoding='utf-8-sig')
        
        # Criando tabela resumo por cliente
        resumo_clientes = self.df_completo.groupby('cliente_id').agg({
            'transacao_id': 'count',
            'valor': ['sum', 'mean'],
            'status': lambda x: (x == 'Aprovada').sum()
        }).reset_index()
        resumo_clientes.columns = ['cliente_id', 'total_trans', 'volume_total', 
                                   'ticket_medio', 'trans_aprovadas']
        resumo_clientes.to_csv('powerbi_data/resumo_clientes.csv', index=False, encoding='utf-8-sig')
        
        # Criando medidas DAX para Power BI
        dax_measures = """
        # MEDIDAS DAX PARA POWER BI - BANVIC
        
        ## KPIs Principais
        
        Total Transações = COUNT('dados_completos'[transacao_id])
        
        Volume Total = SUM('dados_completos'[valor])
        
        Ticket Médio = AVERAGE('dados_completos'[valor])
        
        Taxa Aprovação = 
        DIVIDE(
            CALCULATE(COUNT('dados_completos'[transacao_id]), 'dados_completos'[status] = "Aprovada"),
            COUNT('dados_completos'[transacao_id]),
            0
        ) * 100
        
        ## Análise Temporal
        
        Transações YoY = 
        VAR TransacoesAnoAtual = CALCULATE([Total Transações], YEAR('dados_completos'[data_transacao]) = YEAR(TODAY()))
        VAR TransacoesAnoAnterior = CALCULATE([Total Transações], YEAR('dados_completos'[data_transacao]) = YEAR(TODAY()) - 1)
        RETURN
        DIVIDE(TransacoesAnoAtual - TransacoesAnoAnterior, TransacoesAnoAnterior, 0) * 100
        
        Volume MoM = 
        VAR VolumeMesAtual = CALCULATE([Volume Total], MONTH('dados_completos'[data_transacao]) = MONTH(TODAY()))
        VAR VolumeMesAnterior = CALCULATE([Volume Total], MONTH('dados_completos'[data_transacao]) = MONTH(TODAY()) - 1)
        RETURN
        DIVIDE(VolumeMesAtual - VolumeMesAnterior, VolumeMesAnterior, 0) * 100
        
        ## Ranking de Agências
        
        Ranking Agências Volume = 
        RANKX(
            ALL('resumo_agencias'[nome_agencia]),
            [Volume Total],
            ,
            DESC
        )
        
        ## Segmentação de Clientes
        
        Segmento Cliente = 
        SWITCH(
            TRUE(),
            [Volume Total] > 10000, "Diamante",
            [Volume Total] > 5000, "Ouro",
            [Volume Total] > 1000, "Prata",
            "Bronze"
        )
        """
        
        # Salvando medidas DAX
        with open('powerbi_data/medidas_dax.txt', 'w', encoding='utf-8') as f:
            f.write(dax_measures)
        
        print("✅ Dados exportados com sucesso!")
        print("📁 Arquivos criados em: ./powerbi_data/")
        print("   - dados_completos.csv")
        print("   - dim_dates.csv")
        print("   - resumo_agencias.csv")
        print("   - resumo_clientes.csv")
        print("   - medidas_dax.txt")
        
    def generate_all_dashboards(self):
        """
        Gera todos os dashboards e salva em HTML
        """
        print("🎨 Gerando dashboards...")
        
        # Lista para armazenar todos os gráficos
        all_figures = []
        
        # 1. KPIs
        kpi_fig = self.create_kpi_cards()
        kpi_fig.write_html('dashboards/01_kpis.html')
        all_figures.append(kpi_fig)
        
        # 2. Performance das Agências
        agency_fig = self.create_agency_performance()
        agency_fig.write_html('dashboards/02_agencias.html')
        all_figures.append(agency_fig)
        
        # 3. Análise Temporal
        time_fig = self.create_time_analysis()
        time_fig.write_html('dashboards/03_temporal.html')
        all_figures.append(time_fig)
        
        # 4. Análise por Dia da Semana
        weekday_fig = self.create_weekday_analysis()
        weekday_fig.write_html('dashboards/04_dia_semana.html')
        all_figures.append(weekday_fig)
        
        # 5. Segmentação de Clientes
        customer_fig = self.create_customer_segmentation()
        customer_fig.write_html('dashboards/05_clientes.html')
        all_figures.append(customer_fig)
        
        # 6. Comparação Meses Pares vs Ímpares
        month_fig = self.create_monthly_comparison()
        month_fig.write_html('dashboards/06_meses.html')
        all_figures.append(month_fig)
        
        print("✅ Dashboards gerados com sucesso!")
        print("📁 Arquivos HTML salvos em: ./dashboards/")
        
        return all_figures

# Função principal para executar o dashboard
def main():
    """
    Função principal para executar o dashboard
    """
    print("\n" + "="*60)
    print("🏦 DASHBOARD BANVIC - ANÁLISE DE DADOS")
    print("="*60 + "\n")
    
    # Criando diretórios necessários
    import os
    for folder in ['dashboards', 'powerbi_data']:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # Inicializando dashboard
    dashboard = BanVicDashboard(data_path='data/')
    
    # Gerando todos os dashboards
    dashboard.generate_all_dashboards()
    
    # Exportando dados para Power BI
    dashboard.export_to_powerbi()
    
    print("\n" + "="*60)
    print("🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\n📊 Próximos passos:")
    print("1. Abra o Power BI Desktop")
    print("2. Importe os arquivos CSV da pasta 'powerbi_data'")
    print("3. Use as medidas DAX do arquivo 'medidas_dax.txt'")
    print("4. Os dashboards HTML podem ser visualizados no navegador")
    print("\n")

if __name__ == "__main__":
    main()