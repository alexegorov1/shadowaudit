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
    logger.info(f"Discovered {len(collectors)} collector(s).")

    all_valid = []
    total_valid = total_invalid = 0

    for collector in collectors:
        name = collector.get_name()
        logger.info(f"[{name}] Starting...")

        try:
            artifacts = collector.collect()
        except Exception as err:
            logger.error(f"[{name}] Execution failed: {err}")
            continue

        if not isinstance(artifacts, list):
            logger.error(f"[{name}] Returned non-list output: {type(artifacts).__name__}")
            continue

        valid_count = 0

        for idx, artifact in enumerate(artifacts, 1):
            try:
                validator.validate_artifact(artifact)
                all_valid.append(artifact)
                valid_count += 1
            except ValueError as ve:
                total_invalid += 1
                logger.warning(f"[{name}][#{idx}] Validation failed: {ve}")

        total_valid += valid_count
        logger.info(f"[{name}] {len(artifacts)} collected, {valid_count} valid.")

    logger.info(f"Collection summary — Valid: {total_valid}, Invalid: {total_invalid}")

    if all_valid:
        filename = f"artifacts_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(output_dir, filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(all_valid, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(all_valid)} artifact(s) to: {path}")
        except Exception as e:
            logger.error(f"Failed to write file '{path}': {e}")

    return all_valid
