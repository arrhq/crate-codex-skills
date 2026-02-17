# Field Contract

## Connection

`create_snapshot` と同じ MCP 接続を使う。

`https://<crate-domain>/api/mcp?project_id=<project_uuid>&ingest_token=<project_ingest_token>`

## Tool Arguments

### `create_context`

- 必須:
  - `query: string`
- 条件付き必須:
  - `project_id: string`（URL query に無い場合のみ）

### `get_session_continuity`

- 必須:
  - `session_id: string`
- 条件付き必須:
  - `project_id: string`（URL query に無い場合のみ）

## Query品質

高シグナルqueryは次のうち最低1つを含める。

- 対象: 現在アーキテクチャ / 特定 task-spec-topic / 機能
- 軸: 決定事項 / 決定理由 / 前提 / 方向転換 / リスク
- 期間ヒント: recent / current / before PR merge
- 根拠アンカー: `task:...` / `spec:...` / URL / user request
- 任意GitHubアンカー: `PR #...` / `Issue #...`

checkpoint gate 検証query:

- `checkpoint:<note>:<work_slug>` を必ず含める
- 例: `checkpoint:tests_passed:search-local-first の決定事項と決定理由を確認`

例:

- `現在の設計判断と前提を要約して`
- `task:search-eval-v2 の背景と制約を教えて`
- `最近の方向転換と未解決事項は？`
- `Issue #451 と PR #456 の判断理由を教えて（GitHub運用時）`

## Returned Fields

- `reconstruction_prompt`: 再構成用プロンプト
- `snapshot_summaries`: 上位snapshotの圧縮テキスト
- `results`: 上位3件のランキング結果（score付き）
- `results[].evidence`: context_label / URL / user_request / （任意PR/Issue）アンカー
- `results[].evidence_anchor_adjustment`: アンカー一致による加点
- checkpoint検証では `results[].evidence.context_labels` の一致有無で pass/fail 判定する
