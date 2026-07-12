"""Canva service models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CanvaExportFormat(str, Enum):
    """Supported export formats for Canva designs."""

    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    MP4 = "mp4"
    GIF = "gif"
    PPTX = "pptx"


@dataclass(slots=True)
class CanvaDesign:
    """Represents a Canva design."""

    design_id: str
    title: str
    owner_id: str = ""
    thumbnail_url: str = ""
    edit_url: str = ""
    view_url: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class CanvaExportJob:
    """Represents an export job result."""

    job_id: str
    design_id: str
    status: str = "queued"
    export_format: CanvaExportFormat = CanvaExportFormat.PDF
    urls: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CanvaFolder:
    """Represents a Canva folder."""

    folder_id: str
    name: str
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class CanvaBrandTemplate:
    """Represents a Canva brand template."""

    template_id: str
    title: str
    thumbnail_url: str = ""
    view_url: str = ""
