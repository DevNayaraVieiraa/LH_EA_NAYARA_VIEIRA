# 📊 Projeto de Análise de Dados - Desafio BanVic

## 🏦 Contexto: A Jornada de Dados do Banco Vitória (BanVic)

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

Para a execução deste projeto, foram utilizadas as seguintes tecnologias:

- **Linguagem de Programação**: Python (Pandas, Matplotlib, Seaborn)
- **Ferramenta de BI**: Power BI
- **Ambiente de Desenvolvimento**: VS Code
- **Controle de Versão**: Git/GitHub
- **Dados Externos**: API do Banco Central do Brasil

## 📂 Estrutura do Repositório

```
├── scripts/
│   ├── fix_csv_issues.py                    # Script para diagnóstico e correção de dados
│   ├── banvic_powerbi_integration_fixed.py  # Pipeline de preparação para Power BI
│   └── get_taxa_cambio.py                   # Extração de dados do Banco Central
├── dashboard/
│   └── Dashboard_BanVic_Final.pbix          # Dashboard Power BI
├── relatorio/
│   └── Relatorio_Final_BanVic.pdf           # Relatório completo da análise
└── README.md                                # Documentação do projeto
```

## 📈 Análises e Entregáveis

Este projeto compreende as seguintes entregas:

1. **Análise Exploratória e Definição de KPIs**: Investigação inicial dos dados para entender sua estrutura e definir os principais indicadores de negócio.

2. **Construção da dim_dates**: Criação de uma dimensão de datas para permitir análises temporais robustas, como performance por dia da semana e validação da hipótese dos meses pares/ímpares.

3. **Enriquecimento com Dados Externos**: Análise de correlação entre a cotação do dólar (Banco Central do Brasil) e as transações do BanVic.

4. **Ranking de Performance das Agências**: Análise focada no desempenho das agências para identificar as de maior e menor volume de transações.

5. **Dashboard de KPIs**: Painel interativo em Power BI, permitindo visualização detalhada dos indicadores por data, agência e cliente.

6. **Relatório em PDF**: Documento final consolidando todas as análises, processos de tratamento, conclusões e recomendações estratégicas.

## 🔍 Principais Resultados

### KPIs Identificados
- **Total de Transações**: 3 bilhões
- **Volume Total Movimentado**: 5E+18
- **Ticket Médio**: 75,80 trilhões
- **Agências Ativas**: Múltiplas unidades em operação

### Insights Principais
- **Agência Digital** lidera o ranking com 33.167 transações
- **Sexta-feira** apresenta maior média de transações (70M)
- **Hipótese refutada**: Meses pares não apresentam volume significativamente maior que ímpares
- **Taxa de câmbio**: Correlação limitada com volume de transações

## 💡 Conclusão e Recomendações

Com base nas análises realizadas, foi possível gerar insights valiosos e propor recomendações estratégicas para o BanVic. Os resultados demonstram como a análise de dados pode direcionar decisões mais assertivas, otimizar a performance das agências e aprimorar a segmentação de clientes. Este projeto piloto serve como um forte argumento para convencer a diretoria sobre o potencial de uma área de Business Intelligence na empresa.

### Recomendações Estratégicas
1. **Foco na Agência Digital**: Investigar fatores de sucesso para replicar em outras unidades
2. **Otimização de Sextas-feiras**: Alocar recursos adicionais no dia de maior movimento
3. **Revisão de Estratégias Sazonais**: Ajustar planejamento baseado em dados reais, não suposições
4. **Investimento em BI**: Implementar cultura data-driven para decisões estratégicas

---

**Desenvolvido para o Desafio de Engenharia de Analytics - Indicium**