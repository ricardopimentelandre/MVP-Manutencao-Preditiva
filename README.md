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

O **Random Forest original** apresentou o melhor desempenho entre os modelos avaliados e foi selecionado para compor o MVP.

## Sistema de Suporte à Decisão

O sistema recebe as condições operacionais da máquina e utiliza o modelo treinado para classificar a situação como possível ocorrência de falha ou operação sem falha.

A saída funciona como apoio à equipe de manutenção e não substitui a decisão do responsável.

## Arquivo principal

`MVP_Manutencao_Preditiva.ipynb`
