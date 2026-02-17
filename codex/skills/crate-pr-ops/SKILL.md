---
name: crate-pr-ops
description: Crate環境でのPR作成・更新・レビュー反復・マージ時に、continuity/task/snapshot運用を適用するオーバーレイスキル。
---

# Crate PR Ops

Crate環境でPR関連作業を行う際に、PRフロー系スキルの有無に依存せず Crate運用を適用する。

## 0. 起動条件

- PR作成 / PR更新 / レビュー反復 / マージ対応に着手する時に使う。
- PRフロースキルの有無に依存しない。

## 1. PR作成・更新前

- `get_session_continuity` で最新状態を復元する。
- 必要に応じて `create_context` で根拠を補完する。
- 重要判断や前提が変わっていれば `upsert_session_continuity` へ反映する。

## 2. レビュー反復中

- 指摘対応で方針が変わった場合は、task状態と continuity を更新する。
- 複数ステップ化した場合は `crate-task-ops` で task を整理する。
- 既存taskで表現できない作業だけ新規taskを作成する。

## 3. 成果公開チェックポイント

- PR作成またはマージ完了を成果公開チェックポイントとして扱う。
- `crate-create-snapshot` に従って `note=deliverable_shared` の snapshot を送る。
- `create_context` で checkpoint gate の到達確認を行う。

## 4. 完了時

- PR対応完了時に関連taskを `status=close` へ更新する。
- 未解決事項は `open_questions` と task に残して `upsert_session_continuity` へ反映する。

## Notes

- PR本文やコメントはレビュー成立に必要な情報を優先し、冗長ログを貼り付けない。
- Crate MCPが利用不能な場合は、参照不能であることを明示して作業を停止する。
