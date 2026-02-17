# Conversation Slice テンプレート

## 必須ブロック

次の5ブロックを必ず含める。

1. 決定事項
2. 決定理由
3. 前提/制約
4. 方向転換（なければ `なし`）
5. 未解決事項/次アクション

加えて、evidence anchor を最低1つ含める。

- context_label
- user_request
- url

`pr_or_issue` は存在する場合のみ補助アンカーとして追加する。

本文（値）は日本語で記述し、キー名は仕様に合わせて英語のままでよい。

## 推奨フォーマット

```json
[
  {
    "type": "snapshot_context_v1",
    "checkpoint": "impl_done",
    "decision": ["検索はローカル優先にする"],
    "reason": ["応答速度と再現性を優先するため"],
    "assumptions": ["インデックス更新は日次で十分"],
    "pivots": ["なし"],
    "open_questions": ["更新遅延をどこまで許容するか"],
    "verification": ["E2Eで主要ケースを確認済み"],
    "links": ["https://..."],
    "evidence": {
      "context_labels": [
        "checkpoint:tests_passed:auth-flow-v2",
        "task:auth-flow-v2"
      ],
      "user_requests": ["snapshotを日本語で統一したい"],
      "urls": ["https://..."],
      "anchors": ["PR #447", "Issue #451"]
    }
  }
]
```

## 最小フォーマット

```json
[
  {
    "role": "user",
    "content": "決定事項: ... 決定理由: ... 前提/制約: ... 方向転換: ... 未解決事項/次アクション: ... 根拠: context_label checkpoint:tests_passed:..., context_label task:..., ユーザー依頼 <...>, URL <...>"
  }
]
```

## 悪い例

- `"LGTM"` だけ
- 生ログだけ
- 同一内容の再送
- 判断影響のない運用メモだけ（例: `tests passed`）
- `checkpoint:<note>:<work_slug>` ラベルなしの checkpoint 送信
