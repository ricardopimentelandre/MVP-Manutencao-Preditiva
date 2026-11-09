# Perguntas de negócio e apoio à decisão — MVP Manutenção Preditiva

**Data da documentação:** 09/11/2026  
**Projeto:** Sistema de Suporte à Decisão para Manutenção Preditiva  
**Referência da implementação:** `MVP_Manutencao_Preditiva.ipynb` (commit original `303a80b`)  
**Ambiente de reprodução dos números:** Python 3.13.18, scikit-learn 1.8.0, conjunto oficial UCI AI4I 2020 (id 601); ver `evidencias/relatorio_reproducao_ssd.json`.

> **Transparência sobre a cronologia:** as perguntas abaixo foram **formalizadas retrospectivamente** para relacionar o problema já descrito no notebook original às métricas existentes. Não há registro de que tenham sido pré-registradas antes da escolha da base, do treinamento ou da seleção do modelo. Este documento não afirma o contrário.

## 1. Problema gerencial e decisão apoiada

**Usuário-alvo conceitual:** responsável técnico ou equipe de manutenção.  
**Problema:** quando recursos de inspeção são limitados, identificar condições operacionais que mereçam avaliação prioritária, sem transformar uma previsão estatística em ordem automática de parada.  
**Decisão apoiada pelo MVP:** receber uma classificação de uma condição informada e uma orientação textual para **priorizar avaliação** ou **manter acompanhamento**. A decisão final pertence à equipe de manutenção.

**Hipótese de avaliação retrospectivamente expressa (não pré-registrada):** as seis características operacionais do AI4I 2020 permitem identificar uma parcela das ocorrências de falha e gerar sinais para triagem humana; esses resultados, isoladamente, não validam automatização de manutenção.

## 2. Perguntas e respostas verificadas

### P1 — Qual é a frequência de falhas na base disponível e o que isso implica para a avaliação?

**Resultado:** 339 de 10.000 observações têm `Machine failure=1` (**3,39%**); 9.661 não têm falha (**96,61%**).  
**Evidência:** contagens do notebook e relatórios `relatorio_reproducao_ssd.json` / `relatorio_qualidade_dados.json`.  
**Implicação gerencial:** como eventos positivos são raros nesta base, acurácia isolada não é suficiente para decidir sobre um classificador; é necessário olhar recall, precisão, F1-score e erros de classificação.  
**Limite:** esta é a frequência de um conjunto **sintético**, não uma taxa de falhas de uma fábrica real.

### P2 — Qual das três configurações avaliadas oferece o maior F1-score para a classe de falha nesta partição?

| Configuração | Precisão (falha) | Recall (falha) | F1-score (falha) |
|---|---:|---:|---:|
| Regressão Logística | 0,636 | 0,103 | 0,177 |
| Random Forest sem pesos de classe | 0,900 | 0,529 | **0,667** |
| Random Forest com `class_weight="balanced"` | 0,969 | 0,456 | 0,620 |

**Resultado:** na partição documentada e no ambiente reproduzido com scikit-learn 1.8.0, o Random Forest sem balanceamento apresentou o maior F1-score e recall entre as três configurações.  
**Evidência:** células 27–28 do notebook e `evidencias/relatorio_reproducao_ssd.json`.  
**Decisão apoiada:** escolher esse modelo como **candidato demonstrativo** do MVP, não como vencedor universal.  
**Limites:** os modelos foram escolhidos e comparados na mesma partição de teste; não houve validação final independente, custos de erro ou intervalos de confiança. O Random Forest balanceado pode apresentar resultados distintos em outras versões do scikit-learn; a versão usada na execução original não foi registrada.

### P3 — Quantas falhas são sinalizadas e quantos alertas incorretos ou falhas não identificadas restam?

Na avaliação do Random Forest sem balanceamento sobre **2.000 registros de teste** (68 falhas reais e 1.932 operações sem falha):

| Resultado | Quantidade |
|---|---:|
| Falhas corretamente identificadas (VP) | 36 |
| Alertas sem falha real (FP) | 4 |
| Falhas não identificadas (FN) | 32 |
| Operações sem falha corretamente classificadas (VN) | 1.928 |

