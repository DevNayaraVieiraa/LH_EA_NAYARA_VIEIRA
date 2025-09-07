# 📊 Projeto de Análise de Dados - Desafio BanVic 🏦

## Contexto: A Jornada de Dados do Banco Vitória (BanVic)

Este projeto simula um desafio de analytics para o Banco Vitória (BanVic), uma instituição financeira fundada em São Paulo em 2010. Com uma visão inovadora e uma equipe de 100 colaboradores, o BanVic busca amadurecer sua cultura de dados para elevar a organização a um novo patamar.

A CEO, Sofia Oliveira, acredita que o uso estratégico de dados é a chave para otimizar operações e melhorar a experiência do cliente. No entanto, existe um ceticismo interno, principalmente por parte da Diretora Comercial, Camila Diniz, que prefere investir em estratégias de marketing já conhecidas.

## 🎯 O Desafio

O objetivo central deste projeto é realizar uma análise piloto nos dados de crédito do BanVic para demonstrar o valor tangível que uma cultura orientada a dados pode trazer. O desafio consiste em manipular, analisar e visualizar os dados fornecidos para gerar um relatório com indicadores de performance, respondendo a perguntas de negócio e convencendo as partes interessadas sobre a importância da iniciativa.

## ❓ Perguntas de Negócio a Serem Respondidas

Para guiar a análise e demonstrar o potencial do projeto, buscamos responder às seguintes questões:

1. **Análise de Transações por Tempo**: Qual o dia da semana com maior média de transações aprovadas e maior volume financeiro movimentado?

2. **Hipótese de Sazonalidade**: É verdade que o volume médio de transações é maior em meses pares (Fevereiro, Abril, etc.) do que em meses ímpares?

3. **Desempenho das Agências**: Quais agências estão performando acima ou abaixo da média nos últimos 6 meses? Qual o ranking das 3 melhores e 3 piores agências em número de transações?

4. **Enriquecimento com Dados Externos**: Existe correlação entre a cotação do dólar e o volume/valor das transações do BanVic? Que outras fontes de dados públicos podem agregar valor ao negócio?

## 🛠️ Ferramentas Utilizadas

Para a execução deste projeto, foram utilizadas as seguintes tecnologias e ferramentas:

- **Linguagem de Programação**: Python
  - Pandas (manipulação de dados)
  - Matplotlib e Seaborn (visualizações)
  - Requests (APIs externas)
- **Ferramenta de BI**: Power BI (dashboard interativo)
- **Ambiente de Desenvolvimento**: Jupyter Notebook
- **Banco de Dados**: SQLite para consultas locais
- **Dados Externos**: API do Banco Central do Brasil (cotação USD/BRL)
- **Outros**: Excel para validações pontuais

## 📂 Estrutura do Repositório

O projeto está organizado da seguinte forma para facilitar a navegação e o entendimento:

```
├── dados/
│   ├── raw/                    # Dados brutos originais do desafio
│   └── processed/              # Dados tratados e prontos para análise
├── notebooks/
│   └── 01_analise_exploratoria.ipynb  # Notebook com toda a análise passo a passo
├── relatorio/
│   └── Relatorio_Final_BanVic.pdf     # Relatório final em PDF com as conclusões
├── dashboard/
│   └── Dashboard_BanVic.pbix          # Dashboard Power BI desenvolvido
└── README.md                          # Documentação do projeto
```

## 📈 Análises e Entregáveis

Este projeto compreende as seguintes entregas, conforme solicitado no desafio:

### 1. **Análise Exploratória e Argumentação**
Investigação inicial dos dados para entender sua estrutura, qualidade e potencial para responder às perguntas de negócio. Desenvolvimento de argumentos para convencer a Diretora Comercial sobre o valor de uma área de BI.

### 2. **Definição de Indicadores (KPIs)**
Estabelecimento dos principais indicadores de performance que respondem às demandas estratégicas do banco, incluindo métricas de volume, valor e performance temporal.

### 3. **Construção da Dimensão de Datas**
Criação de uma tabela dim_dates robusta para permitir análises temporais avançadas, incluindo:
- Análise por dia da semana
- Validação da hipótese de meses pares vs ímpares
- Proposição de análises adicionais com valor de negócio

### 4. **Enriquecimento com Dados Externos**
- Integração com dados de cotação do dólar (Banco Central)
- Análise de correlação entre câmbio e transações
- Proposição de outras fontes de dados públicos relevantes

### 5. **Ranking de Performance das Agências**
Análise focada no desempenho das agências nos últimos 6 meses para identificar:
- Top 3 agências com maior volume de transações
- 3 agências com menor performance
- Justificativas e recomendações baseadas nos dados

### 6. **Relatório Executivo em PDF**
Documento consolidado contendo:
- Respostas a todas as perguntas do desafio
- Processos de transformação e tratamento aplicados
- Dashboard dos principais KPIs
- Análises para suporte à tomada de decisão
- Conclusões e recomendações estratégicas para a CEO
- Justificativa das ferramentas adotadas

### 7. **Vídeo Explicativo**
Gravação detalhando o planejamento e execução de todas as atividades do desafio.

🎥 **[Link do Vídeo Explicativo](INSERIR_LINK_GOOGLE_DRIVE_AQUI)**

## 🔍 Principais Insights Descobertos

### Análise Temporal
- **Dia da semana com maior volume**: [INSERIR RESULTADO]
- **Validação da hipótese dos meses pares**: [INSERIR CONCLUSÃO]

### Performance das Agências
- **Top 3 agências**: [INSERIR RANKING]
- **Bottom 3 agências**: [INSERIR RANKING]

### Correlação com Dados Externos
- **Correlação USD/BRL vs Transações**: [INSERIR RESULTADO]
- **Outras fontes identificadas**: [LISTAR FONTES PROPOSTAS]

## 💡 Conclusões e Recomendações

Com base nas análises realizadas, foi possível demonstrar o valor tangível que uma cultura orientada a dados pode trazer para o BanVic. Os insights gerados permitem:

- **Otimização operacional** através do entendimento de padrões temporais
- **Melhoria na alocação de recursos** entre agências
- **Decisões estratégicas informadas** com base em dados externos
- **Segmentação mais eficiente** de clientes e produtos

Este projeto piloto serve como um argumento convincente para a implementação de uma área de Business Intelligence robusta no banco, demonstrando que o investimento em dados gera retorno mensurável e sustentável.

## 📋 Como Reproduzir Este Projeto

1. Clone este repositório
2. Instale as dependências: `pip install pandas matplotlib seaborn requests`
3. Execute o notebook `01_analise_exploratoria.ipynb`
4. Abra o dashboard `Dashboard_BanVic.pbix` no Power BI
5. Consulte o relatório final em PDF para conclusões detalhadas

---

**Desenvolvido por**: Nayara Vieira  
**Data**: Setembro 2025  
**Contexto**: Desafio de Engenharia de Analytics - Lighthouse Program