# Trigger Policy

## 実行してよいトリガー

1. 明示トリガー
- ユーザー入力に `$create-snapshot` 行がある
- `ingest_turn` を実行

2. 自律トリガー（checkpoint）
- 次のいずれかでのみ `create_snapshot` を実行する:
  - 仕様/設計判断が確定した
  - 主要実装マイルストーンが完了した
  - テスト/検証マイルストーンが完了した
  - 成果を外部共有できる状態になった（PR作成、release note草案、tag作成など）
  - 重要な方針転換が発生した
- checkpoint 送信は必ず checkpoint gate（送信 + create_context検証）を通す。

## 実行しない条件

- 挨拶・雑談のみ
- 判断/節目がない継続実装中
- 意味のある差分がない同一checkpointの再送
- 判断影響や根拠アンカーがない運用メモのみ（例: "tests passed"）

## 可視性

- `snapshot accepted` / `snapshot skipped` は通常チャットで無言。
- `snapshot ingest failed` のときだけ1行通知する。

## クールダウン

- 同一 `session_id` 内では、意味のある差分が出てから次を送る。
- `snapshot skipped ... reason=no_new_messages` を受けたら即時再送しない。
- 低情報snapshotを複数送るより、checkpointごとに高情報snapshotを1件送る。
- checkpoint gate fail 時は outbox fallback 前に1回だけ再試行する。
