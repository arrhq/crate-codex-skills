---
name: crate-session-ops
description: 計画整理・進捗共有・引き継ぎを統合した運用スキル。mode により plan / status / handover-file を切り替える。
---

# Session Ops

セッション運用系の共通スキル。以下の mode を使い分ける。

- `plan`: これからの方針と選択肢を整理
- `status`: Done / Now / Next / Open Questions の短報
- `handover-file`: 明示依頼時のみ引き継ぎMarkdownを作成

## 0. 共通前提

- まず `get_session_continuity` で状態を復元する。
- 目標/制約/判断/進捗が更新されたら `upsert_session_continuity` へ反映する。
- 必要時のみ `create_context` で履歴を補完する。
- 実装系タスクでは `crate-task-ops` を使い、開始時確認と必要時の task 作成を行う。

## mode=`plan`

- 目的、完了条件、制約、リスク、候補案を整理する。
- 候補は `採用/保留/却下` の状態を付ける。
- 実装に進む前の判断ポイントを明示する。
- 複数ステップ作業で既存taskが無い場合は、作成するtaskの最小集合を定義する（細かく分割しすぎない）。

## mode=`status`

- 次を短く提示する。
  - Done
  - Now
  - Next
  - Open Questions
- 関連taskがある場合は、`task_id` と現在ステータス（`open` / `in_progress` / `close` / `canceled`）を併記する。

## mode=`handover-file`

- ユーザーが明示した場合のみ `~/Downloads` にMarkdownを作成する。
- 必須項目:
  - 背景
  - 現在地（Done/Now/Next）
  - 主要判断
  - 未解決事項
  - 再開手順
- 秘密情報は含めない。

## Notes

- 通常の会話は `plan` または `status` で十分。`handover-file` は最小限に使う。
- `CONTINUITY` 全文貼り付けではなく、要点と根拠アンカーを優先する。
