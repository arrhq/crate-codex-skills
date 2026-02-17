# Checkpoint Gate

`create_snapshot` の送信漏れを防ぐため、checkpoint では必ずこの gate を通す。

## 目的

- 送信した snapshot が「検索再利用できる状態」になったことをその場で確認する。
- 確認できないまま次工程へ進まない。

## 必須入力

- `session_id`
- `note`
- `work_slug`（GitHub非依存の識別子）
- `checkpoint_label = checkpoint:<note>:<work_slug>`

## 手順

1. `conversation_slice` に `checkpoint_label` を含める
2. `create_snapshot` を送信する
3. `create_context` で `checkpoint_label` を含む query を実行する
4. Top3 で `checkpoint_label` を確認できれば pass

## Pass条件

- Top3 のどれかに `checkpoint_label` が根拠として現れる
  - `results[].evidence.context_labels` に一致
  - または summary/notes から明示的に追える

## Fail時の扱い

1. `scope=recent` + retry note で1回だけ再送
2. 再送後も fail の場合:
- `reindex_snapshots(project_id, limit=50)` を1回実行
- `create_context` を `checkpoint_label` 単体クエリで再確認
3. それでも fail の場合:
- `~/.codex/state/crate-snapshot-outbox.ndjson` に pending を記録（同一 `session_id + checkpoint_label` は上書き）
- 通常チャットには1行だけ通知

## Outbox JSONL Schema

```json
{
  "created_at": "2026-02-16T03:35:00Z",
  "reason": "checkpoint_gate_failed",
  "project_id": "<uuid-or-null>",
  "session_id": "<session-id>",
  "note": "tests_passed",
  "checkpoint_label": "checkpoint:tests_passed:search-local-first",
  "payload": {
    "session_id": "...",
    "note": "...",
    "scope": "recent",
    "conversation_slice": []
  }
}
```

## Replay方針

- 次ターン開始時に outbox を先に確認し、pending があれば古い順に再送する。
- 再送前に outbox を `session_id + checkpoint_label` 単位で重複排除する。
- 再送成功時は該当行を outbox から削除する。

## Outbox後片付け

- 一括処理前に一時バックアップを作るのは許可。
- 一時バックアップ名は `crate-snapshot-outbox.ndjson.resolved-<timestamp>.bak` を推奨。
- 全pending解消を確認したら `resolved-*.bak` は削除し、恒久保存しない。
- outbox が非空ならバックアップを残してよいが、次の再送ターンで再利用/削除を判断する。
