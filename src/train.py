"""
src/train.py

Pipeline de treinamento de modelo para o dataset
Telco Customer Churn utilizando RandomForestClassifier.

Responsabilidades:
1. Carregar dataset de features
2. Separar treino e teste
3. Treinar modelo Random Forest
4. Avaliar desempenho
5. Salvar métricas
6. Persistir modelo treinado

Boas práticas aplicadas:
- Estrutura modular
- Logging
- Reprodutibilidade
- Configuração centralizada
- Type hints
- Separação de responsabilidades
- Persistência de artefatos
- Métricas de avaliação
- Tratamento de erros

Execução:
    python src/train.py

Entrada esperada:
    data/features/telco_customer_churn_features.csv

Saídas:
    models/random_forest_model.pkl
    reports/metrics.json
    reports/classification_report.txt
"""

from __future__ import annotations

import json
import logging
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO
# -----------------------------------------------------------------------------

INPUT_DATA_PATH = Path(
    "data/features/telco_customer_churn_features.csv"
)

MODEL_OUTPUT_PATH = Path(
    "models/random_forest_model.pkl"
)

METRICS_OUTPUT_PATH = Path(
    "reports/metrics.json"
)

CLASSIFICATION_REPORT_PATH = Path(
    "reports/classification_report.txt"
)

TARGET_COLUMN = "Churn"

RANDOM_STATE = 42

TEST_SIZE = 0.2

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
    Carrega dataset de features.

    Args:
        file_path: Caminho do dataset.

    Returns:
        DataFrame carregado.
    """
    logger.info(
        "Carregando dataset de features"
    )

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


def split_features_and_target(
    df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Separa variáveis independentes e alvo.

    Args:
        df: Dataset completo.

    Returns:
        Tuple contendo:
            X -> Features
            y -> Variável alvo
    """
    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Coluna alvo '{TARGET_COLUMN}' não encontrada"
        )

    X = df.drop(columns=[TARGET_COLUMN])

    y = df[TARGET_COLUMN]

    logger.info(
        "Features e target separados"
    )

    logger.info(
        "Quantidade de features: %d",
        X.shape[1]
    )

    return X, y


def split_train_test(
    X: pd.DataFrame,
    y: pd.Series
) -> Tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series
]:
    """
    Realiza divisão treino/teste.

    Args:
        X: Features.
        y: Variável alvo.

    Returns:
        Dados divididos.
    """
    logger.info(
        "Realizando divisão treino/teste"
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )

    logger.info(
        "Treino: %d registros | Teste: %d registros",
        len(X_train),
        len(X_test)
    )

    return X_train, X_test, y_train, y_test


def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series
) -> RandomForestClassifier:
    """
    Treina modelo Random Forest.

    Args:
        X_train: Features de treino.
        y_train: Labels de treino.

    Returns:
        Modelo treinado.
    """
    logger.info(
        "Iniciando treinamento do modelo"
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    logger.info(
        "Treinamento concluído"
    )

    return model


def evaluate_model(
    model: RandomForestClassifier,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> dict:
    """
    Avalia desempenho do modelo.

    Args:
        model: Modelo treinado.
        X_test: Features de teste.
        y_test: Labels de teste.

    Returns:
        Dicionário contendo métricas.
    """
    logger.info(
        "Avaliando modelo"
    )

    predictions = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(
            y_test,
            predictions
        ),
        "precision": precision_score(
            y_test,
            predictions
        ),
        "recall": recall_score(
            y_test,
            predictions
        ),
        "f1_score": f1_score(
            y_test,
            predictions
        ),
    }

    logger.info(
        "Accuracy: %.4f",
        metrics["accuracy"]
    )

    logger.info(
        "F1-Score: %.4f",
        metrics["f1_score"]
    )

    confusion = confusion_matrix(
        y_test,
        predictions
    )

    logger.info(
        "Matriz de confusão:\n%s",
        confusion
    )

    report = classification_report(
        y_test,
        predictions
    )

    save_classification_report(report)

    return metrics


def save_model(
    model: RandomForestClassifier,
    output_path: Path
) -> None:
    """
    Salva modelo treinado.

    Args:
        model: Modelo treinado.
        output_path: Caminho de saída.
    """
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "wb") as file:
        pickle.dump(model, file)

    logger.info(
        "Modelo salvo em: %s",
        output_path
    )


def save_metrics(
    metrics: dict,
    output_path: Path
) -> None:
    """
    Salva métricas em JSON.

    Args:
        metrics: Dicionário de métricas.
        output_path: Caminho de saída.
    """
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            metrics,
            file,
            indent=4
        )

    logger.info(
        "Métricas salvas em: %s",
        output_path
    )


def save_classification_report(
    report: str
) -> None:
    """
    Salva classification report.

    Args:
        report: Texto do relatório.
    """
    CLASSIFICATION_REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CLASSIFICATION_REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(report)

    logger.info(
        "Classification report salvo"
    )


def log_feature_importance(
    model: RandomForestClassifier,
    feature_names: list[str]
) -> None:
    """
    Exibe importância das features.

    Args:
        model: Modelo treinado.
        feature_names: Lista de features.
    """
    logger.info(
        "Top 10 features mais importantes"
    )

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": model.feature_importances_
    })

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    )

    top_features = importance_df.head(10)

    for _, row in top_features.iterrows():
        logger.info(
            "%s -> %.4f",
            row["feature"],
            row["importance"]
        )


# -----------------------------------------------------------------------------
# PIPELINE PRINCIPAL
# -----------------------------------------------------------------------------


def run_training_pipeline() -> None:
    """
    Executa pipeline completo de treinamento.
    """
    logger.info(
        "Iniciando pipeline de treinamento"
    )

    # 1. Carregar dataset
    df = load_dataset(INPUT_DATA_PATH)

    # 2. Separar features e target
    X, y = split_features_and_target(df)

    # 3. Dividir treino/teste
    X_train, X_test, y_train, y_test = split_train_test(
        X,
        y
    )

    # 4. Treinar modelo
    model = train_model(
        X_train,
        y_train
    )

    # 5. Avaliar modelo
    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    # 6. Salvar modelo
    save_model(
        model,
        MODEL_OUTPUT_PATH
    )

    # 7. Salvar métricas
    save_metrics(
        metrics,
        METRICS_OUTPUT_PATH
    )

    # 8. Exibir feature importance
    log_feature_importance(
        model,
        X.columns.tolist()
    )

    logger.info(
        "Pipeline de treinamento concluído com sucesso"
    )


# -----------------------------------------------------------------------------
# ENTRYPOINT
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        run_training_pipeline()

    except Exception as exc:
        logger.exception(
            "Erro durante execução do pipeline: %s",
            exc
        )
        raise