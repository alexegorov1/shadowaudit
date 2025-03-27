import pytest
from core.schema_validator import ArtifactSchemaValidator

validator = ArtifactSchemaValidator()

def test_valid_artifact_passes():
    artifact = {
        "host_id": "host-123",
        "source": "filesystem",
        "collected_at": "2024-01-01T12:00:00Z",
        "artifact_type": "suspicious_file",
        "confidence": 0.85,
        "evidence_type": "persistence"
    }
    validator.validate_artifact(artifact)

def test_missing_required_field_fails():
    artifact = {
        "source": "registry",
        "collected_at": "2024-01-01T12:00:00Z",
        "artifact_type": "registry_key",
        "confidence": 0.7,
        "evidence_type": "execution"
    }
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)

def test_invalid_confidence_type_fails():
    artifact = {
        "host_id": "host-001",
        "source": "registry",
        "collected_at": "2024-01-01T12:00:00Z",
        "artifact_type": "registry_key",
        "confidence": "high",
        "evidence_type": "execution"
    }
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)

def test_invalid_timestamp_format_fails():
    artifact = {
        "host_id": "host-002",
        "source": "logon",
        "collected_at": "01-01-2024 12:00",
        "artifact_type": "logon_event",
        "confidence": 0.5,
        "evidence_type": "access"
    }
    with pytest.raises(ValueError):
        validator.validate_artifact(artifact)
