# Result Handling

## 成功時

- `get_session_continuity` があり十分なら、まず continuity を優先して回答する。
- `reconstruction_prompt` と `results` から要点を短くまとめる:
  - 現在有効な決定事項
  - 主要な前提
  - 直近の方向転換
- 根拠があれば必ず示す:
  - context_label（`task:...` / `spec:...` など）
  - URL
  - user request 抜粋
  - PR/Issue anchor（存在する場合のみ）
- 根拠が薄い場合は不確実性を明示する。

## Checkpoint検証モード

- query に `checkpoint:<note>:<work_slug>` が含まれる場合は検証モードとして扱う。
- Pass:
  - Top3 のいずれかで同一 `checkpoint_label` が確認できる。
- Fail:
  - Top3 で `checkpoint_label` が確認できない。
  - `create_snapshot` 側へ retry / outbox fallback を返す。

## 結果なし

- 関連snapshotが見つからないことを伝える。
- query を狭めるか、別アンカーでの再実行を提案する。
- 次のcheckpointで高シグナルsnapshotを追加することを提案する。

## 失敗時

- 失敗理由を1行で示す。
- query を短くして1回だけ再試行する。
- 再試行も失敗なら、ローカル文脈で継続しつつ context 取得不可を明示する。
