from __future__ import annotations

import sqlite3
from typing import Any


def fts_query(query: str) -> str:
    tokens = [token.replace('"', "") for token in query.split() if token.strip()]
    return " ".join(tokens)


def search_rows(conn: sqlite3.Connection, query: str, limit: int = 10) -> list[dict[str, Any]]:
    match = fts_query(query)
    try:
        page_rows = conn.execute(
            """
            SELECT 'page' AS kind, p.path, p.title,
                   snippet(pages_fts, 2, '[', ']', '...', 14) AS snippet,
                   bm25(pages_fts) AS rank
            FROM pages_fts
            JOIN pages p ON p.id = pages_fts.rowid
            WHERE pages_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (match, limit),
        ).fetchall()
        source_rows = conn.execute(
            """
            SELECT 'source' AS kind, s.path, s.title,
                   snippet(sources_fts, 1, '[', ']', '...', 14) AS snippet,
                   bm25(sources_fts) AS rank
            FROM sources_fts
            JOIN sources s ON s.id = sources_fts.rowid
            WHERE sources_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (match, limit),
        ).fetchall()
        rows = sorted([*page_rows, *source_rows], key=lambda row: row["rank"])[:limit]
        return [dict(row) for row in rows]
    except sqlite3.OperationalError:
        pass

    like = f"%{query}%"
    rows = conn.execute(
        """
        SELECT 'page' AS kind, path, title, summary AS snippet, 0 AS rank
        FROM pages
        WHERE title LIKE ? OR summary LIKE ?
        UNION ALL
        SELECT 'source' AS kind, path, title, '' AS snippet, 0 AS rank
        FROM sources
        WHERE title LIKE ? OR path LIKE ?
        LIMIT ?
        """,
        (like, like, like, like, limit),
    ).fetchall()
    return [dict(row) for row in rows]


def list_event_rows(conn: sqlite3.Connection, limit: int = 20) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT occurred_at, kind, actor, object_path, summary, metadata_json
        FROM events
        ORDER BY occurred_at DESC, id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]
