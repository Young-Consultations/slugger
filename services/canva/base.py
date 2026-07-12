"""Canva service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from services.canva.models import (
    CanvaBrandTemplate,
    CanvaDesign,
    CanvaExportFormat,
    CanvaExportJob,
    CanvaFolder,
)


class ICanvaService(ABC):
    """Abstract interface for the Canva Connect API."""

    @abstractmethod
    def list_designs(self) -> list[CanvaDesign]:
        """Return all designs accessible to the authenticated user."""

    @abstractmethod
    def get_design(self, design_id: str) -> CanvaDesign:
        """Return metadata for a single design."""

    @abstractmethod
    def export_design(
        self, design_id: str, export_format: CanvaExportFormat
    ) -> CanvaExportJob:
        """Initiate an export job for the given design and format."""

    @abstractmethod
    def get_export_job(self, job_id: str) -> CanvaExportJob:
        """Poll the status of an existing export job."""

    @abstractmethod
    def list_folders(self) -> list[CanvaFolder]:
        """Return all folders accessible to the authenticated user."""

    @abstractmethod
    def list_brand_templates(self) -> list[CanvaBrandTemplate]:
        """Return all brand templates accessible to the authenticated user."""
