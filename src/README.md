# Documentação da pasta `src`

Este documento descreve os arquivos Python presentes em `src/` e suas responsabilidades dentro do pipeline de processamento de dados e treinamento de modelo para o dataset Telco Customer Churn.

## Estrutura da pasta `src`

- `clean.py`
- `features.py`
- `ingest.py`
- `train.py`

---

## `clean.py`

### Descrição
Implementa a etapa de limpeza de dados do pipeline.

### Responsabilidades
- Carrega o arquivo bruto `data/raw/telco_customer_churn.csv`
- Remove registros duplicados
- Converte a coluna `TotalCharges` para numérico
- Identifica colunas numéricas e categóricas
- Imputa valores ausentes usando mediana para numéricas e moda para categóricas
- Normaliza colunas numéricas com `StandardScaler`
- Salva o resultado em `data/processed/telco_customer_churn_clean.csv`

### Uso
```bash
python src/clean.py
```

### Observações
- Usa logging para registrar o progresso
- Verifica se o arquivo de entrada existe antes da leitura
- Foi projetado para garantir que dados limpos e consistentes sejam gerados para a próxima etapa

---

## `features.py`

### Descrição
Implementa a etapa de engenharia de características do pipeline.

### Responsabilidades
- Carrega o dataset processado em `data/processed/telco_customer_churn_clean.csv`
- Remove colunas irrelevantes, como `customerID`
- Cria novas features derivadas:
  - `tenure_bucket`
  - `avg_monthly_revenue`
  - `is_high_value_customer`
- Converte a coluna alvo `Churn` para valores numéricos (`Yes` -> `1`, `No` -> `0`)
- Identifica colunas categóricas e aplica `OneHotEncoder`
- Valida o dataset final para garantir ausência de valores nulos e presença da variável alvo
- Salva o resultado em `data/features/telco_customer_churn_features.csv`

### Uso
```bash
python src/features.py
```

### Observações
- Garante que o dataset final esteja pronto para treinamento de modelo
- Mantém uma separação clara entre transformação de dados e criação de features

---

## `ingest.py`

### Descrição
Arquivo presente no projeto, mas atualmente sem implementação.

### Responsabilidades esperadas
- Normalmente, um módulo de ingestão serve para:
  - coletar dados de fontes externas
  - mover ou copiar arquivos para o diretório de dados brutos
  - preparar o raw dataset para a etapa de limpeza

### Observações
- Atualmente não contém código nem pipeline definido
- Pode ser utilizado no futuro para centralizar a ingestão de dados antes da limpeza

---

## `train.py`

### Descrição
Implementa a etapa de treinamento e avaliação de modelo do pipeline.

### Responsabilidades
- Carrega o dataset de features em `data/features/telco_customer_churn_features.csv`
- Separa `X` (features) e `y` (target `Churn`)
- Divide os dados em treino e teste (`test_size=0.2` e `random_state=42`)
- Treina um modelo `RandomForestClassifier`
- Avalia o modelo usando métricas:
  - acurácia
  - precisão
  - recall
  - f1-score
- Salva:
  - modelo em `models/random_forest_model.pkl`
  - métricas em `reports/metrics.json`
  - relatório de classificação em `reports/classification_report.txt`
- Exibe a importância das features no log

### Uso
```bash
python src/train.py
```

### Observações
- Verifica a presença da coluna alvo antes de treinar
- Salva artefatos e relatórios para reprodutibilidade
- Usa logging para rastrear cada passo do pipeline

---

## Fluxo esperado do pipeline

1. `python src/clean.py`
2. `python src/features.py`
3. `python src/train.py`

> No momento, `src/ingest.py` está vazio e pode ser preenchido futuramente com a lógica de ingestão de dados.
