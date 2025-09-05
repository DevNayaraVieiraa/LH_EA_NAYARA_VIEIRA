"""
Script de Integração Python com Power BI
Este script prepara e transforma os dados para uso no Power BI
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def prepare_data_for_powerbi():
    """
    Prepara todos os datasets necessários para o Power BI
    """
    
    print("Preparando dados para Power BI...")
    
    # 1. Carregar dados originais
    df_agencias = pd.read_excel('data/tb_agencias.xlsx')
    df_clientes = pd.read_excel('data/tb_clientes.xlsx')
    df_transacoes = pd.read_excel('data/tb_transacoes.xlsx')
    
    # 2. Criar dataset consolidado
    df_fato = df_transacoes.merge(
        df_clientes[['cliente_id', 'nome_cliente', 'cidade_cliente']], 
        on='cliente_id', 
        how='left'
    ).merge(
        df_agencias[['agencia_id', 'nome_agencia', 'cidade_agencia']], 
        on='agencia_id', 
        how='left'
    )
    
    # 3. Adicionar colunas calculadas
    df_fato['data_transacao'] = pd.to_datetime(df_fato['data_transacao'])
    df_fato['ano'] = df_fato['data_transacao'].dt.year
    df_fato['mes'] = df_fato['data_transacao'].dt.month
    df_fato['dia'] = df_fato['data_transacao'].dt.day
    df_fato['trimestre'] = df_fato['data_transacao'].dt.quarter
    df_fato['semana_ano'] = df_fato['data_transacao'].dt.isocalendar().week
    df_fato['dia_semana'] = df_fato['data_transacao'].dt.dayofweek + 1
    df_fato['nome_dia_semana'] = df_fato['data_transacao'].dt.day_name()
    df_fato['nome_mes'] = df_fato['data_transacao'].dt.month_name()
    df_fato['eh_fim_semana'] = (df_fato['dia_semana'] >= 6).astype(int)
    df_fato['mes_par'] = (df_fato['mes'] % 2 == 0).astype(int)
    df_fato['status_aprovado'] = (df_fato['status'] == 'Aprovada').astype(int)
    
    # 4. Criar dimensão de tempo
    min_date = df_fato['data_transacao'].min()
    max_date = df_fato['data_transacao'].max()
    
    dim_tempo = pd.DataFrame({
        'data': pd.date_range(start=min_date, end=max_date, freq='D')
    })
    
    dim_tempo['ano'] = dim_tempo['data'].dt.year
    dim_tempo['mes'] = dim_tempo['data'].dt.month
    dim_tempo['dia'] = dim_tempo['data'].dt.day
    dim_tempo['trimestre'] = dim_tempo['data'].dt.quarter
    dim_tempo['semana_ano'] = dim_tempo['data'].dt.isocalendar().week
    dim_tempo['dia_semana'] = dim_tempo['data'].dt.dayofweek + 1
    dim_tempo['nome_dia_semana'] = dim_tempo['data'].dt.day_name()
    dim_tempo['nome_mes'] = dim_tempo['data'].dt.month_name()
    dim_tempo['nome_mes_abrev'] = dim_tempo['data'].dt.strftime('%b')
    dim_tempo['ano_mes'] = dim_tempo['data'].dt.strftime('%Y-%m')
    dim_tempo['data_completa'] = dim_tempo['data'].dt.strftime('%d/%m/%Y')
    dim_tempo['eh_fim_semana'] = (dim_tempo['dia_semana'] >= 6).astype(int)
    dim_tempo['eh_dia_util'] = (~dim_tempo['eh_fim_semana'].astype(bool)).astype(int)
    dim_tempo['mes_par'] = (dim_tempo['mes'] % 2 == 0).astype(int)
    
    # 5. Criar medidas agregadas por agência
    metricas_agencia = df_fato.groupby(['agencia_id', 'nome_agencia', 'cidade_agencia']).agg({
        'transacao_id': 'count',
        'valor': ['sum', 'mean', 'median', 'std'],
        'status_aprovado': 'mean'
    }).round(2)
    
    metricas_agencia.columns = ['total_transacoes', 'volume_total', 'valor_medio', 
                                'valor_mediano', 'desvio_padrao', 'taxa_aprovacao']
    metricas_agencia['taxa_aprovacao'] = (metricas_agencia['taxa_aprovacao'] * 100).round(1)
    metricas_agencia = metricas_agencia.reset_index()
    
    # Classificar agências
    metricas_agencia['classificacao'] = pd.qcut(
        metricas_agencia['volume_total'], 
        q=3, 
        labels=['Pequeno Porte', 'Médio Porte', 'Grande Porte']
    )
    
    # 6. Criar medidas agregadas por cliente
    metricas_cliente = df_fato.groupby(['cliente_id', 'nome_cliente', 'cidade_cliente']).agg({
        'transacao_id': 'count',
        'valor': ['sum', 'mean'],
        'status_aprovado': 'mean',
        'agencia_id': 'nunique'
    }).round(2)
    
    metricas_cliente.columns = ['total_transacoes', 'volume_total', 'ticket_medio', 
                                'taxa_aprovacao', 'agencias_utilizadas']
    metricas_cliente['taxa_aprovacao'] = (metricas_cliente['taxa_aprovacao'] * 100).round(1)
    metricas_cliente = metricas_cliente.reset_index()
    
    # Segmentar clientes
    metricas_cliente['segmento'] = pd.qcut(
        metricas_cliente['volume_total'],
        q=4,
        labels=['Bronze', 'Prata', 'Ouro', 'Diamante']
    )
    
    # 7. Criar análise por período
    analise_periodo = df_fato.groupby(['ano', 'mes', 'nome_mes']).agg({
        'transacao_id': 'count',
        'valor': ['sum', 'mean'],
        'status_aprovado': 'mean',
        'cliente_id': 'nunique',
        'agencia_id': 'nunique'
    }).round(2)
    
    analise_periodo.columns = ['total_transacoes', 'volume_total', 'valor_medio',
                               'taxa_aprovacao', 'clientes_ativos', 'agencias_ativas']
    analise_periodo['taxa_aprovacao'] = (analise_periodo['taxa_aprovacao'] * 100).round(1)
    analise_periodo = analise_periodo.reset_index()
    
    # 8. Análise dos últimos 6 meses
    data_corte = df_fato['data_transacao'].max() - pd.DateOffset(months=6)
    df_ultimos_6_meses = df_fato[df_fato['data_transacao'] >= data_corte]
    
    ranking_agencias_6m = df_ultimos_6_meses.groupby('nome_agencia').agg({
        'transacao_id': 'count',
        'valor': 'sum'
    }).round(2)
    ranking_agencias_6m.columns = ['transacoes_6m', 'volume_6m']
    ranking_agencias_6m = ranking_agencias_6m.sort_values('volume_6m', ascending=False)
    ranking_agencias_6m['ranking'] = range(1, len(ranking_agencias_6m) + 1)
    ranking_agencias_6m = ranking_agencias_6m.reset_index()
    
    # 9. Exportar todos os datasets
    print("Exportando datasets...")
    
    # Criar pasta se não existir
    import os
    if not os.path.exists('powerbi_data'):
        os.makedirs('powerbi_data')
    
    # Exportar para CSV (melhor compatibilidade com Power BI)
    df_fato.to_csv('powerbi_data/fato_transacoes.csv', index=False, encoding='utf-8-sig')
    dim_tempo.to_csv('powerbi_data/dim_tempo.csv', index=False, encoding='utf-8-sig')
    df_agencias.to_csv('powerbi_data/dim_agencias.csv', index=False, encoding='utf-8-sig')
    df_clientes.to_csv('powerbi_data/dim_clientes.csv', index=False, encoding='utf-8-sig')
    metricas_agencia.to_csv('powerbi_data/metricas_agencia.csv', index=False, encoding='utf-8-sig')
    metricas_cliente.to_csv('powerbi_data/metricas_cliente.csv', index=False, encoding='utf-8-sig')
    analise_periodo.to_csv('powerbi_data/analise_periodo.csv', index=False, encoding='utf-8-sig')
    ranking_agencias_6m.to_csv('powerbi_data/ranking_agencias_6m.csv', index=False, encoding='utf-8-sig')
    
    print("✅ Dados preparados com sucesso!")
    
    return {
        'fato_transacoes': df_fato,
        'dim_tempo': dim_tempo,
        'dim_agencias': df_agencias,
        'dim_clientes': df_clientes,
        'metricas_agencia': metricas_agencia,
        'metricas_cliente': metricas_cliente,
        'analise_periodo': analise_periodo,
        'ranking_agencias_6m': ranking_agencias_6m
    }

def create_powerbi_measures():
    """
    Cria arquivo com medidas DAX para Power BI
    """
    
    measures = """
