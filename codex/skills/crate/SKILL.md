---
name: crate
description: Crate MCP を利用した task/continuity/snapshot 運用を行うためのスキル。
---

# crate

Crate を使う作業では、次の順でツールを使います。

## 1. セッション開始

- `get_session_continuity` で現在状態を復元する
- 複数ステップ作業なら `list_project_tasks` で `open` / `in_progress` を確認する

## 2. 作業中

- 既存taskで表現できない場合のみ `create_project_task` を使う
- 着手時: `update_project_task(status=in_progress)`
- 完了時: `update_project_task(status=close)`
- 中止時: `update_project_task(status=canceled)`

## 3. 判断ログ

以下が変化したら `upsert_session_continuity` を使う。

- goal
- constraints
- key_decisions
- done / now / next

## 4. 履歴参照

次の依頼では `create_context` を使って要点を取り出す。

- 設計理由の説明
- 前提変更の説明
- 引き継ぎ要約

## 5. Snapshot

次のチェックポイントで `create_snapshot` を送る。

- 仕様確定
- 主要実装完了
- テスト完了
- 成果公開
- 方針転換

ユーザーが `$create-snapshot` を明示した場合は `ingest_turn` を優先する。
