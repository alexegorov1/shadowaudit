import os
import json
from jsonschema.validators import validator_for

class ArtifactSchemaValidator:

    def validate_artifact(self, artifact):
        try:
            self._validator.validate(artifact)
        except ValidationError as e:
            raise ValueError(f"Artifact validation error: {e.message}") from e
        except SchemaError as e:
            raise ValueError(f"Schema structure error: {e.message}") from e
