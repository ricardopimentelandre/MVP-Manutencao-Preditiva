# Modelo de dados, catálogo e linhagem — MVP de manutenção preditiva

**Projeto:** Sistema de Suporte à Decisão para Manutenção Preditiva  
**Data da verificação:** 09/11/2026  
**Fonte oficial:** [UCI AI4I 2020 (ID 601)](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset), DOI [10.24432/C5HS5C](https://doi.org/10.24432/C5HS5C), licença CC BY 4.0.  
**Evidências de execução:** `evidencias/relatorio_etl_nuvem.json`; `evidencias/relatorio_qualidade_dados.json`.

## 1. Modelo de dados

Modelo **flat** (tabela única), adequado ao escopo atual da classificação binária. **Grão:** uma observação sintética de condição operacional de produto/equipamento. Não há identificação de máquina nem timestamps; portanto, não se deve interpretar o conjunto como histórico longitudinal por máquina.

- **Bronze:** `bronze/ai4i_original_ucimlrepo.csv` (10.000 linhas × 14 colunas). Representa a tabela retornada por `ucimlrepo` e serializada em CSV UTF-8; **não é cópia byte a byte do CSV original da UCI**.
- **Prata:** `prata/ai4i_modelagem.csv` (10.000 linhas × 7 colunas). Seis atributos de entrada e o alvo binário `Machine failure`.
- **Sem tabela fato/dimensão:** o esquema estrela não acrescentaria utilidade ao conjunto de sete colunas no escopo demonstrativo. A tabela única é a modelagem adotada; isso não representa implantação de um data warehouse corporativo.

## 2. Catálogo de dados — camada prata

Todos os sete campos são **obrigatórios** neste conjunto; a auditoria dos 10.000 registros encontrou **0 nulos**. As faixas abaixo são **mínimos e máximos observados no CSV**, não limites universais para futuros equipamentos.

| Campo | Tipo lógico | Unidade | Definição | Domínio / regra de validação | Faixa ou frequência observada |
|---|---|---|---|---|---|
| `Type` | categórico (texto) | — | Categoria do produto (qualidade L/M/H) | L, M, H | L, M, H |
| `Air temperature` | numérico contínuo | K | Temperatura do ar | positivo, finito | 295,3–304,5 |
| `Process temperature` | numérico contínuo | K | Temperatura de processo | positivo, finito | 305,7–313,8 |
| `Rotational speed` | inteiro | rpm | Rotação da máquina | inteiro positivo | 1.168–2.886 |
| `Torque` | numérico contínuo | Nm | Torque aplicado | finito, não negativo | 3,8–76,6 |
| `Tool wear` | inteiro | min | Desgaste acumulado da ferramenta, em minutos | inteiro não negativo | 0–253 |
| `Machine failure` | inteiro binário (alvo) | — | Ocorrência de falha (0: não; 1: sim) | 0 ou 1 | 0: 9.661; 1: 339 |

A coluna `Type` contém L: 6.000, M: 2.997 e H: 1.003. O alvo tem 9.661 registros sem falha (96,61%) e 339 com falha (3,39%). Não é recomendado impor os mínimos/máximos observados como regra de exclusão sem validação técnica.

## 3. Linhagem e transformações

```text
UCI AI4I 2020 (id=601; fetch_ucirepo)
    └── Colab: coleta dos DataFrames (features, targets e IDs)
          └── Google Drive / bronze/ai4i_original_ucimlrepo.csv (14 colunas)
                └── Seleção das 6 colunas com papel Feature
                    + seleção do alvo Machine failure
                    + concatenação pela ordem original, sem excluir registros
                     └── Google Drive / prata/ai4i_modelagem.csv (7 colunas)
                           └── Notebook do MVP: codificação OneHot/escala quando aplicável
                               + classificadores (apenas em memória; não são ETL de carga)
```

Cada coluna da prata vem **da coluna homônima na bronze**, sem renomeação e sem modificação de valor na etapa ETL. Auditoria por ordem de linha: **70.000 de 70.000 células idênticas** (10.000 × 7), com 10.000 registros preservados. Os dois arquivos foram lidos diretamente do Drive na verificação.

**Limitação de rastreabilidade:** `UID` e `Product ID` permanecem apenas na bronze e não são armazenados na prata. A correspondência atual é demonstrada pela posição da linha na carga, o que **não constitui chave estável** se os arquivos forem reordenados. Para um pipeline evolutivo, recomenda-se preservar `UID` como chave técnica separada da matriz de variáveis do modelo.

**Campos mantidos apenas na bronze:** `UID`, `Product ID`, `TWF`, `HDF`, `PWF`, `OSF` e `RNF`. Os cinco indicadores de modo de falha não devem compor as entradas do classificador binário, devido ao risco de vazamento do alvo.

## 4. Validações de qualidade realizadas

| Controle | Evidência | Resultado |
|---|---|---|
| Quantidade de registros | Contagem bronze e prata | 10.000 / 10.000 |
| Completude | Campos nulos nas 7 colunas | **0** |
| Domínio categórico e alvo | `Type ∈ {L,M,H}`; `Machine failure ∈ {0,1}` | **0 inválidos** |
| Tipos e sinais básicos | Temperaturas e rotação positivas; torque e desgaste não negativos | **0 inválidos** |
| Relação física básica | Temperatura de processo ≥ temperatura do ar | **0 violações** |
| Repetição exata | Comparação de todas as 7 colunas | **0 linhas repetidas exatamente** |
| Linhagem de valores | Prata contra colunas homônimas na bronze, mesma posição | **70.000/70.000 coincidentes** |
| UID na bronze | Contagem de IDs únicos | **10.000** |
| Coerência `Product ID` × `Type` | Prefixo L/M/H do identificador | **0 divergências** |
| Coerência alvo × modos de falha | `Machine failure` versus OR(TWF,HDF,PWF,OSF,RNF) | **27 divergências — atenção** |

**Achado importante na base de origem:** em 9 registros o alvo é 1 embora todos os cinco modos estejam em 0; em outros 18, `RNF=1` e `Machine failure=0`. Esse comportamento foi observado **na bronze**, antes da seleção para a prata. A documentação da UCI descreve a ocorrência de falha a partir dos modos, mas o CSV contém esses desacordos. Não foi feita correção automática, porque mudar o alvo alteraria o experimento original; recomenda-se registrar a inconsistência e avaliá-la antes de qualquer evolução do modelo.

**Alcance da auditoria:** essas verificações demonstram estrutura, alguns domínios, integridade da seleção e consistência básica. Elas não comprovam precisão de sensores ou validade operacional em máquinas reais: a base é sintética.

## 5. Local dos artefatos e verificação

- Pasta da execução no Drive: [20261109T200446Z](https://drive.google.com/drive/folders/1LnvAGG_XBg992YM8zth1jJ8fn3Fe7Q6w)
- [CSV bronze](https://drive.google.com/file/d/1i2osfEb5oTiyMMNQWGEabjg4fmsjuWTz/view)
- [CSV prata](https://drive.google.com/file/d/1cs9dIXXyZkuW1p_bTk7WHU7u-7nZZG8z/view)
- Evidência do ETL: `evidencias/relatorio_etl_nuvem.json`
- Evidência adicional de catálogo/qualidade: `evidencias/relatorio_qualidade_dados.json`

O notebook original `MVP_Manutencao_Preditiva.ipynb` e o short paper **não foram modificados** nesta etapa.
