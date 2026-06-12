from __future__ import annotations

import hashlib
import json
import re
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .extractors import extract_text
from .markdown import (
    extract_wikilinks,
    list_value,
    normalize_title,
    parse_frontmatter,
    parse_frontmatter_result,
    read_markdown,
    slugify,
    summary_from_markdown,
    title_from_markdown,
)
from .paths import (
    DB_PATH,
    PAGE_DIR_BY_TYPE,
    PAGE_TYPE_BY_DIR,
    WIKI_DIRS,
    is_text_file,
    relative_posix,
)
from .db_search import fts_query, list_event_rows, search_rows


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'file',
  sha256 TEXT NOT NULL DEFAULT '',
  size_bytes INTEGER NOT NULL DEFAULT 0,
  available INTEGER NOT NULL DEFAULT 1,
  added_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS pages (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  page_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  confidence TEXT NOT NULL DEFAULT 'medium',
  summary TEXT NOT NULL DEFAULT '',
  content_hash TEXT NOT NULL,
  source_count INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS page_sources (
  page_id INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
  source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  relation TEXT NOT NULL DEFAULT 'supports',
  PRIMARY KEY (page_id, source_id)
);

CREATE TABLE IF NOT EXISTS links (
  id INTEGER PRIMARY KEY,
  from_page_id INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
  to_title TEXT NOT NULL,
  to_page_id INTEGER REFERENCES pages(id) ON DELETE SET NULL,
  line INTEGER NOT NULL DEFAULT 0,
  context TEXT NOT NULL DEFAULT '',
  UNIQUE (from_page_id, to_title, line, context)
);

CREATE TABLE IF NOT EXISTS claims (
  id INTEGER PRIMARY KEY,
  page_id INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
  claim_text TEXT NOT NULL,
  source_path TEXT NOT NULL DEFAULT '',
  source_locator TEXT NOT NULL DEFAULT '',
  confidence TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'unreviewed',
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS tags (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS page_tags (
  page_id INTEGER NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
  tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (page_id, tag_id)
);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY,
  occurred_at TEXT NOT NULL,
  event_key TEXT NOT NULL DEFAULT '',
  kind TEXT NOT NULL,
  actor TEXT NOT NULL DEFAULT 'agent',
  object_path TEXT NOT NULL DEFAULT '',
  summary TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS review_items (
  id INTEGER PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'open',
  kind TEXT NOT NULL,
  priority INTEGER NOT NULL DEFAULT 3,
  title TEXT NOT NULL,
  path TEXT NOT NULL DEFAULT '',
  detail TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL,
  resolved_at TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS source_extracts (
  source_id INTEGER PRIMARY KEY REFERENCES sources(id) ON DELETE CASCADE,
  source_sha256 TEXT NOT NULL,
  extracted_text TEXT NOT NULL DEFAULT '',
  extractor TEXT NOT NULL DEFAULT '',
  warnings_json TEXT NOT NULL DEFAULT '[]',
  updated_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS ingest_jobs (
  id INTEGER PRIMARY KEY,
  source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  source_path TEXT NOT NULL,
  source_sha256 TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  priority INTEGER NOT NULL DEFAULT 5,
  attempts INTEGER NOT NULL DEFAULT 0,
  queued_at TEXT NOT NULL,
  started_at TEXT,
  completed_at TEXT,
  failed_at TEXT,
  result_pages_json TEXT NOT NULL DEFAULT '[]',
  notes TEXT NOT NULL DEFAULT '',
  error TEXT NOT NULL DEFAULT '',
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS task_records (
  path TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  role_owner TEXT NOT NULL DEFAULT '',
  created TEXT NOT NULL DEFAULT '',
  objective TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_sources_path ON sources(path);
CREATE INDEX IF NOT EXISTS idx_pages_path ON pages(path);
CREATE INDEX IF NOT EXISTS idx_pages_title ON pages(title);
CREATE INDEX IF NOT EXISTS idx_links_from ON links(from_page_id);
CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_page_id);
CREATE INDEX IF NOT EXISTS idx_source_extracts_hash ON source_extracts(source_sha256);
CREATE INDEX IF NOT EXISTS idx_ingest_jobs_status ON ingest_jobs(status, priority, queued_at);
CREATE INDEX IF NOT EXISTS idx_task_records_status ON task_records(status, path);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ingest_jobs_active_source
  ON ingest_jobs(source_id)
  WHERE status IN ('queued', 'in_progress');
"""


LOG_HEADING_RE = re.compile(r"^## \[(?P<date>\d{4}-\d{2}-\d{2})\]\s+(?P<kind>[^|]+?)\s*\|\s*(?P<summary>.+?)\s*$")
LOG_PATH_RE = re.compile(r"-\s+Path:\s+`([^`]+)`")


@dataclass(frozen=True)
class RebuildStats:
    sources: int
    pages: int
    links: int
    fts_enabled: bool


@dataclass(frozen=True)
class LintIssue:
    severity: str
    path: str
    message: str


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def connect(root: Path) -> sqlite3.Connection:
    db_path = root / DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database(conn: sqlite3.Connection) -> bool:
    conn.executescript(SCHEMA)
    migrate_database(conn)
    fts_enabled = ensure_fts(conn)
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
        ("schema_version", "2"),
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
        ("fts5_enabled", "true" if fts_enabled else "false"),
    )
    conn.commit()
    return fts_enabled


def migrate_database(conn: sqlite3.Connection) -> None:
    ensure_column(conn, "events", "event_key", "TEXT NOT NULL DEFAULT ''")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_events_event_key ON events(event_key) WHERE event_key <> ''")


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def ensure_fts(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(title, summary, body, path)"
        )
        conn.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS sources_fts USING fts5(title, body, path)"
        )
    except sqlite3.OperationalError:
        return False
    return True


def ensure_project(root: Path) -> bool:
    for rel in WIKI_DIRS:
        (root / rel).mkdir(parents=True, exist_ok=True)
    conn = connect(root)
    try:
        return initialize_database(conn)
    finally:
        conn.close()


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text_preview(path: Path, max_chars: int = 200_000) -> str:
    if not is_text_file(path):
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:max_chars]
    except OSError:
        return ""


def sync_source_extracts(root: Path, conn: sqlite3.Connection) -> int:
    count = 0
    timestamp = now_iso()
    rows = conn.execute(
        "SELECT id, path, sha256 FROM sources WHERE available = 1 AND kind = 'file' ORDER BY path"
    ).fetchall()
    for row in rows:
        existing = conn.execute(
            "SELECT source_sha256, extractor FROM source_extracts WHERE source_id = ?",
            (row["id"],),
        ).fetchone()
        needs_refresh = (
            existing is None
            or existing["source_sha256"] != row["sha256"]
            or str(existing["extractor"]).startswith("missing-")
        )
        if not needs_refresh:
            continue
        extracted = extract_text(root / row["path"])
        conn.execute(
            """
            INSERT INTO source_extracts(source_id, source_sha256, extracted_text, extractor, warnings_json, updated_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, '{}')
            ON CONFLICT(source_id) DO UPDATE SET
              source_sha256=excluded.source_sha256,
              extracted_text=excluded.extracted_text,
              extractor=excluded.extractor,
              warnings_json=excluded.warnings_json,
              updated_at=excluded.updated_at,
              metadata_json=excluded.metadata_json
            """,
            (
                row["id"],
                row["sha256"],
                extracted.text,
                extracted.extractor,
                json.dumps(extracted.warnings, ensure_ascii=False),
                timestamp,
            ),
        )
        count += 1
    return count


def sync_sources(root: Path, conn: sqlite3.Connection) -> int:
    source_root = root / "raw" / "sources"
    seen: set[str] = set()
    count = 0
    timestamp = now_iso()
    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or path.name == ".gitkeep":
            continue
        rel = relative_posix(path, root)
        seen.add(rel)
        stat = path.stat()
        sha = hash_file(path)
        title = path.stem.replace("-", " ").replace("_", " ").strip() or path.name
        metadata = {"extension": path.suffix.lower()}
        conn.execute(
            """
            INSERT INTO sources(path, title, kind, sha256, size_bytes, available, added_at, updated_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
              title=excluded.title,
              kind=excluded.kind,
              sha256=excluded.sha256,
              size_bytes=excluded.size_bytes,
              available=1,
              updated_at=excluded.updated_at,
              metadata_json=excluded.metadata_json
            """,
            (rel, title, "file", sha, stat.st_size, timestamp, timestamp, json.dumps(metadata)),
        )
        count += 1

    if seen:
        placeholders = ",".join("?" for _ in seen)
        conn.execute(
            f"UPDATE sources SET available=0, updated_at=? WHERE path LIKE 'raw/sources/%' AND path NOT IN ({placeholders})",
            [timestamp, *sorted(seen)],
        )
    else:
        conn.execute(
            "UPDATE sources SET available=0, updated_at=? WHERE path LIKE 'raw/sources/%'",
            (timestamp,),
        )
    return count


def page_type_for(rel_path: str, metadata: dict[str, Any]) -> str:
    explicit = metadata.get("type")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    parts = Path(rel_path).parts
    if len(parts) >= 2 and parts[0] == "wiki":
        if parts[1] in PAGE_TYPE_BY_DIR:
            return PAGE_TYPE_BY_DIR[parts[1]]
        if parts[1] == "overview.md":
            return "overview"
        if parts[1] == "index.md":
            return "index"
        if parts[1] == "log.md":
            return "log"
        if parts[1] == "review.md":
            return "overview"
    return "note"


def iter_wiki_pages(root: Path) -> list[Path]:
    wiki_root = root / "wiki"
    paths = []
    for path in sorted(wiki_root.rglob("*.md")):
        rel = path.relative_to(wiki_root).as_posix()
        if rel.startswith("templates/"):
            continue
        paths.append(path)
    return paths


def ensure_source_reference(conn: sqlite3.Connection, source_path: str) -> int:
    row = conn.execute("SELECT id FROM sources WHERE path = ?", (source_path,)).fetchone()
    if row:
        return int(row["id"])
    timestamp = now_iso()
    cursor = conn.execute(
        """
        INSERT INTO sources(path, title, kind, sha256, size_bytes, available, added_at, updated_at, metadata_json)
        VALUES (?, ?, 'reference', '', 0, 0, ?, ?, '{}')
        """,
        (source_path, Path(source_path).stem or source_path, timestamp, timestamp),
    )
    return int(cursor.lastrowid)


def sync_pages(root: Path, conn: sqlite3.Connection) -> int:
    seen: set[str] = set()
    timestamp = now_iso()
    count = 0
    for path in iter_wiki_pages(root):
        text = read_markdown(path)
        rel = relative_posix(path, root)
        seen.add(rel)
        metadata = parse_frontmatter(text)
        title = title_from_markdown(path, text, metadata)
        summary = summary_from_markdown(text, metadata)
        page_type = page_type_for(rel, metadata)
        status = str(metadata.get("status", "draft"))
        confidence = str(metadata.get("confidence", "medium"))
        sources = list_value(metadata.get("sources"))
        known_metadata = {
            "title",
            "type",
            "status",
            "confidence",
            "summary",
            "sources",
            "tags",
            "created",
            "updated",
        }
        extra_metadata = {k: v for k, v in metadata.items() if k not in known_metadata}

        cursor = conn.execute(
            """
            INSERT INTO pages(path, title, page_type, status, confidence, summary, content_hash, source_count, created_at, updated_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
              title=excluded.title,
              page_type=excluded.page_type,
              status=excluded.status,
              confidence=excluded.confidence,
              summary=excluded.summary,
              content_hash=excluded.content_hash,
              source_count=excluded.source_count,
              updated_at=excluded.updated_at,
              metadata_json=excluded.metadata_json
            """,
            (
                rel,
                title,
                page_type,
                status,
                confidence,
                summary,
                hash_text(text),
                len(sources),
                timestamp,
                timestamp,
                json.dumps(extra_metadata, ensure_ascii=False, default=str),
            ),
        )
        page_id = conn.execute("SELECT id FROM pages WHERE path = ?", (rel,)).fetchone()["id"]

        conn.execute("DELETE FROM page_sources WHERE page_id = ?", (page_id,))
        for source in sources:
            source_id = ensure_source_reference(conn, source)
            conn.execute(
                "INSERT OR IGNORE INTO page_sources(page_id, source_id, relation) VALUES (?, ?, 'supports')",
                (page_id, source_id),
            )

        conn.execute("DELETE FROM page_tags WHERE page_id = ?", (page_id,))
        for tag in list_value(metadata.get("tags")):
            conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (tag,))
            tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()["id"]
            conn.execute(
                "INSERT OR IGNORE INTO page_tags(page_id, tag_id) VALUES (?, ?)",
                (page_id, tag_id),
            )

        count += 1
        _ = cursor

    if seen:
        placeholders = ",".join("?" for _ in seen)
        conn.execute(f"DELETE FROM pages WHERE path NOT IN ({placeholders})", sorted(seen))
    else:
        conn.execute("DELETE FROM pages")
    return count


def rebuild_links(root: Path, conn: sqlite3.Connection) -> int:
    conn.execute("DELETE FROM links")
    pages = conn.execute("SELECT id, path, title FROM pages").fetchall()
    title_index: dict[str, int] = {}
    for page in pages:
        title_index[normalize_title(page["title"])] = int(page["id"])
        title_index[normalize_title(Path(page["path"]).stem)] = int(page["id"])

    count = 0
    for page in pages:
        path = root / page["path"]
        if not path.exists():
            continue
        text = read_markdown(path)
        for link in extract_wikilinks(text):
            target_id = title_index.get(normalize_title(link.target))
            conn.execute(
                """
                INSERT OR IGNORE INTO links(from_page_id, to_title, to_page_id, line, context)
                VALUES (?, ?, ?, ?, ?)
                """,
                (page["id"], link.target, target_id, link.line, link.context),
            )
            count += 1
    return count


def rebuild_fts(root: Path, conn: sqlite3.Connection) -> bool:
    if not ensure_fts(conn):
        return False
    conn.execute("DELETE FROM pages_fts")
    conn.execute("DELETE FROM sources_fts")
    for page in conn.execute("SELECT id, path, title, summary FROM pages").fetchall():
        text = read_text_preview(root / page["path"])
        conn.execute(
            "INSERT INTO pages_fts(rowid, title, summary, body, path) VALUES (?, ?, ?, ?, ?)",
            (page["id"], page["title"], page["summary"], text, page["path"]),
        )
    for source in conn.execute(
        """
        SELECT s.id, s.path, s.title, COALESCE(se.extracted_text, '') AS extracted_text
        FROM sources s
        LEFT JOIN source_extracts se ON se.source_id = s.id
        WHERE s.available = 1
        """
    ).fetchall():
        text = source["extracted_text"]
        conn.execute(
            "INSERT INTO sources_fts(rowid, title, body, path) VALUES (?, ?, ?, ?)",
            (source["id"], source["title"], text, source["path"]),
        )
    return True


def sync_log_events(root: Path, conn: sqlite3.Connection) -> int:
    log_path = root / "wiki" / "log.md"
    if not log_path.exists():
        return 0
    text = read_text_preview(log_path)
    lines = text.splitlines()
    entries: list[dict[str, str]] = []
    for index, line in enumerate(lines):
        match = LOG_HEADING_RE.match(line)
        if not match:
            continue
        body_lines = []
        for body_line in lines[index + 1 :]:
            if LOG_HEADING_RE.match(body_line):
                break
            body_lines.append(body_line)
        body = "\n".join(body_lines)
        path_match = LOG_PATH_RE.search(body)
        occurrence = sum(
            1
            for entry in entries
            if entry["date"] == match.group("date")
            and entry["kind"] == match.group("kind").strip()
            and entry["summary"] == match.group("summary").strip()
        )
        entries.append(
            {
                "date": match.group("date"),
                "kind": match.group("kind").strip(),
                "summary": match.group("summary").strip(),
                "object_path": path_match.group(1) if path_match else "",
                "event_key": stable_event_key(match.group(0), body, occurrence),
                "body": body.strip(),
            }
        )

    count = 0
    for entry in entries:
        payload = (
            f"{entry['date']}T00:00:00Z",
            entry["kind"],
            entry["object_path"],
            entry["summary"],
            json.dumps({"source": "wiki/log.md", "body": entry["body"]}, ensure_ascii=False),
            entry["event_key"],
        )
        existing = conn.execute("SELECT id FROM events WHERE event_key = ?", (entry["event_key"],)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE events
                SET occurred_at = ?, kind = ?, object_path = ?, summary = ?, metadata_json = ?
                WHERE event_key = ?
                """,
                payload,
            )
        else:
            conn.execute(
                """
                INSERT INTO events(occurred_at, kind, object_path, summary, metadata_json, event_key)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
        count += 1
    current_keys = [entry["event_key"] for entry in entries]
    if current_keys:
        placeholders = ",".join("?" for _ in current_keys)
        conn.execute(
            f"DELETE FROM events WHERE event_key LIKE 'log:%' AND event_key NOT IN ({placeholders})",
            current_keys,
        )
    else:
        conn.execute("DELETE FROM events WHERE event_key LIKE 'log:%'")
    return count


def sync_task_records(root: Path, conn: sqlite3.Connection) -> int:
    from .tasks import list_tasks

    records = list_tasks(root)
    timestamp = now_iso()
    conn.execute("DELETE FROM task_records")
    for record in records:
        conn.execute(
            """
            INSERT INTO task_records(path, title, status, role_owner, created, objective, updated_at, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, '{}')
            """,
            (
                record.path,
                record.title,
                record.status,
                record.role_owner,
                record.created,
                record.objective,
                timestamp,
            ),
        )
    return len(records)


def stable_event_key(heading: str, body: str, occurrence: int) -> str:
    digest = hashlib.sha1(f"{heading}\n{body}\n{occurrence}".encode("utf-8")).hexdigest()
    return f"log:{digest}"


def rebuild_index(root: Path) -> RebuildStats:
    ensure_project(root)
    conn = connect(root)
    try:
        initialize_database(conn)
        sources = sync_sources(root, conn)
        sync_source_extracts(root, conn)
        pages = sync_pages(root, conn)
        links = rebuild_links(root, conn)
        sync_log_events(root, conn)
        sync_task_records(root, conn)
        fts_enabled = rebuild_fts(root, conn)
        conn.commit()
        return RebuildStats(sources=sources, pages=pages, links=links, fts_enabled=fts_enabled)
    finally:
        conn.close()


def search(root: Path, query: str, limit: int = 10) -> list[dict[str, Any]]:
    ensure_project(root)
    conn = connect(root)
    try:
        initialize_database(conn)
        return search_rows(conn, query, limit)
    finally:
        conn.close()


def list_events(root: Path, limit: int = 20) -> list[dict[str, Any]]:
    rebuild_index(root)
    conn = connect(root)
    try:
        return list_event_rows(conn, limit)
    finally:
        conn.close()


def enqueue_ingest_jobs(root: Path, paths: list[str], all_new: bool = False) -> dict[str, Any]:
    rebuild_index(root)
    conn = connect(root)
    try:
        sources = select_sources_for_ingest(root, conn, paths, all_new)
        queued: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        timestamp = now_iso()
        for source in sources:
            active = conn.execute(
                """
                SELECT id, status FROM ingest_jobs
                WHERE source_id = ? AND status IN ('queued', 'in_progress')
                ORDER BY id DESC LIMIT 1
                """,
                (source["id"],),
            ).fetchone()
            if active:
                skipped.append(
                    {
                        "source_path": source["path"],
                        "reason": f"active job already exists: {active['id']} ({active['status']})",
                    }
                )
                continue
            completed = conn.execute(
                """
                SELECT id FROM ingest_jobs
                WHERE source_id = ? AND source_sha256 = ? AND status = 'completed'
                ORDER BY id DESC LIMIT 1
                """,
                (source["id"], source["sha256"]),
            ).fetchone()
            if completed:
                skipped.append(
                    {
                        "source_path": source["path"],
                        "reason": f"source hash already completed by job {completed['id']}",
                    }
                )
                continue
            cursor = conn.execute(
                """
                INSERT INTO ingest_jobs(source_id, source_path, source_sha256, status, priority, queued_at)
                VALUES (?, ?, ?, 'queued', 5, ?)
                """,
                (source["id"], source["path"], source["sha256"], timestamp),
            )
            queued.append({"job_id": int(cursor.lastrowid), "source_path": source["path"], "status": "queued"})
        conn.commit()
        return {"queued": queued, "skipped": skipped}
    finally:
        conn.close()


def select_sources_for_ingest(
    root: Path, conn: sqlite3.Connection, paths: list[str], all_new: bool
) -> list[sqlite3.Row]:
    if paths:
        rows = []
        for raw_path in paths:
            rel = normalize_source_argument(root, raw_path)
            row = conn.execute(
                "SELECT id, path, sha256 FROM sources WHERE path = ? AND available = 1",
                (rel,),
            ).fetchone()
            if row is None:
                raise FileNotFoundError(f"Source is not registered or unavailable: {rel}")
            rows.append(row)
        return rows
    if all_new:
        return conn.execute(
            """
            SELECT s.id, s.path, s.sha256
            FROM sources s
            WHERE s.available = 1
              AND s.kind = 'file'
              AND NOT EXISTS (
                SELECT 1 FROM ingest_jobs j
                WHERE j.source_id = s.id
                  AND j.source_sha256 = s.sha256
                  AND j.status = 'completed'
              )
            ORDER BY s.path
            """
        ).fetchall()
    raise ValueError("Provide source paths or use --all-new.")


def normalize_source_argument(root: Path, raw_path: str) -> str:
    candidate = Path(raw_path)
    absolute = candidate if candidate.is_absolute() else root / candidate
    try:
        rel = absolute.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"Ingest source must be inside project root: {raw_path}") from exc
    if not rel.startswith("raw/sources/"):
        raise ValueError(f"Ingest source must live under raw/sources/: {rel}")
    return rel


def next_ingest_job(root: Path) -> dict[str, Any] | None:
    rebuild_index(root)
    conn = connect(root)
    try:
        job = conn.execute(
            """
            SELECT j.*, s.title, s.size_bytes, se.extracted_text, se.extractor, se.warnings_json
            FROM ingest_jobs j
            JOIN sources s ON s.id = j.source_id
            LEFT JOIN source_extracts se ON se.source_id = s.id
            WHERE j.status = 'in_progress'
            ORDER BY j.started_at, j.id
            LIMIT 1
            """
        ).fetchone()
        if job is None:
            queued = conn.execute(
                """
                SELECT id FROM ingest_jobs
                WHERE status = 'queued'
                ORDER BY priority ASC, queued_at ASC, id ASC
                LIMIT 1
                """
            ).fetchone()
            if queued is None:
                return None
            timestamp = now_iso()
            conn.execute(
                """
                UPDATE ingest_jobs
                SET status = 'in_progress',
                    started_at = COALESCE(started_at, ?),
                    attempts = attempts + 1
                WHERE id = ?
                """,
                (timestamp, queued["id"]),
            )
            conn.commit()
            job = conn.execute(
                """
                SELECT j.*, s.title, s.size_bytes, se.extracted_text, se.extractor, se.warnings_json
                FROM ingest_jobs j
                JOIN sources s ON s.id = j.source_id
                LEFT JOIN source_extracts se ON se.source_id = s.id
                WHERE j.id = ?
                """,
                (queued["id"],),
            ).fetchone()
        return build_ingest_package(conn, job)
    finally:
        conn.close()


def build_ingest_package(conn: sqlite3.Connection, job: sqlite3.Row) -> dict[str, Any]:
    extracted_text = job["extracted_text"] or ""
    try:
        warnings = json.loads(job["warnings_json"] or "[]")
    except json.JSONDecodeError:
        warnings = [job["warnings_json"]]
    return {
        "job_id": job["id"],
        "status": job["status"],
        "source": {
            "path": job["source_path"],
            "title": job["title"],
            "sha256": job["source_sha256"],
            "size_bytes": job["size_bytes"],
        },
        "extraction": {
            "extractor": job["extractor"] or "none",
            "warnings": warnings,
            "text_preview": extracted_text[:12_000],
            "truncated": len(extracted_text) > 12_000,
        },
        "relevant_pages": related_pages_for_source(conn, job["source_id"], job["title"], limit=8),
        "required_output_contract": [
            "Read purpose.md, schema.md, wiki/index.md, and recent wiki/log.md entries before editing.",
            "Create or update one source summary under wiki/sources/.",
            "Update relevant entity, concept, synthesis, comparison, or query pages.",
            "Update wiki/index.md and append wiki/log.md.",
            "Run python tools/llm_wiki.py rebuild and python tools/llm_wiki.py lint after edits.",
            "Complete the job with llm-wiki ingest complete JOB_ID --pages ... --notes \"...\".",
        ],
    }


def related_pages_for_source(
    conn: sqlite3.Connection, source_id: int, source_title: str, limit: int
) -> list[dict[str, Any]]:
    related: dict[str, dict[str, Any]] = {}
    for row in conn.execute(
        """
        SELECT p.path, p.title, p.page_type, p.summary, 'cites-source' AS reason
        FROM page_sources ps
        JOIN pages p ON p.id = ps.page_id
        WHERE ps.source_id = ?
        ORDER BY p.path
        LIMIT ?
        """,
        (source_id, limit),
    ).fetchall():
        related[row["path"]] = dict(row)

    if len(related) < limit and source_title.strip():
        match = fts_query(source_title)
        try:
            rows = conn.execute(
                """
                SELECT p.path, p.title, p.page_type, p.summary, 'title-search' AS reason
                FROM pages_fts
                JOIN pages p ON p.id = pages_fts.rowid
                WHERE pages_fts MATCH ?
                ORDER BY bm25(pages_fts)
                LIMIT ?
                """,
                (match, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = conn.execute(
                """
                SELECT path, title, page_type, summary, 'title-search' AS reason
                FROM pages
                WHERE title LIKE ? OR summary LIKE ?
                LIMIT ?
                """,
                (f"%{source_title}%", f"%{source_title}%", limit),
            ).fetchall()
        for row in rows:
            related.setdefault(row["path"], dict(row))
            if len(related) >= limit:
                break
    return list(related.values())[:limit]


def complete_ingest_job(root: Path, job_id: int, pages: list[str], notes: str) -> dict[str, Any]:
    conn = connect(root)
    try:
        job = conn.execute("SELECT id, status, source_path FROM ingest_jobs WHERE id = ?", (job_id,)).fetchone()
        if job is None:
            raise ValueError(f"Unknown ingest job: {job_id}")
        if job["status"] not in {"queued", "in_progress", "failed"}:
            raise ValueError(f"Cannot complete job {job_id} from status {job['status']}")
        timestamp = now_iso()
        conn.execute(
            """
            UPDATE ingest_jobs
            SET status = 'completed',
                completed_at = ?,
                failed_at = NULL,
                result_pages_json = ?,
                notes = ?,
                error = ''
            WHERE id = ?
            """,
            (timestamp, json.dumps(pages, ensure_ascii=False), notes, job_id),
        )
        conn.commit()
    finally:
        conn.close()
    append_log(root, "ingest", f"Completed ingest job {job_id}", path=job["source_path"])
    rebuild_index(root)
    return {"job_id": job_id, "status": "completed", "pages": pages, "notes": notes}


def fail_ingest_job(root: Path, job_id: int, reason: str) -> dict[str, Any]:
    conn = connect(root)
    try:
        job = conn.execute("SELECT id, status, source_path FROM ingest_jobs WHERE id = ?", (job_id,)).fetchone()
        if job is None:
            raise ValueError(f"Unknown ingest job: {job_id}")
        if job["status"] == "completed":
            raise ValueError(f"Cannot fail completed job {job_id}")
        timestamp = now_iso()
        conn.execute(
            """
            UPDATE ingest_jobs
            SET status = 'failed',
                failed_at = ?,
                error = ?
            WHERE id = ?
            """,
            (timestamp, reason, job_id),
        )
        conn.commit()
    finally:
        conn.close()
    append_log(root, "ingest", f"Failed ingest job {job_id}", path=job["source_path"])
    rebuild_index(root)
    return {"job_id": job_id, "status": "failed", "reason": reason}


def collect_lint_issues(root: Path) -> list[LintIssue]:
    stats = rebuild_index(root)
    _ = stats
    issues: list[LintIssue] = []
    conn = connect(root)
    try:
        rows = conn.execute("SELECT path, page_type FROM pages ORDER BY path").fetchall()
        for row in rows:
            path = root / row["path"]
            text = read_text_preview(path)
            metadata = parse_frontmatter(text)
            frontmatter = parse_frontmatter_result(text)
            if row["page_type"] in {"index", "log"}:
                continue
            for warning in frontmatter.warnings:
                issues.append(LintIssue("warning", row["path"], warning))
            required = ["title", "type", "status", "confidence", "sources", "summary"]
            for key in required:
                if key not in metadata:
                    issues.append(LintIssue("warning", row["path"], f"Missing frontmatter field: {key}"))

        for row in conn.execute(
            """
            SELECT p.path, l.to_title, l.line
            FROM links l
            JOIN pages p ON p.id = l.from_page_id
            WHERE l.to_page_id IS NULL
            ORDER BY p.path, l.line
            """
        ).fetchall():
            issues.append(
                LintIssue("warning", row["path"], f"Dead wikilink [[{row['to_title']}]] at line {row['line']}")
            )

        for row in conn.execute(
            """
            SELECT p.path, p.page_type
            FROM pages p
            LEFT JOIN links outgoing ON outgoing.from_page_id = p.id
            LEFT JOIN links incoming ON incoming.to_page_id = p.id
            WHERE p.page_type NOT IN ('index', 'log', 'overview')
            GROUP BY p.id
            HAVING COUNT(DISTINCT outgoing.id) = 0 AND COUNT(DISTINCT incoming.id) = 0
            ORDER BY p.path
            """
        ).fetchall():
            issues.append(LintIssue("info", row["path"], "Orphan page has no resolved incoming or outgoing links"))

        for row in conn.execute(
            """
            SELECT DISTINCT p.path AS page_path, s.path AS source_path
            FROM page_sources ps
            JOIN pages p ON p.id = ps.page_id
            JOIN sources s ON s.id = ps.source_id
            WHERE s.available = 0
            ORDER BY p.path
            """
        ).fetchall():
            issues.append(
                LintIssue("warning", row["page_path"], f"Referenced source is missing: {row['source_path']}")
            )

        for row in conn.execute(
            """
            SELECT s.path, se.extractor, se.warnings_json
            FROM source_extracts se
            JOIN sources s ON s.id = se.source_id
            WHERE s.available = 1 AND se.warnings_json <> '[]'
            ORDER BY s.path
            """
        ).fetchall():
            try:
                warnings = json.loads(row["warnings_json"])
            except json.JSONDecodeError:
                warnings = [row["warnings_json"]]
            for warning in warnings:
                severity = "warning" if str(row["extractor"]).startswith("missing-") else "info"
                issues.append(LintIssue(severity, row["path"], str(warning)))
        from .harness import validate_harness

        issues.extend(validate_harness(root))
        return issues
    finally:
        conn.close()


def add_source(root: Path, source: Path) -> Path:
    ensure_project(root)
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(source)
    target_dir = root / "raw" / "sources"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / source.name
    if target.exists():
        stem = target.stem
        suffix = target.suffix
        index = 2
        while target.exists():
            target = target_dir / f"{stem}-{index}{suffix}"
            index += 1
    shutil.copy2(source, target)
    append_log(root, "ingest", f"Added source {target.name}", path=relative_posix(target, root))
    rebuild_index(root)
    return target


def create_page(root: Path, page_type: str, title: str, summary: str = "") -> Path:
    ensure_project(root)
    if page_type not in PAGE_DIR_BY_TYPE:
        raise ValueError(f"Unsupported page type: {page_type}")
    folder = root / PAGE_DIR_BY_TYPE[page_type]
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{slugify(title)}.md"
    if target.exists():
        raise FileExistsError(target)
    date = today()
    rendered_summary = summary or "Draft page."
    content = f"""---
title: {title}
type: {page_type}
status: draft
confidence: medium
sources: []
tags: []
created: {date}
updated: {date}
summary: {rendered_summary}
---

# {title}

## Summary

{rendered_summary}

## Evidence

No source-backed evidence added yet.

## Links

Add relevant wikilinks here.

## Open Questions

- What needs source-backed clarification?
"""
    target.write_text(content, encoding="utf-8")
    append_log(root, "maintenance", f"Created {page_type} page {title}", path=relative_posix(target, root))
    rebuild_index(root)
    return target


def append_log(root: Path, kind: str, summary: str, path: str = "") -> None:
    log_path = root / "wiki" / "log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# Wiki Log\n\n", encoding="utf-8")
    date = today()
    details = f"\n\n- Path: `{path}`\n" if path else "\n"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n## [{date}] {kind} | {summary}{details}")
