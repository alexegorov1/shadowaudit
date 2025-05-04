import os
import json
from datetime import datetime, timezone
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from core.plugin_loader import discover_collectors

def run_collection_phase(config: dict = None) -> list[dict]:
    config = config or ConfigLoader().full
    general = config.get("general", {})
    output_dir = general.get("output_path", "./results")
    os.makedirs(output_dir, exist_ok=True)

    logger = LoggerFactory(general).create_logger("shadowaudit.agent")
    validator = ArtifactSchemaValidator()
    collectors = discover_collectors()

    logger.info(f"Found {len(collectors)} collector(s)")
    valid_artifacts = []
    total_valid = total_invalid = 0

    for collector in collectors:
        name = collector.get_name()
        logger.info(f"[{name}] Collecting")

        try:
            artifacts = collector.collect()
        except Exception as e:
            logger.error(f"[{name}] Collector failed: {e}")
            continue

        if not isinstance(artifacts, list):
            logger.error(f"[{name}] Non-list output: {type(artifacts).__name__}")
            continue

        for idx, artifact in enumerate(artifacts, 1):
            try:
                validator.validate_artifact(artifact)
                valid_artifacts.append(artifact)
                total_valid += 1
            except ValueError as e:
                total_invalid += 1
                logger.warning(f"[{name}][#{idx}] Validation error: {e}")

        logger.info(f"[{name}] Processed: {len(artifacts)}, Valid: {total_valid}")

    logger.info(f"Collection complete — Valid: {total_valid}, Invalid: {total_invalid}")

    if valid_artifacts:
        filename = f"artifacts_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(valid_artifacts, f, indent=2, ensure_ascii=False)
            logger.info(f"Artifacts written to: {path}")
        except Exception as e:
            logger.error(f"File write failed: {e}")

    return valid_artifacts
