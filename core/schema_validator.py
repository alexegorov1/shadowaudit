import os
import json
from jsonschema import validate, ValidationError, SchemaError, RefResolver
from jsonschema.validators import validator_for

class ArtifactSchemaValidator:
    def __init__(self, base_schema_path="schemas/base_artifact.schema.json", schema_map=None):
        self._schemas = {}
        self._validators = {}

        # Load base schema and any additional schemas if specified
        self._load_schema("base", base_schema_path)

        if schema_map is None:
            schema_map = {
                "file_scan": "schemas/filesystem_artifact.schema.json",
                "registry": "schemas/registry_artifact.schema.json"
            }

        for artifact_type, schema_path in schema_map.items():
            self._load_schema(artifact_type, schema_path)

    def _load_schema(self, schema_id, path):
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Schema file not found: {abs_path}")
        with open(abs_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        ValidatorClass = validator_for(schema)
        ValidatorClass.check_schema(schema)
        self._schemas[schema_id] = schema
        self._validators[schema_id] = ValidatorClass(schema)

        try:
            validator.validate(artifact)
        except ValidationError as e:
            raise ValueError(f"Artifact validation error: {e.message}") from e
        except SchemaError as e:
            raise ValueError(f"Schema structure error: {e.message}") from e
