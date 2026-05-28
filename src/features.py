"""
src/features.py

Pipeline de engenharia de características para o dataset
Telco Customer Churn.

Responsabilidades:
1. Encoding de variáveis categóricas
2. Criação de features derivadas
3. Bucketização de variáveis
4. Geração do dataset final para treinamento

Boas práticas aplicadas:
- Estrutura modular
- Logging
- Type hints
- Configuração centralizada
- Pipeline reproduzível
- Separação clara de responsabilidades
- Código orientado a manutenção

Execução:
    python src/features.py

Entrada esperada:
    data/processed/telco_customer_churn_clean.csv

Saída:
    data/features/telco_customer_churn_features.csv
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO
# -----------------------------------------------------------------------------

INPUT_DATA_PATH = Path(
    "../data/processed/telco_customer_churn_clean.csv"
)

OUTPUT_DATA_PATH = Path(
    "../data/features/telco_customer_churn_features.csv"
)

TARGET_COLUMN = "Churn"

# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------------------


def load_dataset(file_path: Path) -> pd.DataFrame:
    """
    Carrega dataset processado.

    Args:
        file_path: Caminho do dataset.

    Returns:
        DataFrame carregado.
    """
    logger.info("Carregando dataset processado")

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {file_path}"
        )

    df = pd.read_csv(file_path)

    logger.info(
        "Dataset carregado com %d linhas e %d colunas",
        df.shape[0],
        df.shape[1]
    )

    return df


def create_tenure_bucket_feature(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria bucketização da variável tenure.

    Categorias:
    - New
    - Short-Term
    - Mid-Term
    - Long-Term

    Args:
        df: DataFrame.

    Returns:
        DataFrame atualizado.
    """
    if "tenure" not in df.columns:
        logger.warning(
            "Coluna 'tenure' não encontrada"
        )
        return df

    logger.info(
        "Criando feature derivada: tenure_bucket"
    )

    bins = [-np.inf, 12, 24, 48, np.inf]

    labels = [
        "New",
        "Short-Term",
        "Mid-Term",
        "Long-Term",
    ]

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=bins,
        labels=labels
    )

    return df


