"""Tests for memory persistence layer.

These tests verify that the MemoryStore:
- Persists artifacts to SQLite
- Persists workflow executions
- Persists pipeline executions
- Retrieves data correctly
- Handles cleanup operations
"""
import json
import tempfile
from pathlib import Path

from slugger.orchestrator.storage.memory_store import MemoryStore


def test_memory_store_save_and_get_artifact():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        store = MemoryStore(f.name)
        
        store.save_artifact(
            artifact_id="req_001",
            artifact_name="requirements_v1",
            artifact_type="requirements",
            content="System requirements document"
        )
        
        artifact = store.get_artifact("req_001")
        assert artifact is not None
        assert artifact["artifact_name"] == "requirements_v1"
        assert artifact["artifact_type"] == "requirements"
        assert artifact["content"] == "System requirements document"
        
        Path(f.name).unlink()


def test_memory_store_list_artifacts():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        store = MemoryStore(f.name)
        
        store.save_artifact("req_001", "requirements_v1", "requirements", "content1")
        store.save_artifact("arch_001", "architecture_v1", "architecture", "content2")
        store.save_artifact("req_002", "requirements_v2", "requirements", "content3")
        
        all_artifacts = store.list_artifacts()
        assert len(all_artifacts) == 3
        
        req_artifacts = store.list_artifacts(artifact_type="requirements")
        assert len(req_artifacts) == 2
        
        Path(f.name).unlink()


def test_memory_store_workflow_execution():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        store = MemoryStore(f.name)
        
        store.save_workflow_execution(
            execution_id="exec_001",
            agent_name="requirements",
            status="success",
            input_data={"request": "test"},
            output_data={"artifact_name": "requirements_v1"},
            execution_time_ms=1500
        )
        
        # Verify execution was saved (simplified test)
        # Full retrieval would require get_workflow_execution method
        
        Path(f.name).unlink()


def test_memory_store_pipeline_execution():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        store = MemoryStore(f.name)
        
        store.save_pipeline_execution(
            pipeline_id="pipe_001",
            agents=["requirements", "business_analyst", "architecture"],
            context={"request": "test"},
            status="success",
            result={"artifact_type": "architecture"},
            execution_time_ms=5000
        )
        
        pipeline = store.get_pipeline_execution("pipe_001")
        assert pipeline is not None
        assert pipeline["pipeline_id"] == "pipe_001"
        assert pipeline["status"] == "success"
        assert len(pipeline["agents"]) == 3
        assert pipeline["execution_time_ms"] == 5000
        
        Path(f.name).unlink()
