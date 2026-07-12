from agents.planning.product_vision_agent import ProductVisionAgent
from models import DocumentArtifact
from validators import AgentValidator, ArtifactValidator


def test_artifact_validator_detects_missing_content() -> None:
    artifact = DocumentArtifact(artifact_id="a1", name="empty", content="")
    result = ArtifactValidator().validate(artifact)
    assert not result.valid
    assert result.errors


def test_agent_validator_accepts_first_party_agent() -> None:
    result = AgentValidator().validate(ProductVisionAgent())
    assert result.valid
