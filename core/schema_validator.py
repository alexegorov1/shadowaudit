import os
import json
from jsonschema import validate, ValidationError, SchemaError
from jsonschema.validators import validator_for

class ArtifactSchemaValidator:
    def __init__(self, schema_path="schemas/base_artifact.schema.json"):
        absolute_path = os.path.abspath(schema_path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(f"Schema file not found: {absolute_path}")

        with open(absolute_path, "r", encoding="utf-8") as f:
            self._schema = json.load(f)

        ValidatorClass = validator_for(self._schema)
        ValidatorClass.check_schema(self._schema)
        self._validator = ValidatorClass(self._schema)

    def validate_artifact(self, artifact):
        try:
            self._validator.validate(artifact)
        except ValidationError as e:
            raise ValueError(f"Artifact validation error: {e.message}") from e
        except SchemaError as e:
            raise ValueError(f"Schema structure error: {e.message}") from e
