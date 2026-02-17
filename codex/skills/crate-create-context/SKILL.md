---
name: crate-create-context
description: Crate の履歴文脈を必要時だけ取得する運用スキル。明示 `$crate-create-context` または履歴参照が必要な質問時に `create_context` を実行し、要点のみを回答へ反映する。
---

# Create Context

## Core Policy

- 常時注入はしないが、調査/計画/Web検索タスクでは `create_context` を必須で実行する。
- セッション開始/再開では `get_session_continuity` を先に実行し、足りない履歴のみ `create_context` で補う。
- 回答は要点優先。生ログや長文JSONをそのまま貼らない。
- `create_snapshot` と同じ MCP 接続（`project_id` + `x-crate-ingest-token` ヘッダ）で使う。
- 回答時は `results` の score だけでなく evidence（`context_label` / URL / User request）を根拠として使う。PR/Issueは任意。
- checkpoint gate 検証クエリ（`checkpoint:<note>:<work_slug>`）では、Top3 内に同一 label があるかを必ず確認する。

## Trigger

1. 入力に `$crate-create-context` があるときは `create_context` を実行する。
2. `$crate-create-context` がなくても、調査/計画/Web検索を開始する場合は必ず `create_context` を実行する。
3. `$crate-create-context` がなくても、次の質問では自律実行してよい。
- 現在の状態/判断/前提/最近の方針転換を説明してほしい
- 以前の議論理由や変更背景（PR有無を問わない）を参照したい
- 引き継ぎ・再開で履歴再構成が必要
4. ローカルコードだけで十分答えられる純実装質問では実行しない。
5. 直近セッション内の現在状態だけで答えられる場合は `get_session_continuity` を優先し、履歴検索は省略してよい。
6. `create_snapshot` 直後の到達確認では、要約回答よりも `checkpoint_label` のヒット有無判定を優先する。

## Visibility

- 通常は「履歴から再構成した要点」だけを回答する。
- `results` 全量の貼り付けは、ユーザーが要求したときのみ。
- `create_context` 失敗時のみ1行で通知し、必要なら質問を短くして1回再試行する。

## Minimum Contract

- 必須: `query`
- 条件付き必須: `project_id`（MCP URLに未指定の場合）
- 返却の `reconstruction_prompt` と `results(Top3)` を使って回答を組み立てる。
- `results` に `evidence` / `evidence_anchor_adjustment` がある場合は、回答内で根拠として優先的に参照する（`context_label` / URL / user request を優先）。
- `query` と通常回答の本文は日本語で記述する（識別子やアンカー名は英語のままでよい）。

## References

- Trigger: `references/trigger-policy.md`
- Fields: `references/field-contract.md`
- Query design: `references/query-template.md`
- Result handling: `references/result-handling.md`
