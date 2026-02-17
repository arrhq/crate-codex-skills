---
name: crate-dev-ops
description: Crate環境での開発実装時に、continuity/task/snapshot運用を漏れなく適用するためのオーバーレイスキル。
---

# Crate Dev Ops

Crate環境で実装を進める際に、開発フロー系スキルの有無に依存せず Crate運用を適用する。

## 0. 起動条件

- 実装・調査・テストを伴う開発作業に着手する時に使う。
- 開発フロースキルが無くてもこのスキル単体で運用できる。

## 1. 開始時

- `get_session_continuity` で現在状態を復元する。
- 複数ステップ作業なら `crate-task-ops` に従って `list_project_tasks` を実行する。
- 既存taskで表現できない場合のみ `create_project_task` する。
- 作業着手時は対象taskを `status=in_progress` に更新する。

## 2. 実装中

- 調査/計画/Web検索を開始する都度 `get_session_continuity` を再実行する。
- 履歴根拠が必要な場面では `create_context` を実行する。
- 目標/制約/重要判断/Done-Now-Next/Open questions/Working set が変わったら `upsert_session_continuity` を実行する。

## 3. チェックポイント

- 次の節目で `crate-create-snapshot` に従って snapshot を送る。
  - 仕様確定
  - 主要実装完了
  - テスト完了
  - 方針転換
- 各節目は checkpoint gate とし、`create_context` で到達確認できるまで次工程へ進まない。

## 4. 終了時

- 完了したtaskを `status=close` に更新する。
- 実施しないと決めたtaskは `status=canceled` に更新する。
- 最終状態を `upsert_session_continuity` へ反映する。

## Notes

- task は実行対象管理、continuity は判断圧縮、snapshot は節目証跡として分離して扱う。
- Crate MCPが利用不能な場合は、参照不能であることを明示して作業を停止する。