================================================================================
MEDIDAS DAX PARA POWER BI - BANVIC
================================================================================

Copie e cole estas medidas no Power BI Desktop
Para criar uma nova medida: Tabela > Nova Medida

--------------------------------------------------------------------------------
1. MEDIDAS BÁSICAS
--------------------------------------------------------------------------------

Total_Transacoes = 
COUNTROWS('fato_transacoes')

Volume_Total = 
SUM('fato_transacoes'[valor])

Ticket_Medio = 
AVERAGE('fato_transacoes'[valor])

Total_Clientes = 
DISTINCTCOUNT('fato_transacoes'[cliente_id])

Total_Agencias = 
DISTINCTCOUNT('fato_transacoes'[agencia_id])

--------------------------------------------------------------------------------
2. MEDIDAS DE APROVAÇÃO
--------------------------------------------------------------------------------

Transacoes_Aprovadas = 
CALCULATE(
    COUNTROWS('fato_transacoes'),
    'fato_transacoes'[status] = "Aprovada"
)

Taxa_Aprovacao = 
DIVIDE(
    [Transacoes_Aprovadas],
    [Total_Transacoes],
    0
) * 100

Volume_Aprovado = 
CALCULATE(
    SUM('fato_transacoes'[valor]),
    'fato_transacoes'[status] = "Aprovada"
)

