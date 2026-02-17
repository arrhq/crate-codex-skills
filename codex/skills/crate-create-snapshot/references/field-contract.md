# Field Contract

## Connection

推奨MCP URL:

`https://<crate-domain>/api/mcp?project_id=<project_uuid>&ingest_token=<project_ingest_token>`

- `project_id`: project UUID
- `ingest_token`: `snapshot:write` 権限付きトークン

URLに `project_id` が含まれる場合、tool引数の `project_id` は省略可。

## Tool Arguments

### `create_snapshot`

- 必須:
  - `session_id: string`（作業単位で固定）
  - `conversation_slice: any`
- 条件付き必須:
  - `project_id: string`（URL query に無い場合のみ）
- 任意:
  - `note: string`
  - `pr_number: int > 0`
  - `scope: since_last_snap | recent`
  - `branch: string`
  - `system_prompt: string`
  - `tools: any`

### `ingest_turn`

- 必須:
  - `message: string`
  - `session_id: string`
- 任意:
  - `conversation_slice: any`
  - `create_snapshot` と同じ任意項目

`conversation_slice` を省略した場合、server は `message` から最小sliceを構築する。

## Value Rules

### `scope`

- 既定: `since_last_snap`
- `recent` を使う条件:
  - 意図的に新規セッションを開始する
  - 短いローリングウィンドウ送信を設計している

サーバー挙動:

- `conversation_slice.length < cursor` の場合、server は `recent` fallback を適用
- 差分が無い場合、`snapshot skipped ... reason=no_new_messages` を返す

### `note`

フィルタ向けに短いcheckpointラベルを使う:

- `spec_finalized`
- `major_implementation_completed`
- `tests_passed`
- `deliverable_shared`
- `release_note_drafted`
- `tag_cut`
- `pr_opened`
- `pr_ready_for_review`
- `pr_merged`
- `pivot`

### `checkpoint_label`（推奨、checkpoint gateでは必須）

`checkpoint_label` は `create_snapshot` 引数ではなく、`conversation_slice` 内の evidence 文字列として含める。

- 形式: `checkpoint:<note>:<work_slug>`
- 例:
  - `checkpoint:spec_finalized:memory-policy-v3`
  - `checkpoint:tests_passed:search-local-first`
  - `checkpoint:deliverable_shared:crate-memory-docs`

補足:

- `tests_completed` / `lint_completed` など `*_completed` は server 側で `*_passed` に正規化される。
- `note` は分類ヒントであり単体では不十分。`conversation_slice` 側に根拠（`context_label` / user request / URL）を入れる。
- PR/Issue は存在する場合のみ補助アンカーとして含める。
- checkpoint gate fail 時の pending 退避先: `~/.codex/state/crate-snapshot-outbox.ndjson`
