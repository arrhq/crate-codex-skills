---
name: crate-task-ops
description: Crate MCP の project task（list/create/update/delete）を使って、明示依頼と自律運用の両方で実行対象を管理するための共通スキル。
---

# Task Ops

Crate task を「実行対象の管理」に限定して扱うスキル。
Snapshot/Continuity との棲み分けを維持しながら、必要時に task を作成・更新する。

## 0. 基本方針

- まず `list_project_tasks` で着手候補の task（主に `open` / `in_progress`）を確認する。
- 既存taskで表現できない複数ステップ作業だけ `create_project_task` する。
- task は粗めの粒度を維持し、細かく分割しすぎない。
- 作業着手時は対象taskを `status=in_progress` に更新する。
- 作業完了時は対象taskを `status=close` に更新する。
- 実施しないと決めたtaskは `status=canceled` に更新する（誤作成のみ `delete_project_task`）。
- task の `title` / `description` は日本語で記述する（`status` などの列挙値はAPI仕様どおりに扱う）。
- `title` / `description` に PR/Issue 番号を記載する場合は、可能な限りGitHub URLも併記する。

## 1. 明示依頼時の運用

ユーザーが task 操作を依頼したら、対応するツールを実行する。

- 作成依頼: `create_project_task`
- 一覧確認: `list_project_tasks`
- 状態更新: `update_project_task`
- 削除依頼: `delete_project_task`

推奨の依頼フォーマット:

- `Crateにtask追加: title=..., description=...`
- `task一覧を見せて（status=in_progress）`
- `task <task_id> を in_progress に更新して`
- `task <task_id> を close に更新して`
- `task <task_id> を canceled に更新して`
- `task <task_id> を削除して`

## 2. 自律運用時の判断

- 実装・調査など複数ステップ作業に着手する前に `list_project_tasks` を実行する。
- 該当taskがなければ最小集合で `create_project_task` する。
- 既存taskでカバーできるなら新規作成しない。

## 3. パラメータ規約

- `status`: `open` / `in_progress` / `close` / `canceled`

## 4. Snapshot / Continuity との棲み分け

- task: 実行対象と進捗状態の正本
- continuity: 判断理由・制約・次の意思決定
- snapshot: チェックポイントの証跡

task の詳細を continuity に重複保存しない。必要最小限の task ID と要約のみ `working_set` に反映する。
