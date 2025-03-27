from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from collector.example_collector import ExampleCollector  # Replace with real collector module

def run_collection():
    config = ConfigLoader().get("general")
    logger = LoggerFactory(config).create_logger("shadowaudit.agent")
    validator = ArtifactSchemaValidator()

    collector = ExampleCollector()
    raw_artifacts = collector.collect()

    validated_artifacts = []

    for artifact in raw_artifacts:
        try:
            validator.validate_artifact(artifact)
            validated_artifacts.append(artifact)
        except ValueError as e:
            logger.error(f"Validation failed for artifact from {collector.__class__.__name__}: {e}")

    logger.info(f"{len(validated_artifacts)} valid artifacts collected from {collector.__class__.__name__}")
    return validated_artifacts
