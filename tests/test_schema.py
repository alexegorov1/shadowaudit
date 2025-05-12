import pytest
from core.schema_validator import ArtifactSchemaValidator

@pytest.fixture
def validator():
    return ArtifactSchemaValidator()

def test_valid_artifact_minimal_passes(validator):
    artifact = {
        "host_id": "host-123",
        "source": "filesystem",
        "collected_at": "2024-01-01T12:00:00Z",
        "artifact_type": "suspicious_file",
        "confidence": 0.85,
        "evidence_type": "persistence"
    }
    try:
        validator.validate_artifact(artifact)
    except Exception as e:
        pytest.fail(f"Validation unexpectedly failed: {e}")

@pytest.mark.parametrize("missing_field", [
    "host_id", "source", "collected_at", "artifact_type", "confidence", "evidence_type"
])
def test_missing_required_field_fails(validator, missing_field):
    artifact = {
        "host_id": "a", "source": "b", "collected_at": "2024-01-01T00:00:00Z",
        "artifact_type": "x", "confidence": 0.5, "evidence_type": "y"
    }
    artifact.pop(missing_field)
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)

@pytest.mark.parametrize("bad_confidence", [-0.1, 1.1, "not-a-number", None])
def test_invalid_confidence_value_fails(validator, bad_confidence):
    artifact = {
        "host_id": "h", "source": "s", "collected_at": "2024-01-01T00:00:00Z",
        "artifact_type": "t", "confidence": bad_confidence, "evidence_type": "e"
    }
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)

@pytest.mark.parametrize("bad_time", ["2024-01-01", "01/01/2024", "yesterday"])
def test_invalid_timestamp_format_fails(validator, bad_time):
    artifact = {
        "host_id": "h", "source": "s", "collected_at": bad_time,
        "artifact_type": "t", "confidence": 0.7, "evidence_type": "e"
    }
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)

def test_additional_fields_are_accepted(validator):
    artifact = {
        "host_id": "abc",
        "source": "test",
        "collected_at": "2024-01-01T12:00:00Z",
        "artifact_type": "generic",
        "confidence": 1.0,
        "evidence_type": "execution",
        "extra_field": "allowed_by_additionalProperties"
    }
    try:
        validator.validate_artifact(artifact)
    except Exception as e:
        pytest.fail(f"Validation failed on valid extended artifact: {e}")

def test_empty_string_fields_fail(validator):
    artifact = {
        "host_id": "",
        "source": "",
        "collected_at": "2024-01-01T12:00:00Z",
        "artifact_type": "",
        "confidence": 0.5,
        "evidence_type": ""
    }
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)
