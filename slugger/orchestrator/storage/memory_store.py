"""Memory persistence layer.

This module provides persistent storage for artifacts, conversations, and workflow state
using SQLite for local development and pluggable backends for production.
"""
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class MemoryStore:
    """Persistent storage for orchestrator state and artifacts."""

    def __init__(self, db_path: str = "slugger.db"):
        """Initialize memory store with SQLite backend.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Artifacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY,
                artifact_id TEXT UNIQUE NOT NULL,
                artifact_name TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                conversation_id TEXT UNIQUE NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                turn_number INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Workflow execution table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id INTEGER PRIMARY KEY,
                execution_id TEXT UNIQUE NOT NULL,
                agent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                input_data TEXT,
                output_data TEXT,
                error_message TEXT,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Pipeline executions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_executions (
                id INTEGER PRIMARY KEY,
                pipeline_id TEXT UNIQUE NOT NULL,
                agents TEXT NOT NULL,
                context TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                error_message TEXT,
                execution_time_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def save_artifact(self, artifact_id: str, artifact_name: str, artifact_type: str, content: str) -> None:
        """Save artifact to persistent storage.
        
        Args:
            artifact_id: Unique identifier for the artifact
            artifact_name: Human-readable name
            artifact_type: Type of artifact (e.g., 'requirements', 'code_scaffold')
            content: Full artifact content
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO artifacts (artifact_id, artifact_name, artifact_type, content)
            VALUES (?, ?, ?, ?)
        """, (artifact_id, artifact_name, artifact_type, content))
        conn.commit()
        conn.close()

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve artifact from persistent storage.
        
        Args:
            artifact_id: Unique identifier for the artifact
            
        Returns:
            Artifact dict or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT artifact_id, artifact_name, artifact_type, content, created_at FROM artifacts WHERE artifact_id = ?",
            (artifact_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "artifact_id": row[0],
                "artifact_name": row[1],
                "artifact_type": row[2],
                "content": row[3],
                "created_at": row[4],
            }
        return None

    def list_artifacts(self, artifact_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all artifacts, optionally filtered by type.
        
        Args:
            artifact_type: Optional filter by artifact type
            
        Returns:
            List of artifact dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if artifact_type:
            cursor.execute(
                "SELECT artifact_id, artifact_name, artifact_type, created_at FROM artifacts WHERE artifact_type = ? ORDER BY created_at DESC",
                (artifact_type,)
            )
        else:
            cursor.execute(
                "SELECT artifact_id, artifact_name, artifact_type, created_at FROM artifacts ORDER BY created_at DESC"
            )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "artifact_id": row[0],
                "artifact_name": row[1],
                "artifact_type": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    def save_workflow_execution(self, execution_id: str, agent_name: str, status: str, 
                               input_data: Dict[str, Any], output_data: Optional[Dict[str, Any]] = None,
                               error_message: Optional[str] = None, execution_time_ms: int = 0) -> None:
        """Save workflow execution record.
        
        Args:
            execution_id: Unique identifier for the execution
            agent_name: Name of the agent that executed
            status: Execution status ('success', 'error', 'pending')
            input_data: Input data provided to agent
            output_data: Output data from agent
            error_message: Error message if status is 'error'
            execution_time_ms: Execution time in milliseconds
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workflow_executions 
            (execution_id, agent_name, status, input_data, output_data, error_message, execution_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            execution_id,
            agent_name,
            status,
            json.dumps(input_data),
            json.dumps(output_data) if output_data else None,
            error_message,
            execution_time_ms
        ))
        conn.commit()
        conn.close()

    def save_pipeline_execution(self, pipeline_id: str, agents: List[str], context: Dict[str, Any],
                               status: str, result: Optional[Dict[str, Any]] = None,
                               error_message: Optional[str] = None, execution_time_ms: int = 0) -> None:
        """Save pipeline execution record.
        
        Args:
            pipeline_id: Unique identifier for the pipeline execution
            agents: List of agents in the pipeline
            context: Initial context for the pipeline
            status: Pipeline status ('success', 'error', 'in_progress')
            result: Final result from pipeline
            error_message: Error message if status is 'error'
            execution_time_ms: Total execution time in milliseconds
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pipeline_executions
            (pipeline_id, agents, context, status, result, error_message, execution_time_ms, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pipeline_id,
            json.dumps(agents),
            json.dumps(context),
            status,
            json.dumps(result) if result else None,
            error_message,
            execution_time_ms,
            datetime.now().isoformat() if status in ['success', 'error'] else None
        ))
        conn.commit()
        conn.close()

    def get_pipeline_execution(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve pipeline execution record.
        
        Args:
            pipeline_id: Unique identifier for the pipeline execution
            
        Returns:
            Pipeline execution dict or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pipeline_id, agents, context, status, result, error_message, execution_time_ms, created_at FROM pipeline_executions WHERE pipeline_id = ?",
            (pipeline_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "pipeline_id": row[0],
                "agents": json.loads(row[1]),
                "context": json.loads(row[2]),
                "status": row[3],
                "result": json.loads(row[4]) if row[4] else None,
                "error_message": row[5],
                "execution_time_ms": row[6],
                "created_at": row[7],
            }
        return None

    def cleanup(self, days: int = 30) -> int:
        """Clean up old execution records.
        
        Args:
            days: Delete records older than N days
            
        Returns:
            Number of records deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM workflow_executions WHERE created_at < datetime('now', ?)",
            (f'-{days} days',)
        )
        cursor.execute(
            "DELETE FROM pipeline_executions WHERE created_at < datetime('now', ?)",
            (f'-{days} days',)
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
