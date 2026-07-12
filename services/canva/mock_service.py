"""Mock Canva service for testing and offline use."""

from __future__ import annotations

from services.canva.base import ICanvaService
from services.canva.models import (
    CanvaBrandTemplate,
    CanvaDesign,
    CanvaExportFormat,
    CanvaExportJob,
    CanvaFolder,
)


class MockCanvaService(ICanvaService):
    """In-memory Canva service that requires no network access."""

    def __init__(self) -> None:
        self.designs: list[CanvaDesign] = []
        self.export_jobs: dict[str, CanvaExportJob] = {}
        self.folders: list[CanvaFolder] = []
        self.brand_templates: list[CanvaBrandTemplate] = []
        self._next_job_id = 1

    def list_designs(self) -> list[CanvaDesign]:
        return list(self.designs)

    def get_design(self, design_id: str) -> CanvaDesign:
        for design in self.designs:
            if design.design_id == design_id:
                return design
        raise KeyError(f"Design not found: {design_id}")

    def export_design(
        self, design_id: str, export_format: CanvaExportFormat
    ) -> CanvaExportJob:
        job_id = f"job-{self._next_job_id}"
        self._next_job_id += 1
        job = CanvaExportJob(
            job_id=job_id,
            design_id=design_id,
            status="success",
            export_format=export_format,
            urls=[f"https://export.canva.com/{design_id}.{export_format.value}"],
        )
        self.export_jobs[job_id] = job
        return job

    def get_export_job(self, job_id: str) -> CanvaExportJob:
        if job_id not in self.export_jobs:
            raise KeyError(f"Export job not found: {job_id}")
        return self.export_jobs[job_id]

    def list_folders(self) -> list[CanvaFolder]:
        return list(self.folders)

    def list_brand_templates(self) -> list[CanvaBrandTemplate]:
        return list(self.brand_templates)
