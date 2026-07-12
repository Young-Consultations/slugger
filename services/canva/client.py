"""Canva Connect API REST client."""

from __future__ import annotations

import os

import requests

from services.canva.base import ICanvaService
from services.canva.models import (
    CanvaBrandTemplate,
    CanvaDesign,
    CanvaExportFormat,
    CanvaExportJob,
    CanvaFolder,
)

_CANVA_API_BASE = "https://api.canva.com/rest/v1"


class CanvaClient(ICanvaService):
    """Canva service backed by the Canva Connect REST API."""

    def __init__(
        self, access_token: str | None = None, base_url: str | None = None
    ) -> None:
        self._token = access_token or os.getenv("CANVA_API_TOKEN")
        self._base = (base_url or _CANVA_API_BASE).rstrip("/")

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = "Bearer " + self._token
        return headers

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    # ------------------------------------------------------------------
    # Designs
    # ------------------------------------------------------------------

    def list_designs(self) -> list[CanvaDesign]:
        response = requests.get(
            self._url("/designs"), headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        return [self._parse_design(item) for item in items]

    def get_design(self, design_id: str) -> CanvaDesign:
        response = requests.get(
            self._url(f"/designs/{design_id}"), headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return self._parse_design(data.get("design", data))

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------

    def export_design(
        self, design_id: str, export_format: CanvaExportFormat
    ) -> CanvaExportJob:
        payload = {"design_id": design_id, "format": export_format.value}
        response = requests.post(
            self._url("/exports"), json=payload, headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        response_data = response.json()
        data = response_data.get("job", response_data)
        return self._parse_export_job(data)

    def get_export_job(self, job_id: str) -> CanvaExportJob:
        response = requests.get(
            self._url(f"/exports/{job_id}"), headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        response_data = response.json()
        data = response_data.get("job", response_data)
        return self._parse_export_job(data)

    # ------------------------------------------------------------------
    # Folders
    # ------------------------------------------------------------------

    def list_folders(self) -> list[CanvaFolder]:
        response = requests.get(
            self._url("/folders"), headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        return [
            CanvaFolder(
                folder_id=item.get("id", ""),
                name=item.get("name", ""),
                created_at=item.get("created_at", ""),
                updated_at=item.get("updated_at", ""),
            )
            for item in items
        ]

    # ------------------------------------------------------------------
    # Brand templates
    # ------------------------------------------------------------------

    def list_brand_templates(self) -> list[CanvaBrandTemplate]:
        response = requests.get(
            self._url("/brand-templates"), headers=self._headers(), timeout=30
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        return [
            CanvaBrandTemplate(
                template_id=item.get("id", ""),
                title=item.get("title", ""),
                thumbnail_url=item.get("thumbnail", {}).get("url", ""),
                view_url=item.get("view_url", ""),
            )
            for item in items
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_design(data: dict) -> CanvaDesign:  # type: ignore[type-arg]
        thumbnail = data.get("thumbnail") or {}
        urls = data.get("urls") or {}
        return CanvaDesign(
            design_id=data.get("id", ""),
            title=data.get("title", ""),
            owner_id=(data.get("owner") or {}).get("user_id", ""),
            thumbnail_url=thumbnail.get("url", ""),
            edit_url=urls.get("edit_url", ""),
            view_url=urls.get("view_url", ""),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

    @staticmethod
    def _parse_export_job(data: dict) -> CanvaExportJob:  # type: ignore[type-arg]
        fmt_str = data.get("format", CanvaExportFormat.PDF.value)
        try:
            fmt = CanvaExportFormat(fmt_str)
        except ValueError:
            fmt = CanvaExportFormat.PDF
        exported_items = data.get("urls", [])
        return CanvaExportJob(
            job_id=data.get("id", ""),
            design_id=data.get("design_id", ""),
            status=data.get("status", "queued"),
            export_format=fmt,
            urls=exported_items,
        )
