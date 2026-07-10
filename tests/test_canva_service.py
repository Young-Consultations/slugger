"""Tests for the Canva service layer."""

from __future__ import annotations

import pytest

from services.canva import (
    CanvaDesign,
    CanvaExportFormat,
    CanvaExportJob,
    CanvaFolder,
    ICanvaService,
    MockCanvaService,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def service() -> MockCanvaService:
    svc = MockCanvaService()
    svc.designs = [
        CanvaDesign(design_id='d1', title='Pitch Deck'),
        CanvaDesign(design_id='d2', title='Social Post'),
    ]
    svc.folders = [CanvaFolder(folder_id='f1', name='Marketing')]
    return svc


# ---------------------------------------------------------------------------
# ICanvaService contract
# ---------------------------------------------------------------------------


def test_mock_service_implements_interface() -> None:
    assert issubclass(MockCanvaService, ICanvaService)


# ---------------------------------------------------------------------------
# list_designs
# ---------------------------------------------------------------------------


def test_list_designs_returns_all(service: MockCanvaService) -> None:
    designs = service.list_designs()
    assert len(designs) == 2
    assert designs[0].design_id == 'd1'
    assert designs[1].title == 'Social Post'


def test_list_designs_returns_copy(service: MockCanvaService) -> None:
    result = service.list_designs()
    result.clear()
    assert len(service.list_designs()) == 2


# ---------------------------------------------------------------------------
# get_design
# ---------------------------------------------------------------------------


def test_get_design_found(service: MockCanvaService) -> None:
    design = service.get_design('d1')
    assert design.title == 'Pitch Deck'


def test_get_design_not_found(service: MockCanvaService) -> None:
    with pytest.raises(KeyError):
        service.get_design('nonexistent')


# ---------------------------------------------------------------------------
# export_design
# ---------------------------------------------------------------------------


def test_export_design_returns_job(service: MockCanvaService) -> None:
    job = service.export_design('d1', CanvaExportFormat.PDF)
    assert isinstance(job, CanvaExportJob)
    assert job.design_id == 'd1'
    assert job.export_format == CanvaExportFormat.PDF
    assert job.status == 'success'
    assert len(job.urls) == 1


def test_export_design_increments_job_id(service: MockCanvaService) -> None:
    job1 = service.export_design('d1', CanvaExportFormat.PNG)
    job2 = service.export_design('d2', CanvaExportFormat.JPG)
    assert job1.job_id != job2.job_id


# ---------------------------------------------------------------------------
# get_export_job
# ---------------------------------------------------------------------------


def test_get_export_job_found(service: MockCanvaService) -> None:
    job = service.export_design('d1', CanvaExportFormat.SVG)
    retrieved = service.get_export_job(job.job_id)
    assert retrieved.job_id == job.job_id


def test_get_export_job_not_found(service: MockCanvaService) -> None:
    with pytest.raises(KeyError):
        service.get_export_job('job-99999')


# ---------------------------------------------------------------------------
# list_folders
# ---------------------------------------------------------------------------


def test_list_folders(service: MockCanvaService) -> None:
    folders = service.list_folders()
    assert len(folders) == 1
    assert folders[0].name == 'Marketing'


# ---------------------------------------------------------------------------
# list_brand_templates
# ---------------------------------------------------------------------------


def test_list_brand_templates_empty_by_default(service: MockCanvaService) -> None:
    assert service.list_brand_templates() == []
