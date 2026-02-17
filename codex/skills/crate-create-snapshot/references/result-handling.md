# Result Handling

## 受理時

メッセージ例:

- `snapshot accepted: ...`
- `snapshot accepted: ... fallback=cursor_mismatch`

アクション:

1. 成功として扱う。
2. 通常チャットには表示しない。
3. 意図的に切り替えない限り同一 `session_id` を維持する。
4. checkpoint 送信なら直後に checkpoint gate（`create_context`）を実行する。
5. outbox 再送由来の accepted なら、処理済み行を outbox から削除する。

## スキップ時

メッセージ例:

- `snapshot skipped ... reason=no_new_messages`

アクション:

1. 正常系として扱う。
2. 通常チャットには表示しない。
3. checkpoint gate の場合は `scope=recent` で1回だけ再試行。
4. 再試行でも skipped なら outbox に pending を記録する。

## 失敗時

メッセージ例:

- `snapshot ingest failed: status=...`

アクション:

1. auth / token / project_id / session_id を確認する。
2. ユーザー向けに1行通知する。
3. `scope=recent` と短い retry note で1回再試行する。
4. なお失敗なら `~/.codex/state/crate-snapshot-outbox.ndjson` に pending を追記する。
5. それ以上の再試行は止め、運用ログ確認へエスカレーションする。

補足:
- outbox 追記前に `reindex_snapshots(limit=50)` を1回実行し、`checkpoint_label` 単体クエリで再確認する。
- outbox には同一 `session_id + checkpoint_label` を複数行残さない（追記ではなく上書き）。

## Outbox再送後の後片付け

1. 再送・編集の安全確保のための一時 `resolved-*.bak` は許可。
2. 再送開始前に outbox を重複排除する（キー: `session_id + checkpoint_label`）。
3. 再送完了後、outbox 行数が `0` なら `crate-snapshot-outbox.ndjson.resolved-*.bak` を削除する。
4. 解消済みバックアップを恒久的に残さない。
