"""
src/clean.py

Pipeline de limpeza de dados para o dataset Telco Customer Churn.

Responsabilidades:
1. Remoção de registros duplicados
2. Tratamento de valores ausentes
3. Normalização de colunas numéricas

Boas práticas aplicadas:
- Estrutura modular
- Logging
- Type hints
- Configuração centralizada
- Tratamento de erros
- Reprodutibilidade
- Separação de responsabilidades

Execução:
    python src/clean.py

Entrada esperada:
    data/raw/telco_customer_churn.csv

Saída:
    data/processed/telco_customer_churn_clean.csv
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO
# -----------------------------------------------------------------------------

RAW_DATA_PATH = Path("data/raw/telco_customer_churn.csv")
PROCESSED_DATA_PATH = Path(
    "data/processed/telco_customer_churn_clean.csv"
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


print(RAW_DATA_PATH)
print(PROCESSED_DATA_PATH)


def load_dataset(file_path: Path) -> pd.DataFrame:
    """
    Carrega dataset CSV.

    Args:
        file_path: Caminho do arquivo CSV.

    Returns:
        DataFrame carregado.
    """
    logger.info("Carregando dataset: %s", file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {file_path}"
        )

    df = pd.read_csv(file_path)

    logger.info("Dataset carregado com %d linhas e %d colunas",
                df.shape[0], df.shape[1])

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove registros duplicados.

    Args:
        df: DataFrame original.

    Returns:
        DataFrame sem duplicados.
    """
    initial_rows = len(df)

    df_clean = df.drop_duplicates()

    removed_rows = initial_rows - len(df_clean)

    logger.info(
        "Duplicados removidos: %d registros",
        removed_rows
    )

    return df_clean


def convert_total_charges_to_numeric(
    df: pd.DataFrame
) -> pd.DataFrame:
    """
    Converte coluna TotalCharges para tipo numérico.

    O dataset Telco geralmente possui strings vazias
    nesta coluna.

    Args:
        df: DataFrame original.

    Returns:
        DataFrame atualizado.
    """
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(
            df["TotalCharges"],
            errors="coerce"
        )

        logger.info(
            "Coluna 'TotalCharges' convertida para numérico"
        )

    return df


def split_columns(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, list[str]]:
    """
    Identifica colunas numéricas.

    Args:
        df: DataFrame.

    Returns:
        Tuple contendo:
        - DataFrame atualizado
        - Lista de colunas numéricas
    """
    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    if TARGET_COLUMN in numeric_columns:
        numeric_columns.remove(TARGET_COLUMN)

    logger.info(
        "Colunas numéricas identificadas: %s",
        numeric_columns
    )

    return df, numeric_columns


def impute_missing_values(
    df: pd.DataFrame,
    numeric_columns: list[str]
) -> pd.DataFrame:
    """
    Realiza imputação de valores ausentes.

    Estratégias:
    - Numéricas: mediana
    - Categóricas: moda

    Args:
        df: DataFrame.
        numeric_columns: Lista de colunas numéricas.

    Returns:
        DataFrame tratado.
    """
    logger.info("Iniciando tratamento de valores ausentes")

    # -----------------------------
    # Colunas numéricas
    # -----------------------------
    numeric_imputer = SimpleImputer(strategy="median")

    df[numeric_columns] = numeric_imputer.fit_transform(
        df[numeric_columns]
    )

    # -----------------------------
    # Colunas categóricas
    # -----------------------------
    categorical_columns = df.select_dtypes(
        include=["object"]
    ).columns.tolist()

    categorical_imputer = SimpleImputer(strategy="most_frequent")

    df[categorical_columns] = categorical_imputer.fit_transform(
        df[categorical_columns]
    )

    logger.info("Valores ausentes tratados com sucesso")

    return df


def normalize_numeric_columns(
    df: pd.DataFrame,
    numeric_columns: list[str]
) -> pd.DataFrame:
    """
    Normaliza colunas numéricas utilizando StandardScaler.

    Fórmula:
        z = (x - média) / desvio padrão

    Args:
        df: DataFrame.
        numeric_columns: Lista de colunas numéricas.

    Returns:
        DataFrame normalizado.
    """
    logger.info(
        "Iniciando normalização das colunas numéricas"
    )

    scaler = StandardScaler()

    df[numeric_columns] = scaler.fit_transform(
        df[numeric_columns]
    )

    logger.info(
        "Normalização concluída para %d colunas",
        len(numeric_columns)
    )

    return df


def save_dataset(
    df: pd.DataFrame,
    output_path: Path
) -> None:
    """
    Salva dataset processado.

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
        "Dataset processado salvo em: %s",
        output_path
    )


# -----------------------------------------------------------------------------
# PIPELINE PRINCIPAL
# -----------------------------------------------------------------------------


def run_cleaning_pipeline() -> None:
    """
    Executa pipeline completo de limpeza.
    """
    logger.info("Iniciando pipeline de limpeza")

    # 1. Carregar dados
    df = load_dataset(RAW_DATA_PATH)

    # 2. Conversão específica do dataset
    df = convert_total_charges_to_numeric(df)

    # 3. Remover duplicados
    df = remove_duplicates(df)

    # 4. Identificar colunas numéricas
    df, numeric_columns = split_columns(df)

    # 5. Tratar valores ausentes
    df = impute_missing_values(df, numeric_columns)

    # 6. Normalizar dados numéricos
    # df = normalize_numeric_columns(df, numeric_columns)

    # 7. Salvar resultado
    save_dataset(df, PROCESSED_DATA_PATH)

    logger.info("Pipeline finalizado com sucesso")


# -----------------------------------------------------------------------------
# ENTRYPOINT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_cleaning_pipeline()

    except Exception as exc:
        logger.exception(
            "Erro durante execução do pipeline: %s",
            exc
        )
        raise