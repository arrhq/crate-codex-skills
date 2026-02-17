---
name: crate-continuity-ledger
description: 開発や実装を行う際に、セッションの本質的な状態を圧縮安全な方法で捉えた単一のContinuity Ledgerを維持するため、このスキルを使用する。
---

# Continuity Ledger (compaction-safe)

- 正本は Crate MCP の `get_session_continuity` / `upsert_session_continuity` で管理する。
- 保存単位は **`project_id + session_id`**。セッションごとに完全分離する。
- ローカル `CONTINUITY.md` は作成しない。
- Ledgerに反映されていない限り、過去チャット内容には依存しない。

## How it works

1. **ターン開始時**: `get_session_continuity` で現在の continuity を復元する。
2. 調査/計画/Web検索を開始する前に、`get_session_continuity` を再実行して起点を固定し、`create_context` を必ず実行する。
3. 目標/制約/重要判断/進捗（Done・Now・Next）/Open questions/Working set が変化したら、`upsert_session_continuity` で更新する。
4. 可能な限り `expected_version` を渡して楽観ロックを有効化し、競合時は再取得して再適用する。
5. 事実のみを記録し、逐語ログは入れない。不確実は `UNCONFIRMED` と明示する。
6. 記憶抜けや圧縮が疑われる場合も、まず continuity を再取得して不足のみを質問する（1〜3個、仮案付き）。

## `functions.update_plan` と Ledger の使い分け

- `functions.update_plan` は短期の実行手順管理に使う。
- session continuity は圧縮やセッション跨ぎで維持する長期状態（何を/なぜ/現在状態）に使う。
- 細かな作業ログではなく、意図と進捗レベルを維持する。

## Task との棲み分け

- task 操作手順の正本は `crate-task-ops` スキルとし、運用判断もそれに従う。
- task（`list_project_tasks` / `create_project_task` / `update_project_task`）は実行対象の進捗管理に使う。
- continuity は「なぜそのtaskを実行するか」「判断と制約」「次の意思決定」を保持する。
- task の詳細説明を continuity に重複転記しない。必要最小限の task ID/要約のみ `working_set` へ保持する。

## 返信時のルール

- 冒頭に、簡潔な **「継続状態サマリ」**（目標 + 現在/次 + 未解決事項）を必ず記載。Ledger 全体は、**実質的な変更があった場合**、または**ユーザーから求められた場合のみ**出力。

## Session Continuity Stateフォーマット

日本語で記述する。

- `goal`
- `constraints`
- `key_decisions`
- `state`
- `done`
- `now`
- `next`
- `open_questions`（必要なら `UNCONFIRMED`）
- `working_set`（files/ids/commands）

`goal` / `constraints` / `key_decisions` / `state` / `done` / `now` / `next` / `open_questions` の値は日本語で記述する。  
（キー名や `UNCONFIRMED` は仕様上の識別子としてそのまま使用可）
PR/Issue番号を `key_decisions` / `done` / `next` などに記載する場合は、可能な限りGitHub URLも併記する。

## Failure Policy

- Crate MCP が利用できない場合は、continuity 更新を伴う作業を停止する。
- 代替としてローカルファイルへ退避しない。
- 失敗理由をユーザーへ短く共有し、復旧または方針変更の指示を待つ。
