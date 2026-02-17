# Query Template

## Minimal

`<対象> の <知りたい軸> を教えて`

## Recommended

`<対象> について、<決定事項/決定理由/前提/方向転換/リスク> を <期間> で整理して`

可能なら evidence anchor を含める:

- `task:...` / `spec:...` / `topic:...` / `decision:...`
- URL
- user request の要約（例: `ユーザー依頼: ...`）
- `PR #...` / `Issue #...`（GitHub運用時のみ）

## Examples

- `現在状態について、決定事項と前提を整理して`
- `検索機能の方針転換だけを要約して`
- `直近3日で変化した制約を教えて`
- `task:decision-cache-v2 の背景で、設計判断と前提を整理して`
- `PR #456 と Issue #451 の関係で、設計判断の根拠を整理して`
- `https://... のURLを渡したときに決まった前提を教えて`
- `checkpoint:tests_passed:search-local-first の決定事項と決定理由を確認`
- `checkpoint:deliverable_shared:memory-docs が保存されているか確認`

## Anti-pattern

- `教えて` only
- `全部` only
- too broad question mixing unrelated projects
- anchor無しで曖昧（例: `最近どう？` のみ）
