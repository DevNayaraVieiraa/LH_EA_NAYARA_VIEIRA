# 📊 Projeto de Análise de Dados - Desafio BanVic 🏦

## 🏢 Contexto do Negócio

O **Banco Vitória (BanVic)** é uma instituição financeira fundada em 2010, em São Paulo. Conta com cerca de 100 colaboradores e hoje busca fortalecer sua cultura de dados para embasar decisões estratégicas.

**Personagens-chave:**

**Sofia Oliveira (CEO):** defende o uso de dados para melhorar operações e a experiência do cliente.

**Camila Diniz (Diretora Comercial):** ainda prefere métodos tradicionais, mas precisa enxergar na prática o valor dos dados.

**André Tech (Diretor de TI):** busca aplicar análises avançadas para otimizar processos internos.

**Lucas Johnson (Analista de Dados): ** idealizou este piloto para provar os ganhos que a análise pode trazer.

Este projeto é um piloto de **analytics**, criado para demonstrar de forma prática o impacto positivo que a inteligência de dados pode gerar no BanVic.

## 🎯 Objetivo do Desafio

O objetivo deste piloto é analisar de ponta a ponta os dados de crédito do **BanVic** e responder perguntas-chave do negócio. Vamos gerar indicadores, gráficos e insights acionáveis que comprovem para a diretoria que investir em dados traz retorno mensurável.

## ❓ Perguntas de Negócio Respondidas

### 🕐 Análise Temporal
1. **Dia da semana com maior movimento**  
   - Qual dia concentra mais transações aprovadas e maior volume financeiro?  

2. **Meses pares x meses ímpares**  
   - Há realmente mais transações em meses pares do que em ímpares?  

### 🏪 Performance Operacional
3. **Agências acima ou abaixo da média**  
   - Quais se destacaram nos últimos 6 meses?  

4. **Ranking de desempenho**  
   - Quem são as 3 melhores e as 3 piores agências?  

### 🌍 Dados Externos
5. **Impacto do dólar**  
   - Existe relação entre a cotação USD/BRL e as transações do banco?  

6. **Fontes externas de valor**  
   - Que outros dados públicos podem enriquecer futuras análises?  


## 🛠️ Stack Tecnológica

| Ferramenta            | Finalidade                                                                 |
|------------------------|----------------------------------------------------------------------------|
| **Python**             | Limpeza, exploração e análise de dados (Pandas, Matplotlib, Seaborn, Requests) |
| **Power BI**           | Construção de dashboards interativos para a diretoria                       |
| **SQLite**             | Consultas locais e validação de dados                                       |
| **Excel**              | Conferências e validações pontuais                                          |
| **API Banco Central**  | Coleta da cotação USD/BRL                                                   |
| **Jupyter Notebook**   | Ambiente para desenvolvimento e documentação da análise                     |


## 📂 Estrutura do Repositório

```
LH_EA_NAYARA_VIEIRA/
├── 📁 dados/
│   ├── raw/                     # Dados originais do BanVic
│   └── processed/               # Dados limpos e transformados
├── 📁 dashboard/
│   └── Dashboard_BanVic.pbix    # Dashboard executivo interativo
├── 📁 img/                      # Visualizações e gráficos
├── 📁 notebooks/
│   └── 01_analise_exploratoria.ipynb  # Análise completa
├── 📁 relatorio/
│   └── Relatorio_Final_BanVic.pdf     # Documento executivo
├── 📁 video/
│   └── [Link para Google Drive]        # Vídeo explicativo
└── README.md
```

## 📊 Principais Descobertas

### ⚡ **INSIGHT CRÍTICO**: Problema Operacional Grave
> **Só 3 de 10 agências estão ativas!**
>
> Em 2023, apenas 3 agências do BanVic registraram transações. A **Agência Digital** concentra 70% das operações, sinal de dependência excessiva e de falhas graves nas unidades físicas.

### 📈 Padrões Temporais

**🎯 Dia Mais Forte da Semana**
- Sexta-feira é o pico de transações  
- **Oportunidade**: Intensificar campanhas de fim de semana  

**📅 Sazonalidade Mensal**
- Diferenças claras entre meses pares e ímpares  
- Padrões úteis para planejamento de ações  

### 🏪 Ranking de Performance das Agências

**🏆 TOP 3 Agências (2º Sem/2023)**
1. **Agência Digital** – liderança isolada  
2. **Agência Matriz** – boa performance  
3. **Agência Centro** – terceira colocada  

**⚠️ Agências Inativas**
- 7 agências sem nenhuma transação  
- **Requer investigação imediata**  

### 💱 Dados Externos

**Dólar vs Transações**
- Correlação baixa  
- Outros fatores impactam mais  

**📋 Fontes Úteis para Expansão**
- **IBGE**: dados demográficos  
- **IPEA**: indicadores econômicos  
- **SERASA**: crédito do mercado  
- **BACEN**: informações do sistema financeiro  

## 💼 Valor para o Negócio

### Para a CEO Sofia Oliveira:
- ✅ Panorama claro das operações  
- ✅ Riscos críticos identificados  
- ✅ Base confiável para investimentos  

### Para a Diretora Camila Diniz:
- ✅ Segmentação temporal para campanhas  
- ✅ ROI mensurável por agência/região  
- ✅ Decisões baseadas em dados, não só intuição  

### Para o Diretor André Tech:
- ✅ Relatórios automatizados  
- ✅ Monitoramento em tempo real  
- ✅ Estrutura técnica para expansão  

## 🎯 Recomendações Estratégicas

### 🚨 **Curto Prazo - Agências Inativas**
1. Investigar as 7 agências sem atividade  
2. Definir plano de reativação ou fechamento  
3. Redirecionar recursos de baixa produtividade  

### 📊 **Médio Prazo - BI Estruturado**
1. Criar dashboard executivo permanente  
2. Automatizar coleta de dados externos  
3. Treinar times em cultura data-driven  

### 🎯 **Longo Prazo - Expansão**
1. Ampliar fontes de dados  
2. Desenvolver modelos preditivos  
3. Implementar segmentações avançadas 

**🎬 [Vídeo Explicativo](https://drive.google.com/file/d/10_6z3deDBhSuf5CYuMhbJ83QmQmzDEhN/view)**


## 🚀 Como Reproduzir Este Projeto

### 1. **Setup do Ambiente**
```bash
# Clone o repositório
git clone https://github.com/DevNayaraVieiraa/LH_EA_NAYARA_VIEIRA.git

# Instale dependências
pip install pandas matplotlib seaborn requests sqlite3