def create_avg_monthly_revenue_feature(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria feature de média de gasto mensal.

    Fórmula:
        TotalCharges / tenure

    Args:
        df: DataFrame.

    Returns:
        DataFrame atualizado.
    """
    required_columns = {"TotalCharges", "tenure"}

    if not required_columns.issubset(df.columns):
        logger.warning(
            "Colunas necessárias não encontradas "
            "para avg_monthly_revenue"
        )
        return df

    logger.info(
        "Criando feature derivada: avg_monthly_revenue"
    )

    df["avg_monthly_revenue"] = (
        df["TotalCharges"] /
        (df["tenure"] + 1)
    )

    return df


def create_is_high_value_customer_feature(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Cria flag para clientes de alto valor.

    Critério:
        MonthlyCharges > mediana

    Args:
        df: DataFrame.

    Returns:
        DataFrame atualizado.
    """
    if "MonthlyCharges" not in df.columns:
        logger.warning(
            "Coluna 'MonthlyCharges' não encontrada"
        )
        return df

    logger.info(
        "Criando feature derivada: is_high_value_customer"
    )

    threshold = df["MonthlyCharges"].median()

    df["is_high_value_customer"] = (
        df["MonthlyCharges"] > threshold
    ).astype(int)

    return df


def remove_irrelevant_columns(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Remove colunas irrelevantes para treinamento.

    Exemplo:
        customerID

    Args:
        df: DataFrame.

    Returns:
        DataFrame atualizado.
    """
    columns_to_drop = ["customerID"]

    existing_columns = [
        column
        for column in columns_to_drop
        if column in df.columns
    ]

    if existing_columns:
        logger.info(
            "Removendo colunas irrelevantes: %s",
            existing_columns
        )

        df = df.drop(columns=existing_columns)

    return df


def encode_target_column(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Codifica coluna alvo Churn.

    Yes -> 1
    No  -> 0

    Args:
        df: DataFrame.

    Returns:
        DataFrame atualizado.
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Coluna alvo '{TARGET_COLUMN}' não encontrada"
        )

    logger.info("Codificando variável alvo")

    df[TARGET_COLUMN] = (
        df[TARGET_COLUMN]
        .map({
            "Yes": 1,
            "No": 0
        })
        .astype(int)
    )

    return df


def identify_categorical_columns(
    df: pd.DataFrame
) -> List[str]:
    """
    Identifica colunas categóricas.

    Args:
        df: DataFrame.

    Returns:
        Lista de colunas categóricas.
    """
    categorical_columns = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    if TARGET_COLUMN in categorical_columns:
        categorical_columns.remove(TARGET_COLUMN)

    logger.info(
        "Colunas categóricas identificadas: %s",
        categorical_columns
    )

    return categorical_columns


def apply_one_hot_encoding(
    df: pd.DataFrame,
    categorical_columns: List[str]
) -> pd.DataFrame:
    """
    Aplica One-Hot Encoding.

    Args:
        df: DataFrame.
        categorical_columns: Colunas categóricas.

    Returns:
        DataFrame transformado.
    """
    if not categorical_columns:
        logger.info(
            "Nenhuma coluna categórica encontrada"
        )
        return df

    logger.info(
        "Aplicando One-Hot Encoding"
    )

    encoder = OneHotEncoder(
        sparse_output=False,
        handle_unknown="ignore"
    )

    encoded_array = encoder.fit_transform(
        df[categorical_columns]
    )

    encoded_columns = encoder.get_feature_names_out(
        categorical_columns
    )

    encoded_df = pd.DataFrame(
        encoded_array,
        columns=encoded_columns,
        index=df.index
    )

    df = pd.concat(
        [
            df.drop(columns=categorical_columns),
            encoded_df
        ],
        axis=1
    )

    logger.info(
        "One-Hot Encoding aplicado em %d colunas",
        len(categorical_columns)
    )

    return df


def validate_final_dataset(
    df: pd.DataFrame
) -> None:
    """
    Executa validações básicas do dataset final.

    Args:
        df: DataFrame final.
    """
    logger.info(
        "Validando dataset final"
    )

    if df.isnull().sum().sum() > 0:
        raise ValueError(
            "Dataset final contém valores nulos"
        )

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            "Variável alvo ausente no dataset final"
        )

    logger.info(
        "Validação concluída com sucesso"
    )


def save_dataset(
    df: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Salva dataset final de features.

    Args:
        df: DataFrame final.
        output_path: Caminho de saída.
    """
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(output_path, index=False)

    logger.info(
        "Dataset de features salvo em: %s",
        output_path
    )


# -----------------------------------------------------------------------------
# PIPELINE PRINCIPAL
# -----------------------------------------------------------------------------


def run_feature_engineering_pipeline() -> None:
    """
    Executa pipeline completo de feature engineering.
    """
    logger.info(
        "Iniciando pipeline de engenharia de características"
    )

    # 1. Carregar dataset
    df = load_dataset(INPUT_DATA_PATH)

    # 2. Remover colunas irrelevantes
    df = remove_irrelevant_columns(df)

    # 3. Criar features derivadas
    df = create_tenure_bucket_feature(df)

    df = create_avg_monthly_revenue_feature(df)

    df = create_is_high_value_customer_feature(df)

    # 4. Codificar variável alvo
    df = encode_target_column(df)

    # 5. Identificar colunas categóricas
    categorical_columns = identify_categorical_columns(df)

    # 6. Aplicar encoding
    df = apply_one_hot_encoding(
        df,
        categorical_columns
    )

    # 7. Validar dataset final
    validate_final_dataset(df)

    # 8. Salvar dataset
    save_dataset(df, OUTPUT_DATA_PATH)

    logger.info(
        "Pipeline de features concluído com sucesso"
    )


# -----------------------------------------------------------------------------
# ENTRYPOINT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_feature_engineering_pipeline()

    except Exception as exc:
        logger.exception(
            "Erro durante execução do pipeline: %s",
            exc
        )
        raise