"""Workflow engine."""

from __future__ import annotations

from pathlib import Path

from core.exceptions import WorkflowError
from models.artifact_store import InMemoryArtifactStore
from models.workflow import StepStatus
from workflow.approvals import ApprovalCheckpoint, ApprovalGateHandler
from workflow.executor import StepExecutor
from workflow.models import ApprovalPolicy, StepInstance, WorkflowDefinition, WorkflowInstance
from workflow.parser import WorkflowParser
from workflow.persistence import WorkflowPersistence


class WorkflowEngine:
    def __init__(
        self,
        recipe_directory: Path,
        parser: WorkflowParser,
        executor: StepExecutor,
        artifact_store: InMemoryArtifactStore | None = None,
        persistence: WorkflowPersistence | None = None,
        approval_handler: ApprovalGateHandler | None = None,
    ) -> None:
        self.recipe_directory = recipe_directory
        self.parser = parser
        self.executor = executor
        self.artifact_store = artifact_store or InMemoryArtifactStore()
        self.persistence = persistence
        self.approval_handler = approval_handler or ApprovalGateHandler()

    def list_workflows(self) -> list[str]:
        return sorted(path.stem for path in self.recipe_directory.glob('*.yaml'))

    def load_definition(self, workflow_name: str) -> WorkflowDefinition:
        path = Path(workflow_name)
        if not path.exists():
            path = self.recipe_directory / f'{workflow_name}.yaml'
        return self.parser.parse_file(path)

    def run(
        self,
        workflow_name: str,
        project_id: str = 'default-project',
        metadata: dict[str, str] | None = None,
    ) -> WorkflowInstance:
        definition = self.load_definition(workflow_name)
        instance = WorkflowInstance(
            definition=definition,
            step_instances=[StepInstance(definition=step) for step in definition.steps],
            status='running',
        )
        if self.persistence is not None:
            self.persistence.save(instance)
        return self._execute_instance(instance, project_id, metadata)

    def resume(
        self,
        run_id: str,
        project_id: str = 'default-project',
        metadata: dict[str, str] | None = None,
    ) -> WorkflowInstance:
        """Resume a previously interrupted workflow run identified by *run_id*.

        Steps that already succeeded are skipped; execution continues from the
        first non-succeeded step.

        Raises
        ------
        KeyError
            If *run_id* is not found in the persistence store.
        RuntimeError
            If no persistence backend is configured.
        """
        if self.persistence is None:
            raise RuntimeError('WorkflowEngine has no persistence backend configured.')
        instance = self.persistence.load(run_id)
        if instance is None:
            raise KeyError(f'Unknown workflow run: {run_id!r}')
        instance.status = 'running'
        return self._execute_instance(instance, project_id, metadata)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_approval(self, step_instance: StepInstance, run_id: str = 'default-run') -> bool:
        """Evaluate any approval policy for *step_instance*.

        Returns ``True`` if execution may proceed, ``False`` if the workflow
        should pause pending human approval.

        When the policy is configured as auto-approve (or no policy is set),
        the approval is granted immediately.
        """
        policy: ApprovalPolicy | None = step_instance.definition.approval_policy
        if policy is None:
            return True
        checkpoint = ApprovalCheckpoint(
            name=f'{step_instance.definition.name}.pre',
            description=f'Approval required before executing step: {step_instance.definition.name}',
            required_approvers=policy.required_approvers,
            auto_approve=policy.auto_approve,
            timeout_seconds=policy.timeout_seconds,
        )
        record = self.approval_handler.evaluate(run_id, checkpoint)
        step_instance.approval_record_id = record.record_id
        from workflow.approvals import ApprovalDecision
        return record.decision in (ApprovalDecision.APPROVED, ApprovalDecision.AUTO_APPROVED)

    def _execute_instance(
        self,
        instance: WorkflowInstance,
        project_id: str,
        metadata: dict[str, str] | None,
    ) -> WorkflowInstance:
        artifacts_by_name: dict[str, object] = {}
        for step_instance in instance.step_instances:
            # Skip steps that already succeeded (supports resumable execution).
            if step_instance.status == StepStatus.SUCCEEDED:
                for artifact in step_instance.artifacts:
                    artifacts_by_name[artifact.name] = artifact
                continue

            # Evaluate approval gate before executing the step (WP-022/WP-023)
            if not self._check_approval(step_instance, run_id=instance.run_id):
                step_instance.status = StepStatus.PENDING
                instance.status = 'awaiting_approval'
                if self.persistence is not None:
                    self.persistence.save(instance)
                return instance

            max_attempts = int(step_instance.definition.retry_policy.get('max_attempts', 1))
            while step_instance.attempts < max_attempts:
                step_instance.attempts += 1
                step_instance.status = StepStatus.RUNNING
                try:
                    artifacts, results = self.executor.execute(
                        instance.definition.name,
                        project_id,
                        step_instance,
                        artifacts_by_name,
                        metadata=metadata,
                    )
                    if any(not result.valid for result in results):
                        raise WorkflowError(f'Quality gate failure in step {step_instance.definition.name}')
                    for artifact in artifacts:
                        self.artifact_store.create(artifact)
                        artifacts_by_name[artifact.name] = artifact
                        instance.artifacts.append(artifact)
                    if step_instance.definition.outputs:
                        missing = [name for name in step_instance.definition.outputs if name not in artifacts_by_name]
                        if missing:
                            raise WorkflowError(f'Step {step_instance.definition.name} missing outputs: {missing}')
                    step_instance.status = StepStatus.SUCCEEDED
                    if self.persistence is not None:
                        self.persistence.save(instance)
                    break
                except Exception as error:
                    if step_instance.attempts >= max_attempts:
                        step_instance.status = StepStatus.FAILED
                        instance.status = 'failed'
                        if self.persistence is not None:
                            self.persistence.save(instance)
                        raise WorkflowError(str(error)) from error
            if step_instance.status != StepStatus.SUCCEEDED:
                break
        else:
            instance.status = 'succeeded'
            if self.persistence is not None:
                self.persistence.save(instance)
        return instance
