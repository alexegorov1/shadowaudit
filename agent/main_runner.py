import os
import json
from datetime import datetime, timezone
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.schema_validator import ArtifactSchemaValidator
from core.plugin_loader import discover_collectors


def run_collection_phase(config: dict = None) -> list[dict]:
    config_loader = ConfigLoader()
    full_config = config or config_loader.full
    general_config = full_config.get("general", {})

    output_dir = general_config.get("output_path", "./results")
    os.makedirs(output_dir, exist_ok=True)

    logger = LoggerFactory(general_config).create_logger("shadowaudit.agent")
    validator = ArtifactSchemaValidator()

    collectors = discover_collectors()
    logger.info(f"Discovered {len(collectors)} collector(s).")

    all_valid_artifacts = []
    total_valid, total_invalid = 0, 0

    for collector in collectors:
        name = collector.get_name()
        logger.info(f"Executing collector: {name}")

        try:
            raw_artifacts = collector.collect()
        except Exception as error:
            logger.error(f"[{name}] Collector execution failed: {error}")
            continue

        if not isinstance(raw_artifacts, list):
            logger.error(f"[{name}] Collector returned non-list output: {type(raw_artifacts).__name__}")
            continue

        valid_count = 0

        for index, artifact in enumerate(raw_artifacts, 1):
            try:
                validator.validate_artifact(artifact)
                all_valid_artifacts.append(artifact)
                valid_count += 1
            except ValueError as validation_error:
                total_invalid += 1
                logger.warning(f"[{name}][#{index}] Validation failed: {validation_error}")

        total_valid += valid_count
        logger.info(f"[{name}] {len(raw_artifacts)} total, {valid_count} valid.")

    logger.info(f"Collection finished: {total_valid} valid, {total_invalid} invalid.")

    if all_valid_artifacts:
        filename = f"artifacts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        output_path = os.path.join(output_dir, filename)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(all_valid_artifacts, f, indent=2, ensure_ascii=False)
            logger.info(f"Artifacts saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to write output file '{output_path}': {e}")

    return all_valid_artifacts
