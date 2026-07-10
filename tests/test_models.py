from models import DocumentArtifact, InMemoryArtifactStore, Project, ProjectPhase, ProjectStatus


def test_project_defaults() -> None:
    project = Project(project_id='p1', name='Slugger', description='AI factory')
    assert project.status is ProjectStatus.DRAFT
    assert project.phase is ProjectPhase.IDEA


def test_artifact_store_round_trip() -> None:
    artifact = DocumentArtifact(artifact_id='a1', name='requirements', content='hello')
    store = InMemoryArtifactStore()
    store.create(artifact)
    assert store.get('a1') == artifact
    assert store.find_by_name('requirements') == [artifact]
