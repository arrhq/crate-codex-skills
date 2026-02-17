#!/usr/bin/env python3
"""Replay Crate snapshot outbox entries via MCP HTTP and compact the outbox.

- Reads ~/.codex/state/crate-snapshot-outbox.ndjson
- Normalizes legacy record shapes
- De-duplicates by (session_id, checkpoint_label) when possible
- Calls `create_snapshot` for replayable entries
- Removes successfully replayed entries from outbox
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CHECKPOINT_RE = re.compile(r"checkpoint:[A-Za-z0-9_-]+:[A-Za-z0-9:_-]+")


@dataclass
class Entry:
    line_no: int
    raw_line: str
    raw_obj: dict[str, Any]
    payload: dict[str, Any]
    checkpoint_label: str | None
    sort_time: dt.datetime
    replayable: bool
    reason: str | None


class McpHttpClient:
    def __init__(self, url: str, ingest_token: str, timeout_sec: int = 30) -> None:
        self.url = url
        self.ingest_token = ingest_token
        self.timeout_sec = timeout_sec
        self._request_id = 1

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        rid = self._request_id
        self._request_id += 1
        body = {
            "jsonrpc": "2.0",
            "id": rid,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        req = urllib.request.Request(
            self.url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "content-type": "application/json",
                "accept": "application/json, text/event-stream",
                "x-crate-ingest-token": self.ingest_token,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise RuntimeError(f"HTTP {exc.code}: {detail.strip()}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Network error: {exc.reason}") from exc

        event = self._parse_sse(raw)
        if not isinstance(event, dict):
            raise RuntimeError("Invalid MCP response (not JSON object)")

        if "error" in event:
            err = event["error"]
            code = err.get("code") if isinstance(err, dict) else None
            msg = err.get("message") if isinstance(err, dict) else str(err)
            raise RuntimeError(f"MCP error code={code} message={msg}")

        result = event.get("result", {})
        content = result.get("content", []) if isinstance(result, dict) else []
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text")
                    if isinstance(text, str) and text.strip():
                        return text.strip()
        return "ok"

    @staticmethod
    def _parse_sse(raw: str) -> dict[str, Any] | None:
        last_obj: dict[str, Any] | None = None
        for line in raw.splitlines():
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if not payload:
                continue
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                last_obj = obj
        return last_obj


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay crate snapshot outbox")
    parser.add_argument(
        "--outbox",
        default="~/.codex/state/crate-snapshot-outbox.ndjson",
        help="Outbox NDJSON path",
    )
    parser.add_argument(
        "--config",
        default="~/.codex/config.toml",
        help="Codex config TOML path",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max entries to replay (0 means all deduped entries)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not send or rewrite")
    return parser.parse_args()


def parse_iso_or_min(value: Any) -> dt.datetime:
    if not isinstance(value, str):
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    text = value.strip()
    if not text or text.startswith("$("):
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def extract_checkpoint_label(base: dict[str, Any], conversation_slice: str | None) -> str | None:
    for key in ("checkpoint_label", "context_label"):
        val = base.get(key)
        if isinstance(val, str):
            m = CHECKPOINT_RE.search(val)
            if m:
                return m.group(0)

    if isinstance(conversation_slice, str):
        for marker in ("context_label:", "context_label="):
            idx = conversation_slice.find(marker)
            if idx >= 0:
                tail = conversation_slice[idx + len(marker) :]
                m = CHECKPOINT_RE.search(tail)
                if m:
                    return m.group(0)
        m = CHECKPOINT_RE.search(conversation_slice)
        if m:
            return m.group(0)

    return None


def normalize_raw_entry(line_no: int, raw_line: str, raw_obj: dict[str, Any]) -> Entry:
    if raw_obj.get("type") == "create_snapshot" and isinstance(raw_obj.get("payload"), dict):
        base = dict(raw_obj["payload"])
    else:
        base = dict(raw_obj)

    payload: dict[str, Any] = {}
    for key in (
        "project_id",
        "session_id",
        "github_repo_full_name",
        "repository",
        "branch",
        "pr_number",
        "note",
        "scope",
        "conversation_slice",
    ):
        if key in base:
            payload[key] = base[key]

    if "scope" not in payload or payload["scope"] not in ("recent", "since_last_snap"):
        payload["scope"] = "recent"

    if "repository" not in payload and isinstance(payload.get("github_repo_full_name"), str):
        payload["repository"] = payload["github_repo_full_name"]
    if "github_repo_full_name" not in payload and isinstance(payload.get("repository"), str):
        payload["github_repo_full_name"] = payload["repository"]

    conversation_slice = payload.get("conversation_slice")
    checkpoint_label = extract_checkpoint_label(base, conversation_slice if isinstance(conversation_slice, str) else None)

    sort_time = max(
        parse_iso_or_min(raw_obj.get("recorded_at")),
        parse_iso_or_min(raw_obj.get("created_at")),
        parse_iso_or_min(raw_obj.get("queued_at")),
        parse_iso_or_min(base.get("recorded_at") if isinstance(base, dict) else None),
        parse_iso_or_min(base.get("created_at") if isinstance(base, dict) else None),
        parse_iso_or_min(base.get("queued_at") if isinstance(base, dict) else None),
    )

    if not isinstance(payload.get("session_id"), str) or not payload["session_id"].strip():
        return Entry(line_no, raw_line, raw_obj, payload, checkpoint_label, sort_time, False, "missing_session_id")
    if not isinstance(payload.get("conversation_slice"), str) or not payload["conversation_slice"].strip():
        return Entry(
            line_no,
            raw_line,
            raw_obj,
            payload,
            checkpoint_label,
            sort_time,
            False,
            "missing_conversation_slice",
        )

    return Entry(line_no, raw_line, raw_obj, payload, checkpoint_label, sort_time, True, None)


def dedupe_key(entry: Entry) -> str:
    sid = str(entry.payload.get("session_id", ""))
    if entry.checkpoint_label:
        return f"{sid}::{entry.checkpoint_label}"
    note = str(entry.payload.get("note", ""))
    cs = str(entry.payload.get("conversation_slice", ""))
    digest = hashlib.sha1(cs.encode("utf-8")).hexdigest()[:12]
    return f"{sid}::note:{note}::cs:{digest}"


def load_config(config_path: Path) -> tuple[str, str]:
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    server = data.get("mcp_servers", {}).get("crate-crate", {})
    url = server.get("url")
    token = server.get("http_headers", {}).get("x-crate-ingest-token")
    if not isinstance(url, str) or not url:
        raise RuntimeError("crate-crate url が config.toml にありません")
    if not isinstance(token, str) or not token:
        raise RuntimeError("x-crate-ingest-token が config.toml にありません")
    return url, token


def main() -> int:
    args = parse_args()
    outbox_path = Path(args.outbox).expanduser()
    config_path = Path(args.config).expanduser()

    if not outbox_path.exists():
        print(f"outbox not found: {outbox_path}")
        return 0

    try:
        url, token = load_config(config_path)
    except Exception as exc:  # noqa: BLE001
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    entries: list[Entry] = []
    with outbox_path.open("r", encoding="utf-8") as fh:
        for idx, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                entries.append(
                    Entry(
                        line_no=idx,
                        raw_line=line,
                        raw_obj={"raw": line},
                        payload={},
                        checkpoint_label=None,
                        sort_time=dt.datetime.min.replace(tzinfo=dt.timezone.utc),
                        replayable=False,
                        reason="invalid_json",
                    )
                )
                continue
            if not isinstance(obj, dict):
                entries.append(
                    Entry(
                        line_no=idx,
                        raw_line=line,
                        raw_obj={"raw": line},
                        payload={},
                        checkpoint_label=None,
                        sort_time=dt.datetime.min.replace(tzinfo=dt.timezone.utc),
                        replayable=False,
                        reason="invalid_record",
                    )
                )
                continue
            entries.append(normalize_raw_entry(idx, line, obj))

    if not entries:
        print("outbox is empty")
        return 0

    deduped: dict[str, Entry] = {}
    for entry in entries:
        key = dedupe_key(entry)
        current = deduped.get(key)
        if current is None:
            deduped[key] = entry
            continue
        if entry.sort_time > current.sort_time or (
            entry.sort_time == current.sort_time and entry.line_no > current.line_no
        ):
            deduped[key] = entry

    queue = sorted(deduped.values(), key=lambda e: (e.sort_time, e.line_no))
    if args.limit and args.limit > 0:
        queue = queue[: args.limit]

    replay_ok = 0
    replay_fail = 0
    skipped = 0

    client = McpHttpClient(url=url, ingest_token=token)
    keep_lines: list[str] = []

    for entry in queue:
        if not entry.replayable:
            skipped += 1
            keep_lines.append(entry.raw_line)
            print(f"skip line={entry.line_no} reason={entry.reason}")
            continue

        if args.dry_run:
            replay_ok += 1
            print(
                f"dry-run replay line={entry.line_no} session={entry.payload.get('session_id')} "
                f"checkpoint={entry.checkpoint_label or '-'}"
            )
            continue

        try:
            result_text = client.call_tool("create_snapshot", entry.payload)
            replay_ok += 1
            print(
                f"ok line={entry.line_no} session={entry.payload.get('session_id')} "
                f"checkpoint={entry.checkpoint_label or '-'} result={result_text}"
            )
        except Exception as exc:  # noqa: BLE001
            replay_fail += 1
            keep_lines.append(entry.raw_line)
            print(
                f"fail line={entry.line_no} session={entry.payload.get('session_id')} "
                f"checkpoint={entry.checkpoint_label or '-'} error={exc}",
                file=sys.stderr,
            )

    if args.limit and args.limit > 0 and len(queue) < len(deduped):
        selected = {id(e) for e in queue}
        for entry in sorted(deduped.values(), key=lambda e: e.line_no):
            if id(entry) in selected:
                continue
            keep_lines.append(entry.raw_line)

    if args.dry_run:
        print("dry-run mode: outbox is unchanged")
    else:
        outbox_text = ""
        if keep_lines:
            outbox_text = "\n".join(keep_lines) + "\n"
        outbox_path.write_text(outbox_text, encoding="utf-8")

    remaining = len(keep_lines) if not args.dry_run else len(entries)
    print(
        "summary "
        f"total={len(entries)} deduped={len(deduped)} processed={len(queue)} "
        f"ok={replay_ok} fail={replay_fail} skipped={skipped} remaining={remaining}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
