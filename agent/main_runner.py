import sys
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from collector.example_collector import ExampleCollector  # Replace with real collector module

def run_collection():
    try:
        config = ConfigLoader().get("general")
        logger = LoggerFactory(config).create_logger("shadowaudit.agent")
        validator = ArtifactSchemaValidator()
    except Exception as init_error:
        print(f"[FATAL] Initialization failed: {init_error}", file=sys.stderr)
        sys.exit(1)

    collector = ExampleCollector()
    logger.info(f"Running collector: {collector.__class__.__name__}")

    try:
        raw_artifacts = collector.collect()
    except Exception as collection_error:
        logger.error(f"Collector {collector.__class__.__name__} failed: {collection_error}")
        return []

    if not isinstance(raw_artifacts, list):
        logger.error(f"Collector output must be a list, got {type(raw_artifacts).__name__}")
        return []

    validated_artifacts = []
    failed_count = 0

    for idx, artifact in enumerate(raw_artifacts, start=1):
        try:
            validator.validate_artifact(artifact)
            validated_artifacts.append(artifact)
        except ValueError as validation_error:
            failed_count += 1
            artifact_source = artifact.get("source", "unknown")
            logger.warning(
                f"[{idx}] Artifact validation failed (source: {artifact_source}): {validation_error}"
            )

    logger.info(
        f"Collector {collector.__class__.__name__} returned {len(raw_artifacts)} artifacts. "
        f"{len(validated_artifacts)} passed validation, {failed_count} failed."
    )

    return validated_artifacts