--------------------------------------------------------------------------------
3. MEDIDAS TEMPORAIS
--------------------------------------------------------------------------------

Transacoes_Mes_Atual = 
CALCULATE(
    [Total_Transacoes],
    MONTH('fato_transacoes'[data_transacao]) = MONTH(TODAY()),
    YEAR('fato_transacoes'[data_transacao]) = YEAR(TODAY())
)

Transacoes_Mes_Anterior = 
CALCULATE(
    [Total_Transacoes],
    DATEADD('dim_tempo'[data], -1, MONTH)
)

Crescimento_MoM = 
VAR MesAtual = [Transacoes_Mes_Atual]
VAR MesAnterior = [Transacoes_Mes_Anterior]
RETURN
DIVIDE(MesAtual - MesAnterior, MesAnterior, 0) * 100

Transacoes_YTD = 
TOTALYTD(
    [Total_Transacoes],
    'dim_tempo'[data]
)

Volume_YTD = 
TOTALYTD(
    [Volume_Total],
    'dim_tempo'[data]
)

--------------------------------------------------------------------------------
4. MEDIDAS DE RANKING
--------------------------------------------------------------------------------

Ranking_Agencias_Volume = 
RANKX(
    ALL('dim_agencias'[nome_agencia]),
    [Volume_Total],
    ,
    DESC
)

Ranking_Clientes_Volume = 
RANKX(
    ALL('dim_clientes'[nome_cliente]),
    [Volume_Total],
    ,
    DESC
)

Top10_Agencias = 
IF(
    [Ranking_Agencias_Volume] <= 10,
    [Volume_Total],
    BLANK()
)

--------------------------------------------------------------------------------
5. MEDIDAS DE SEGMENTAÇÃO
--------------------------------------------------------------------------------

Segmento_Cliente = 
SWITCH(
    TRUE(),
    [Volume_Total] > 10000, "Diamante",
    [Volume_Total] > 5000, "Ouro",
    [Volume_Total] > 1000, "Prata",
    "Bronze"
)

Categoria_Agencia = 
SWITCH(
    TRUE(),
    [Total_Transacoes] > 1000, "Alta Performance",
    [Total_Transacoes] > 500, "Média Performance",
    "Baixa Performance"
)

--------------------------------------------------------------------------------
6. MEDIDAS DE COMPARAÇÃO
--------------------------------------------------------------------------------

Volume_Dia_Semana = 
AVERAGEX(
    VALUES('dim_tempo'[nome_dia_semana]),
    [Volume_Total]
)

Volume_Fim_Semana = 
CALCULATE(
    [Volume_Total],
    'dim_tempo'[eh_fim_semana] = 1
)

Volume_Dia_Util = 
CALCULATE(
    [Volume_Total],
    'dim_tempo'[eh_fim_semana] = 0
)

Diferenca_FimSemana_DiaUtil = 
[Volume_Fim_Semana] - [Volume_Dia_Util]

--------------------------------------------------------------------------------
7. MEDIDAS AVANÇADAS
--------------------------------------------------------------------------------

Media_Movel_30D = 
AVERAGEX(
    DATESINPERIOD(
        'dim_tempo'[data],
        LASTDATE('dim_tempo'[data]),
        -30,
        DAY
    ),
    [Volume_Total]
)

