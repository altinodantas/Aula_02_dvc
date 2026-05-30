from src.train import run_training_pipeline, logger

if __name__ == "__main__":
    try:
        run_training_pipeline()

    except Exception as exc:
        logger.exception(
            "Erro durante execução do pipeline: %s",
            exc
        )
        raise