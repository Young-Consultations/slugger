"""Tests for TASK-050: Knowledge Base Indexing."""

from __future__ import annotations

from pathlib import Path

from knowledge.indexer import KnowledgeIndexer


def _create_kb(tmp_path: Path) -> Path:
    """Create a small mock knowledge base."""
    (tmp_path / 'security').mkdir()
    (tmp_path / 'engineering').mkdir()
    (tmp_path / 'security' / 'review.md').write_text(
        '# Security Review Guidance\n\nAlways scan for secrets.\n', encoding='utf-8'
    )
    (tmp_path / 'engineering' / 'testing.md').write_text(
        '# Testing Standards\n\n## Unit Tests\n\nUse pytest.\n', encoding='utf-8'
    )
    (tmp_path / 'README.md').write_text('# Knowledge Base\n', encoding='utf-8')
    return tmp_path


def test_index_returns_count(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    count = indexer.index()
    assert count == 3


def test_search_finds_relevant_doc(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    indexer.index()
    results = indexer.search('security')
    assert len(results) > 0
    assert 'Security' in results[0].document.title


def test_search_no_match_returns_empty(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    indexer.index()
    results = indexer.search('xyznonexistent')
    assert results == []


def test_search_empty_query_returns_empty(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    indexer.index()
    assert indexer.search('') == []


def test_get_by_path(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    indexer.index()
    doc = indexer.get_by_path('security/review.md')
    assert doc is not None
    assert 'Security' in doc.title


def test_tags_from_directory(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    indexer.index()
    doc = indexer.get_by_path('engineering/testing.md')
    assert 'engineering' in doc.tags


def test_headings_extracted(tmp_path) -> None:
    root = _create_kb(tmp_path)
    indexer = KnowledgeIndexer(root)
    indexer.index()
    doc = indexer.get_by_path('engineering/testing.md')
    assert 'Unit Tests' in doc.headings
