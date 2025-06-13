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

    def validate_artifact(self, artifact):
        artifact_type = artifact.get("artifact_type")
        if artifact_type in self._validators:
            validator = self._validators[artifact_type]
        else:
            validator = self._validators["base"]

        try:
            validator.validate(artifact)
        except ValidationError as e:
            raise ValueError(f"Artifact validation error: {e.message}") from e
        except SchemaError as e:
            raise ValueError(f"Schema structure error: {e.message}") from e