Desvio_Padrao_Volume = 
STDEV.P('fato_transacoes'[valor])

CV_Volume = 
DIVIDE(
    [Desvio_Padrao_Volume],
    [Ticket_Medio],
    0
) * 100

Percentil_90_Volume = 
PERCENTILE.INC(
    'fato_transacoes'[valor],
    0.9
)

--------------------------------------------------------------------------------
8. MEDIDAS DOS ÚLTIMOS 6 MESES
--------------------------------------------------------------------------------

Volume_Ultimos_6M = 
CALCULATE(
    [Volume_Total],
    DATESINPERIOD(
        'dim_tempo'[data],
        LASTDATE('dim_tempo'[data]),
        -6,
        MONTH
    )
)

Transacoes_Ultimos_6M = 
CALCULATE(
    [Total_Transacoes],
    DATESINPERIOD(
        'dim_tempo'[data],
        LASTDATE('dim_tempo'[data]),
        -6,
        MONTH
    )
)

Taxa_Aprovacao_6M = 
CALCULATE(
    [Taxa_Aprovacao],
    DATESINPERIOD(
        'dim_tempo'[data],
        LASTDATE('dim_tempo'[data]),
        -6,
        MONTH
    )
)

--------------------------------------------------------------------------------
9. MEDIDAS DE PERFORMANCE
--------------------------------------------------------------------------------

Eficiencia_Agencia = 
DIVIDE(
    [Volume_Aprovado],
    [Total_Transacoes],
    0
)

ROI_Cliente = 
DIVIDE(
    [Volume_Total],
    [Total_Transacoes],
    0
)

Penetracao_Mercado = 
DIVIDE(
    [Total_Clientes],
    CALCULATE([Total_Clientes], ALL('fato_transacoes')),
    0
) * 100

--------------------------------------------------------------------------------
10. FORMATAÇÃO CONDICIONAL (PARA USAR EM TABELAS)
--------------------------------------------------------------------------------

Cor_Performance = 
SWITCH(
    TRUE(),
    [Taxa_Aprovacao] >= 80, "#2ECC71",  // Verde
    [Taxa_Aprovacao] >= 60, "#F39C12",  // Amarelo
    "#E74C3C"  // Vermelho
)

Icone_Tendencia = 
VAR Atual = [Volume_Total]
VAR Anterior = [Transacoes_Mes_Anterior]
RETURN
IF(
    Atual > Anterior, 
    "📈",
    IF(Atual < Anterior, "📉", "➡️")
)

================================================================================
"""
    
    # Salvar medidas DAX
    with open('powerbi_data/medidas_dax.txt', 'w', encoding='utf-8') as f:
        f.write(measures)
    
    print("✅ Arquivo de medidas DAX criado: powerbi_data/medidas_dax.txt")

def create_powerbi_instructions():
    """
    Cria instruções detalhadas para importar no Power BI
    """
    
    instructions = """
================================================================================
INSTRUÇÕES PARA IMPORTAR NO POWER BI
================================================================================

📌 PASSO 1: ABRIR O POWER BI DESKTOP
----------------------------------------
1. Abra o Power BI Desktop
2. Clique em "Obter dados" ou "Get Data"
3. Selecione "Texto/CSV" ou "Text/CSV"

📌 PASSO 2: IMPORTAR OS ARQUIVOS CSV
----------------------------------------
Importe os seguintes arquivos na ordem:

1. fato_transacoes.csv (Tabela principal de fatos)
2. dim_tempo.csv (Dimensão de tempo)
3. dim_agencias.csv (Dimensão de agências)
4. dim_clientes.csv (Dimensão de clientes)
5. metricas_agencia.csv (Métricas agregadas por agência)
6. metricas_cliente.csv (Métricas agregadas por cliente)
7. analise_periodo.csv (Análise por período)
8. ranking_agencias_6m.csv (Ranking últimos 6 meses)

Para cada arquivo:
- Clique em "Carregar" após visualizar
- Certifique-se que a codificação está como UTF-8

📌 PASSO 3: CRIAR RELACIONAMENTOS
----------------------------------------
Vá em "Modelo" ou "Model" e crie os seguintes relacionamentos:

1. fato_transacoes[agencia_id] → dim_agencias[agencia_id]
   Tipo: Muitos para Um (Many to One)

2. fato_transacoes[cliente_id] → dim_clientes[cliente_id]
   Tipo: Muitos para Um (Many to One)

