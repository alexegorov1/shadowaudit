from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from core.plugin_loader import discover_collectors

def run_collection():
    config = ConfigLoader().get("general")
    logger = LoggerFactory(config).create_logger("shadowaudit.agent")
    validator = ArtifactSchemaValidator()

    collectors = discover_collectors()
    logger.info(f"{len(collectors)} collectors discovered.")

    all_valid_artifacts = []

    for collector in collectors:
        collector_name = collector.get_name()
        logger.info(f"Running collector: {collector_name}")

        try:
            artifacts = collector.collect()
        except Exception as e:
            logger.error(f"Collector '{collector_name}' failed during collection: {e}")
            continue

        if not isinstance(artifacts, list):
            logger.error(f"Collector '{collector_name}' returned non-list result: {type(artifacts).__name__}")
            continue

        for index, artifact in enumerate(artifacts, start=1):
            try:
                validator.validate_artifact(artifact)
                all_valid_artifacts.append(artifact)
            except ValueError as e:
                logger.warning(
                    f"Validation failed for artifact #{index} from '{collector_name}': {e}"
                )

        logger.info(
            f"Collector '{collector_name}' completed. "
            f"{len(artifacts)} returned, "
            f"{len([a for a in artifacts if a in all_valid_artifacts])} valid."
        )

    logger.info(f"Total valid artifacts collected: {len(all_valid_artifacts)}")
    return all_valid_artifacts

