# MVP – Sistema de Suporte à Decisão para Manutenção Preditiva

Este projeto apresenta um Mínimo Produto Viável (MVP) de um **Sistema de Suporte à Decisão para Manutenção Preditiva**, utilizando técnicas de Machine Learning para identificar condições operacionais associadas à ocorrência de falhas em máquinas.

## Objetivo

Desenvolver um modelo capaz de analisar condições operacionais de uma máquina e auxiliar a equipe de manutenção na identificação de situações que demandam maior atenção.

## Base de dados

Foi utilizado o **AI4I 2020 Predictive Maintenance Dataset**, disponibilizado pelo UCI Machine Learning Repository.

O modelo utiliza as seguintes variáveis:

* Tipo do produto;
* Temperatura do ar;
* Temperatura do processo;
* Velocidade de rotação;
* Torque;
* Desgaste da ferramenta.

A variável alvo indica a ocorrência ou não de falha da máquina.

## Modelos avaliados

Foram avaliados:

* Regressão Logística;
* Random Forest;
* Random Forest com balanceamento de classes.

Na partição de teste registrada no notebook, o **Random Forest sem balanceamento apresentou o maior F1-score para a classe de falha** entre os modelos avaliados e foi selecionado para compor o MVP. Essa observação depende do ambiente de reprodução e não demonstra superioridade geral.

## Reprodução verificada (09/11/2026)

Uma reprodução controlada no Google Colab, em **9 de novembro de 2026**, com dados oficiais do UCI AI4I 2020 (identificador 601), reproduziu as métricas e matrizes de confusão registradas no notebook original (commit `303a80b`). Foram utilizados **10.000 registros**, com **339 falhas**, e conjunto de teste com **2.000 registros**.

| Modelo | Acurácia | Precisão (falha) | Recall (falha) | F1 (falha) |
| --- | ---: | ---: | ---: | ---: |
| Regressão Logística | 0,968 | 0,636 | 0,103 | 0,177 |
| Random Forest | 0,982 | 0,900 | 0,529 | 0,667 |
| Random Forest balanceado | 0,981 | 0,969 | 0,456 | 0,620 |

**Ambiente reproduzido:** Python 3.13.18 e scikit-learn 1.8.0, com as demais versões registradas em [`requirements.txt`](requirements.txt). Este é o ambiente da **reprodução**, e não há registro confiável da versão do scikit-learn utilizada na execução original. Os resultados do Random Forest balanceado podem variar entre versões da biblioteca.

- Relatório de execução, métricas e versões: [`evidencias/relatorio_reproducao_ssd.json`](evidencias/relatorio_reproducao_ssd.json).
- Para tentar reproduzir os resultados, use ambiente compatível com Python 3.13, instale `pip install -r requirements.txt` e execute o notebook desde o início, com acesso à base oficial da UCI. A instalação do pacote `ucimlrepo` já está prevista na primeira célula do notebook.
- **Limitação metodológica:** a escolha do modelo foi feita com base na mesma partição de teste usada para reportar as métricas. Assim, a seleção e os resultados são exploratórios, e não uma validação independente ou industrial.

## Sistema de Suporte à Decisão

O sistema recebe as condições operacionais da máquina e utiliza o modelo treinado para classificar a situação como possível ocorrência de falha ou operação sem falha.

A saída funciona como apoio à equipe de manutenção e não substitui a decisão do responsável.

## Arquivo principal

`MVP_Manutencao_Preditiva.ipynb`