3. fato_transacoes[data_transacao] → dim_tempo[data]
   Tipo: Muitos para Um (Many to One)

📌 PASSO 4: CRIAR MEDIDAS DAX
----------------------------------------
1. Selecione a tabela "fato_transacoes"
2. Vá em "Modelagem" > "Nova Medida"
3. Copie e cole cada medida do arquivo "medidas_dax.txt"
4. Pressione Enter para criar cada medida

📌 PASSO 5: CRIAR VISUALIZAÇÕES
----------------------------------------

Dashboard 1 - Visão Geral:
- Cartões de KPI: Total Transações, Volume Total, Taxa Aprovação, Ticket Médio
- Gráfico de Linhas: Volume ao longo do tempo
- Gráfico de Barras: Top 10 Agências
- Gráfico de Pizza: Segmentação de Clientes

Dashboard 2 - Análise Temporal:
- Gráfico de Área: Evolução diária do volume
- Gráfico de Colunas: Comparação mensal
- Tabela: Métricas por dia da semana
- Gráfico de Linhas: Média móvel 30 dias

Dashboard 3 - Performance de Agências:
- Tabela: Ranking de agências com métricas
- Gráfico de Dispersão: Volume vs Taxa de Aprovação
- Mapa: Distribuição geográfica (se tiver dados de localização)
- Gráfico de Barras Empilhadas: Status por agência

Dashboard 4 - Análise de Clientes:
- Gráfico Treemap: Segmentação de clientes
- Histograma: Distribuição de valores
- Tabela: Top 20 clientes
- Gráfico de Funil: Conversão por segmento

📌 PASSO 6: APLICAR FORMATAÇÃO
----------------------------------------
1. Selecione cada visualização
2. Vá em "Formato" ou "Format"
3. Configure:
   - Títulos descritivos
   - Cores consistentes (use o padrão BanVic)
   - Rótulos de dados quando relevante
   - Legendas explicativas

📌 PASSO 7: CONFIGURAR FILTROS
----------------------------------------
Adicione os seguintes filtros de página:
- Data (usando dim_tempo)
- Agência (usando dim_agencias)
- Status da transação
- Segmento de cliente

📌 PASSO 8: CRIAR PÁGINA DE ANÁLISE DETALHADA
----------------------------------------
1. Adicione uma nova página
2. Nome: "Análise Detalhada"
3. Adicione:
   - Tabela dinâmica com drill-down
   - Filtros interativos
   - Botões de navegação entre páginas

📌 PASSO 9: PUBLICAR NO POWER BI SERVICE
----------------------------------------
1. Salve o arquivo .pbix
2. Clique em "Publicar"
3. Selecione o workspace desejado
4. Configure a atualização automática dos dados

📌 DICAS IMPORTANTES
----------------------------------------
✓ Use a paleta de cores do BanVic
✓ Mantenha consistência visual entre páginas
✓ Adicione tooltips personalizados
✓ Configure drill-through entre visualizações
✓ Use bookmarks para diferentes visões
✓ Teste a performance com grandes volumes
✓ Configure RLS (Row Level Security) se necessário

📌 SOLUÇÃO DE PROBLEMAS
----------------------------------------
❌ Erro de codificação: Abra o CSV no Excel e salve como UTF-8
❌ Relacionamentos não funcionam: Verifique tipos de dados
❌ Medidas com erro: Verifique nomes de colunas e tabelas
❌ Performance lenta: Use modo de importação ao invés de DirectQuery

================================================================================
"""
    
    # Salvar instruções
    with open('powerbi_data/instrucoes_powerbi.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Arquivo de instruções criado: powerbi_data/instrucoes_powerbi.txt")

# Função principal
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 PREPARAÇÃO DE DADOS PARA POWER BI - BANVIC")
    print("="*60 + "\n")
    
    # Preparar dados
    datasets = prepare_data_for_powerbi()
    
    # Criar medidas DAX
    create_powerbi_measures()
    
    # Criar instruções
    create_powerbi_instructions()
    
    print("\n" + "="*60)
    print("✅ PREPARAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\n📁 Arquivos criados na pasta 'powerbi_data/':")
    print("   - 8 arquivos CSV com dados preparados")
    print("   - medidas_dax.txt (medidas para copiar no Power BI)")
    print("   - instrucoes_powerbi.txt (passo a passo detalhado)")
    print("\n🎯 Próximo passo: Siga as instruções em 'instrucoes_powerbi.txt'")
    print("="*60 + "\n")