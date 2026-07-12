"""Knowledge base indexer — build a searchable in-memory index of markdown documents.

:class:`KnowledgeIndexer` walks a directory tree of markdown files, extracts
headings and text, and provides keyword-based search.  Results include the
document path, matched headings, and a relevance score.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# --------------------------------------------------------------------------- #
# Models                                                                       #
# --------------------------------------------------------------------------- #


@dataclass
class KnowledgeDocument:
    """A single indexed knowledge-base document.

    Parameters
    ----------
    path:
        Relative path within the knowledge directory.
    title:
        Primary heading (first ``#`` heading) or derived from filename.
    headings:
        All headings extracted from the document.
    content:
        Full raw content of the document.
    tags:
        Labels derived from the directory structure or frontmatter.
    """

    path: str
    title: str
    headings: list[str] = field(default_factory=list)
    content: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """A knowledge-base search hit."""

    document: KnowledgeDocument
    score: float
    matched_terms: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Indexer                                                                      #
# --------------------------------------------------------------------------- #

_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)", re.MULTILINE)


def _extract_headings(content: str) -> list[str]:
    return _HEADING_RE.findall(content)


def _score(document: KnowledgeDocument, terms: list[str]) -> tuple[float, list[str]]:
    """Return a relevance score and list of matched terms."""
    text = (
        document.title + " " + " ".join(document.headings) + " " + document.content
    ).lower()
    matched: list[str] = []
    for term in terms:
        if term.lower() in text:
            matched.append(term)
    # Heading/title matches score higher than body matches
    title_hits = sum(1 for t in matched if t.lower() in document.title.lower())
    heading_hits = sum(
        1 for t in matched if any(t.lower() in h.lower() for h in document.headings)
    )
    score = len(matched) + title_hits * 2 + heading_hits
    return float(score), matched


class KnowledgeIndexer:
    """Build and search an index of markdown knowledge-base documents.

    Parameters
    ----------
    root:
        Root directory of the knowledge base.

    Examples
    --------
    >>> indexer = KnowledgeIndexer(Path('knowledge'))
    >>> indexer.index()
    42  # documents indexed
    >>> results = indexer.search('security scanning')
    >>> results[0].document.title
    'Security Review Guidance'
    """

    def __init__(self, root: Path) -> None:
        self.root = root
        self._documents: list[KnowledgeDocument] = []

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index(self) -> int:
        """Walk *root* and index all ``*.md`` files.

        Returns
        -------
        int
            Number of documents indexed.
        """
        self._documents.clear()
        for md_file in sorted(self.root.rglob("*.md")):
            doc = self._index_file(md_file)
            self._documents.append(doc)
        return len(self._documents)

    def _index_file(self, path: Path) -> KnowledgeDocument:
        content = path.read_text(encoding="utf-8", errors="replace")
        headings = _extract_headings(content)
        title = (
            headings[0]
            if headings
            else path.stem.replace("-", " ").replace("_", " ").title()
        )
        # Derive tags from directory components relative to root
        rel = path.relative_to(self.root)
        tags = [part for part in rel.parts[:-1]]
        return KnowledgeDocument(
            path=str(rel),
            title=title,
            headings=headings,
            content=content,
            tags=tags,
        )

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Return the top *limit* documents matching *query*.

        *query* is split on whitespace into individual terms.  Documents are
        ranked by the number of term hits, with title/heading matches weighted
        higher.

        Parameters
        ----------
        query:
            Free-text search query.
        limit:
            Maximum number of results to return.

        Returns
        -------
        list[SearchResult]
            Ordered by descending relevance score.
        """
        terms = query.split()
        if not terms:
            return []
        results: list[SearchResult] = []
        for doc in self._documents:
            score, matched = _score(doc, terms)
            if score > 0:
                results.append(
                    SearchResult(document=doc, score=score, matched_terms=matched)
                )
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def documents(self) -> list[KnowledgeDocument]:
        """All indexed documents."""
        return list(self._documents)

    def get_by_path(self, path: str) -> KnowledgeDocument | None:
        """Return the document at *path* (relative to root), or ``None``."""
        for doc in self._documents:
            if doc.path == path:
                return doc
        return None
