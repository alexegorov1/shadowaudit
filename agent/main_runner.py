import os
import json
from datetime import datetime, timezone
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from core.plugin_loader import discover_collectors

def run_collection():
    config = ConfigLoader().get("general")
    logger = LoggerFactory(config).create_logger("shadowaudit.agent")
    validator = ArtifactSchemaValidator()

    output_path = config.get("output_path", "./results")
    os.makedirs(output_path, exist_ok=True)

    collectors = discover_collectors()
    logger.info(f"{len(collectors)} collectors discovered.")

    total_valid = 0
    total_invalid = 0
    all_valid_artifacts = []

    for collector in collectors:
        name = collector.get_name()
        logger.info(f"Running collector: {name}")

        try:
            artifacts = collector.collect()
        except Exception as e:
            logger.error(f"Collector '{name}' failed to execute: {e}")
            continue

        if not isinstance(artifacts, list):
            logger.error(f"Collector '{name}' returned non-list output: {type(artifacts).__name__}")
            continue

        valid_count = 0
        for idx, artifact in enumerate(artifacts, start=1):
            try:
                validator.validate_artifact(artifact)
                all_valid_artifacts.append(artifact)
                valid_count += 1
            except ValueError as e:
                total_invalid += 1
                logger.warning(f"[{name}][#{idx}] Schema validation failed: {e}")

        logger.info(f"Collector '{name}' returned {len(artifacts)} artifacts, {valid_count} valid.")
        total_valid += valid_count

    logger.info(f"Collection complete: {total_valid} valid artifacts, {total_invalid} invalid.")

    if all_valid_artifacts:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_path, f"artifacts_{timestamp}.json")
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_valid_artifacts, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(all_valid_artifacts)} artifacts to '{output_file}'")
        except Exception as write_error:
            logger.error(f"Failed to write output file: {write_error}")

    return all_valid_artifacts