**Resultado:** entre 40 alertas positivos, 36 eram falhas reais (**precisão de 90%**). Das 68 falhas reais, 36 foram detectadas (**recall de 52,9%**) e 32 não foram (**47,1%**).  
**Evidência:** matriz de confusão do notebook e relatório de reprodução.  
**Decisão apoiada:** sinais positivos podem **orientar uma fila de avaliação técnica**; sinais negativos **não liberam** a máquina de outras rotinas de segurança ou acompanhamento.  
**Limite:** não existe no MVP avaliação do custo de falso positivo versus falso negativo, capacidade de equipe, criticidade de equipamento, histórico real ou escolha de limiar operacional.

### P4 — Como o MVP converte uma previsão em orientação compreensível para a equipe?

A função `avaliar_maquina` recebe **tipo do produto, temperatura do ar, temperatura do processo, rotação, torque e desgaste da ferramenta**. Em seguida:
1. `modelo_rf.predict` indica a classe prevista.
2. `modelo_rf.predict_proba` exibe um **escore do classificador** para a classe de falha, **não calibrado** como probabilidade real.
3. Se a classe prevista é **1**, imprime “POSSÍVEL FALHA IDENTIFICADA” e recomenda **priorizar a avaliação da condição pela equipe de manutenção**.
4. Se a classe prevista é **0**, imprime “NÃO FOI IDENTIFICADA FALHA” e recomenda **manter o acompanhamento das condições operacionais**.

**Evidência:** código da célula 30 e saídas das células 32 e 34 do notebook. Os exemplos exibidos (escores de 94% e 13%) foram escolhidos **entre classificações corretas** do teste, exclusivamente para demonstração.  
**Decisão apoiada:** comunicação clara de um sinal para triagem humana, sem ação automática.  
**Limite:** o projeto não mediu se usuários seguiram a orientação, se foram evitadas falhas, tempo economizado, custo operacional ou desempenho em produção.

## 3. Linha de tomada de decisão efetivamente implementada

```text
Condição operacional informada (6 atributos)
         |
         v
Modelo Random Forest (pipeline em memória)
         |
         +--> Classe prevista = 1 --> “Possível falha”
         |                           --> Priorizar avaliação pela equipe
         |
         +--> Classe prevista = 0 --> “Não foi identificada falha”
                                     --> Manter acompanhamento
         |
         v
Julgamento humano (fora do código do MVP)
```

**Não implementado:** gatilhos com custos, classificação por criticidade, ordens de serviço, desligamento de equipamentos, painel, interface web ou monitoramento contínuo. Não se deve apresentar essas funcionalidades como já existentes.

## 4. Relação com o pipeline de dados em nuvem

O ETL executado no Google Colab salvou e validou duas tabelas CSV no Google Drive (camadas bronze e prata). O notebook original de classificação continua obtendo os dados diretamente da UCI e foi preservado. **Posteriormente**, foi criado e executado o notebook [`notebooks/Integracao_MVP_SSD_Drive_Modelos.ipynb`](../notebooks/Integracao_MVP_SSD_Drive_Modelos.ipynb), que lê a camada prata efetivamente persistida no Drive, verifica seu SHA-256, reproduz as matrizes de confusão dos três modelos e executa as recomendações. Essa execução foi aprovada e registrada em [`evidencias/relatorio_integracao_mvp.json`](../evidencias/relatorio_integracao_mvp.json). Assim, há evidência do fluxo **UCI → ETL → carga no Drive → leitura da prata → treino → previsão → recomendação**, embora a integração ainda utilize caminho e hash fixos da execução do autor, exigindo configuração manual em outra conta.

## 5. Conclusão desta etapa

As quatro perguntas foram respondidas **na extensão permitida pelas evidências existentes**, e o modelo oferece uma orientação simples para triagem humana. Não há prova de eficácia operacional, economia, prevenção de falhas em máquinas reais ou segurança para automatizar intervenções. A documentação das perguntas é posterior ao experimento, em atendimento ao esforço de explicitar problema, interpretação e limites; não equivale a comprovar planejamento prévio.

**Arquivos preservados:** `MVP_Manutencao_Preditiva.ipynb` e o short paper. **Nenhuma métrica, regra ou saída do classificador foi alterada.**
