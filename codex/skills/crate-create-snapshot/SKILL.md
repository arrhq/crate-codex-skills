---
name: crate-create-snapshot
description: Crate Snapshot を節目で自動送信する運用スキル。`$crate-create-snapshot` 明示時は ingest_turn、明示なしは5つのチェックポイントのみ create_snapshot を実行する。accepted/skipped は無言、失敗時のみ1行通知する。
---

# Create Snapshot

## Core Policy

- 通常は自動で保存し、`$crate-create-snapshot` は補助的に使う。
- LLM応答経路はブロックしない。
- チャット表示は最小化し、失敗時のみ通知する。
- 保存品質は「要約の綺麗さ」より「後で検索再利用できる根拠」を優先する。
- チェックポイントで snapshot を送る前に、必要なら `upsert_session_continuity` で最新状態を反映する。
- PR/Issueは任意。GitHubなしでも検索再利用できるよう、`context_label` / user request / URL を優先する。
- チェックポイントでは必ず `checkpoint gate`（送信 + 到達確認）を完了する。完了できなければ次工程へ進まない。
- outbox 再送時に `crate-snapshot-outbox.ndjson.resolved-*.bak` を作る場合は一時退避用途に限定し、解消確認後に削除して残置しない。
- outbox へ pending を書く前に、同一 `session_id + checkpoint_label` の既存行を確認し、重複追記しない（upsert 扱い）。
- `checkpoint gate` が失敗した場合、outbox 退避前に `reindex_snapshots(limit=50)` を1回実行して再確認する。

## Trigger

1. 入力に `$crate-create-snapshot` 行があるときは `ingest_turn` を実行する。
2. `$crate-create-snapshot` がないときは次の5チェックポイントでのみ `create_snapshot` を実行する。
- 仕様/設計確定
- 主要実装完了
- テスト/検証完了
- 成果公開（PR作成 / release note / tag付与 など）
- 方針転換
3. それ以外では送信しない。

## Checkpoint Gate（必須）

チェックポイントで `create_snapshot` を送るときは、次を必ず実行する。

1. `checkpoint_label` を決める（必須）
- 形式: `checkpoint:<note>:<work_slug>`
- 例: `checkpoint:tests_passed:search-local-first`

2. `conversation_slice` に最低1つの `context_label` として `checkpoint_label` を含める
- 推奨: 追加で `task:...` / `spec:...` も入れる

3. `create_snapshot` を実行する
- note は checkpoint に対応する値を使う（`spec_finalized` / `major_implementation_completed` / `tests_passed` / `deliverable_shared` / `pivot` など）

4. 直後に `create_context` で到達確認する
- クエリ例: `checkpoint:tests_passed:search-local-first の decision と reason を確認`
- Top3 のどこかで `checkpoint_label` が根拠として確認できれば pass

5. fail の扱い
- 1回だけ再送（`scope=recent` + retry note）
- それでも fail なら `reindex_snapshots(limit=50)` 後に `checkpoint_label` 単体クエリでもう一度だけ確認する
- なお fail なら pending payload を `~/.codex/state/crate-snapshot-outbox.ndjson` に退避して1行通知（同一 checkpoint は1行に集約）
- pending は次ターン開始時に再送を試みる

## Visibility

- `snapshot accepted` は無言。
- `snapshot skipped ... reason=no_new_messages` も無言。
- `snapshot ingest failed` のときだけ1行通知し、1回だけ再試行する。
- ユーザーが状態確認したときだけ結果を返す。

## Minimum Contract

- 必須: `session_id`, `conversation_slice`
- 条件付き必須: `project_id`（MCP URLに未指定の場合）
- 任意: `note`, `pr_number`, `scope`, `branch`, `system_prompt`, `tools`
- `session_id` は同一作業で固定する。
- `scope` は既定 `since_last_snap`。意図的な復旧時のみ `recent` を使う。
- `checkpoint_label` はツール引数ではなく、`conversation_slice` 側の `context_label` として渡す。

## conversation_slice Quality

以下の5要素を含める。

- 決定事項
- 決定理由
- 前提/制約
- 方向転換（なければ `なし`）
- 未解決事項/次アクション

`conversation_slice` の本文は日本語で記述する。  
（`decision` / `reason` などのキー名や `context_label` の識別子は英語のままでよい）

加えて、以下を最低1つ含める。

- context_label（`task:...` / `spec:...` / `topic:...` / `decision:...` など）
- user request（依頼文の要約または原文短縮）
- URL（ユーザーが渡したリンク、参照した仕様URL）

PR/Issue anchor（`PR #...` / `Issue #...` / `Closes #...` など）は存在する場合のみ補助的に含める。
PR/Issue番号を記載する場合は、可能な限り対応するGitHub URLも併記する。

運用系チェックポイント（`tests_passed` など）の場合は、次を必ず含める。

- 何を検証したか
- 結果がどの判断を確定/否定したか

雑談のみ、ログのみ、重複断片の再送は避ける。

## References

- Trigger: `references/trigger-policy.md`
- Fields: `references/field-contract.md`
- Slice template: `references/conversation-slice-template.md`
- Result handling: `references/result-handling.md`
- Checkpoint gate: `references/checkpoint-gate.md`
