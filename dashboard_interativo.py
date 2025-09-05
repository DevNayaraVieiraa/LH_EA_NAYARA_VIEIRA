"""
Dashboard Interativo BanVic com Dash
Servidor web para visualização interativa
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import warnings
warnings.filterwarnings('ignore')

# Importando a classe do dashboard principal
from dashboard_banvic_csv import BanVicDashboard

# Inicializando a aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Carregando dados
dashboard_data = BanVicDashboard(data_path='data/')

# Layout da aplicação
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("🏦 BanVic Analytics Dashboard", className="text-center text-primary mb-4"),
            html.Hr()
        ], width=12)
    ]),
    
    # Filtros
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("📅 Filtros", className="card-title"),
                    html.Hr(),
                    
                    # Filtro de Data
                    html.Label("Período:", className="fw-bold"),
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date=dashboard_data.df_completo['data_transacao'].min(),
                        end_date=dashboard_data.df_completo['data_transacao'].max(),
                        display_format='DD/MM/YYYY',
                        style={'width': '100%'},
                        className="mb-3"
                    ),
                    
                    # Filtro de Agência
                    html.Label("Agência:", className="fw-bold mt-3"),
                    dcc.Dropdown(
                        id='agency-dropdown',
                        options=[{'label': 'Todas', 'value': 'all'}] + 
                                [{'label': ag, 'value': ag} 
                                 for ag in sorted(dashboard_data.df_completo['nome_agencia'].unique())],
                        value='all',
                        className="mb-3"
                    ),
                    
                    # Filtro de Status
                    html.Label("Status:", className="fw-bold mt-3"),
                    dcc.Dropdown(
                        id='status-dropdown',
                        options=[
                            {'label': 'Todos', 'value': 'all'},
                            {'label': 'Aprovada', 'value': 'Aprovada'},
                            {'label': 'Negada', 'value': 'Negada'},
                            {'label': 'Cancelada', 'value': 'Cancelada'}
                        ],
                        value='all',
                        className="mb-3"
                    ),
                    
                    # Botão de Atualizar
                    dbc.Button(
                        "🔄 Atualizar Dashboard",
                        id="update-button",
                        color="primary",
                        className="w-100 mt-3",
                        n_clicks=0
                    )
                ])
            ])
        ], width=3),
        
        # Área principal do dashboard
        dbc.Col([
            # KPIs
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Total Transações", className="text-muted"),
                            html.H3(id="kpi-total-trans", children="0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Volume Total", className="text-muted"),
                            html.H3(id="kpi-volume", children="R$ 0")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Taxa Aprovação", className="text-muted"),
                            html.H3(id="kpi-approval", children="0%")
                        ])
                    ])
                ], width=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Ticket Médio", className="text-muted"),
                            html.H3(id="kpi-ticket", children="R$ 0")
                        ])
                    ])
                ], width=3),
            ], className="mb-4"),
            
            # Tabs com gráficos
            dbc.Card([
                dbc.CardBody([
                    dcc.Tabs(id="tabs", value="tab-1", children=[
                        dcc.Tab(label="📊 Análise Temporal", value="tab-1"),
                        dcc.Tab(label="🏢 Performance Agências", value="tab-2"),
                        dcc.Tab(label="📅 Dia da Semana", value="tab-3"),
                        dcc.Tab(label="👥 Clientes", value="tab-4"),
                        dcc.Tab(label="📈 Tendências", value="tab-5"),
                    ]),
                    html.Div(id="tabs-content", className="mt-4")
                ])
            ])
        ], width=9)
    ])
], fluid=True)

# Callbacks
@app.callback(
    [Output("kpi-total-trans", "children"),
     Output("kpi-volume", "children"),
     Output("kpi-approval", "children"),
     Output("kpi-ticket", "children"),
     Output("tabs-content", "children")],
    [Input("update-button", "n_clicks"),
     Input("tabs", "value")],
    [State("date-range-picker", "start_date"),
     State("date-range-picker", "end_date"),
     State("agency-dropdown", "value"),
     State("status-dropdown", "value")]
)
def update_dashboard(n_clicks, active_tab, start_date, end_date, agency, status):
    """
    Atualiza o dashboard com base nos filtros
    """
    # Filtrando dados
    df_filtered = dashboard_data.df_completo.copy()
    
    # Filtro de data
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered['data_transacao'] >= start_date) &
            (df_filtered['data_transacao'] <= end_date)
        ]
    
    # Filtro de agência
    if agency != 'all':
        df_filtered = df_filtered[df_filtered['nome_agencia'] == agency]
    
    # Filtro de status
    if status != 'all':
        df_filtered = df_filtered[df_filtered['status'] == status]
    
    # Calculando KPIs
    total_trans = len(df_filtered)
    volume_total = df_filtered['valor'].sum()
    trans_aprovadas = len(df_filtered[df_filtered['status'] == 'Aprovada'])
    taxa_aprovacao = (trans_aprovadas / total_trans * 100) if total_trans > 0 else 0
    ticket_medio = df_filtered['valor'].mean() if total_trans > 0 else 0
    
    # Formatando KPIs
    kpi_total = f"{total_trans:,}"
    kpi_volume = f"R$ {volume_total/1e6:.2f}M" if volume_total >= 1e6 else f"R$ {volume_total/1e3:.1f}K"
    kpi_approval = f"{taxa_aprovacao:.1f}%"
    kpi_ticket = f"R$ {ticket_medio:.2f}"
    
    # Criando conteúdo das tabs
    if active_tab == "tab-1":
        # Análise Temporal
        daily_data = df_filtered.groupby('data_transacao').agg({
            'valor': 'sum',
            'transacao_id': 'count'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_data['data_transacao'],
            y=daily_data['valor'],
            mode='lines+markers',
            name='Volume Diário',
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.3)'
        ))
        
        fig.update_layout(
            title="Volume de Transações ao Longo do Tempo",
            xaxis_title="Data",
            yaxis_title="Volume (R$)",
            hovermode='x unified',
            height=500
        )
        
        content = dcc.Graph(figure=fig)
        
    elif active_tab == "tab-2":
        # Performance das Agências
        agency_data = df_filtered.groupby('nome_agencia').agg({
            'valor': 'sum',
            'transacao_id': 'count'
        }).reset_index()
        agency_data = agency_data.sort_values('valor', ascending=False).head(10)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=agency_data['nome_agencia'],
            y=agency_data['valor'],
            text=[f'R$ {v/1000:.1f}K' for v in agency_data['valor']],
            textposition='auto',
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title="Top 10 Agências por Volume",
            xaxis_title="Agência",
            yaxis_title="Volume (R$)",
            height=500
        )
        
        content = dcc.Graph(figure=fig)
        
    elif active_tab == "tab-3":
        # Análise por Dia da Semana
        df_filtered['dia_semana_num'] = pd.to_datetime(df_filtered['data_transacao']).dt.dayofweek
        df_filtered['dia_semana_nome'] = pd.to_datetime(df_filtered['data_transacao']).dt.day_name()
        
        weekday_data = df_filtered.groupby(['dia_semana_num', 'dia_semana_nome']).agg({
            'valor': ['sum', 'mean'],
            'transacao_id': 'count'
        }).reset_index()
        weekday_data.columns = ['dia_num', 'dia_nome', 'volume', 'ticket_medio', 'total_trans']
        weekday_data = weekday_data.sort_values('dia_num')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekday_data['dia_nome'],
            y=weekday_data['volume'],
            text=[f'R$ {v/1000:.1f}K' for v in weekday_data['volume']],
            textposition='auto',
            marker_color=['#2ca02c' if i < 5 else '#d62728' for i in range(len(weekday_data))]
        ))
        
        fig.update_layout(
            title="Volume por Dia da Semana",
            xaxis_title="Dia da Semana",
            yaxis_title="Volume (R$)",
            height=500
        )
        
        content = dcc.Graph(figure=fig)
        
    elif active_tab == "tab-4":
        # Análise de Clientes
        customer_data = df_filtered.groupby('cliente_id').agg({
            'valor': 'sum',
            'transacao_id': 'count'
        }).reset_index()
        
        # Criando segmentos
        customer_data['segmento'] = pd.qcut(
            customer_data['valor'],
            q=4,
            labels=['Bronze', 'Prata', 'Ouro', 'Diamante']
        )
        
        segment_count = customer_data['segmento'].value_counts()
        
        fig = go.Figure(data=[
            go.Pie(
                labels=segment_count.index,
                values=segment_count.values,
                hole=0.4,
                marker_colors=['#8B4513', '#C0C0C0', '#FFD700', '#B9F2FF']
            )
        ])
        
        fig.update_layout(
            title="Distribuição de Clientes por Segmento",
            height=500
        )
        
        content = dcc.Graph(figure=fig)
        
    else:  # tab-5
        # Tendências
        df_filtered['mes_ano'] = pd.to_datetime(df_filtered['data_transacao']).dt.to_period('M')
        monthly_data = df_filtered.groupby('mes_ano').agg({
            'valor': 'sum',
            'transacao_id': 'count'
        }).reset_index()
        monthly_data['mes_ano'] = monthly_data['mes_ano'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_data['mes_ano'],
            y=monthly_data['valor'],
            mode='lines+markers',
            name='Volume Mensal',
            line=dict(color='#9467bd', width=3),
            marker=dict(size=8)
        ))
        
        # Adicionando linha de tendência
        if len(monthly_data) > 1:
            z = np.polyfit(range(len(monthly_data)), monthly_data['valor'], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=monthly_data['mes_ano'],
                y=p(range(len(monthly_data))),
                mode='lines',
                name='Tendência',
                line=dict(color='red', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Tendência de Volume Mensal",
            xaxis_title="Mês",
            yaxis_title="Volume (R$)",
            height=500
        )
        
        content = dcc.Graph(figure=fig)
    
    return kpi_total, kpi_volume, kpi_approval, kpi_ticket, content

# Executando o servidor
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SERVIDOR DO DASHBOARD BANVIC")
    print("="*60)
    print("\n📊 Acesse o dashboard em: http://localhost:8050")
    print("🛑 Para parar o servidor, pressione Ctrl+C\n")
    
    app.run_server(debug=True, port=8050)