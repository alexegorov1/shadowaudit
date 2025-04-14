import os
import json
from datetime import datetime, timezone
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from core.plugin_loader import discover_collectors

def run_collection_phase(config: dict = None) -> list[dict]:
    if config is None:
        config = ConfigLoader().full

    general_config = config.get("general", {})
    output_path = general_config.get("output_path", "./results")
    os.makedirs(output_path, exist_ok=True)

    logger = LoggerFactory(general_config).create_logger("shadowaudit.agent")
    validator = ArtifactSchemaValidator()

    collectors = discover_collectors()
    logger.info(f"{len(collectors)} collector(s) discovered.")

    all_valid_artifacts = []
    total_valid, total_invalid = 0, 0

    for collector in collectors:
        name = collector.get_name()
        logger.info(f"Executing collector: {name}")

        try:
            raw_artifacts = collector.collect()
        except Exception as e:
            logger.error(f"Collector '{name}' failed: {e}")
            continue

        if not isinstance(raw_artifacts, list):
            logger.error(f"Collector '{name}' returned invalid type: {type(raw_artifacts).__name__}")
            continue

        valid_count = 0
        for idx, artifact in enumerate(raw_artifacts, 1):
            try:
                validator.validate_artifact(artifact)
                all_valid_artifacts.append(artifact)
                valid_count += 1
            except ValueError as e:
                total_invalid += 1
                logger.warning(f"[{name}][#{idx}] Validation error: {e}")

        total_valid += valid_count
        logger.info(f"[{name}] {len(raw_artifacts)} collected, {valid_count} valid.")

    logger.info(f"Collection complete — valid: {total_valid}, invalid: {total_invalid}")

    if all_valid_artifacts:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_path, f"artifacts_{timestamp}.json")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_valid_artifacts, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(all_valid_artifacts)} artifacts to '{output_file}'")
        except Exception as e:
            logger.error(f"Failed to write output file: {e}")

    return all_valid_artifacts
