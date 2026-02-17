## Crate

### 開発/PR運用の互換ルール

- Crate環境の開発実装では `crate-dev-ops` を併用する。
- Crate環境のPR作成/更新/レビュー反復/マージでは `crate-pr-ops` を併用する。

### Continuity

- セッション開始/再開時に `get_session_continuity` を実行する。
- 調査/計画/Web検索を開始する都度 `get_session_continuity` を再実行する。
- 目標/制約/重要判断が変わったら `upsert_session_continuity` を実行する。

### Task

- 複数ステップ作業に着手する前に `list_project_tasks` を実行する。
- 既存taskで表現できない場合のみ `create_project_task` を作成する。
- 着手時: `update_project_task(status=in_progress)`
- 完了時: `update_project_task(status=close)`
- 中止時: `update_project_task(status=canceled)`

### Snapshot

- 仕様確定 / 主要実装完了 / テスト完了 / 成果公開 / 方針転換で `create_snapshot` を実行する。
- ユーザーが `$create-snapshot` を入力した場合は `ingest_turn` を実行する。

### Context

- 設計理由/変更背景/引き継ぎ要約の説明時は `create_context` を実行する。
- 実装詳細のみで回答可能な質問では `create_context` を省略してよい。
