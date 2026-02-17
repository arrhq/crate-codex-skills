# crate-codex-skills

Crate を Codex で運用開始するための公開導入セットです。

このリポジトリには次を含みます。

- crate 系 skills（`crate` と `crate-*`）
- 導入スクリプト（`scripts/install.sh`）
- `AGENTS.md` 追記テンプレート
- MCP 設定サンプル

## リポジトリ構成

- `codex/skills/README.md`: crate系 skill 一覧
- `codex/skills/*/SKILL.md`: 各 skill 実体
- `scripts/install.sh`: crate系 skills 一括導入スクリプト
- `templates/AGENTS.crate.md`: `AGENTS.md` 追記テンプレート
- `examples/mcp-config.json`: MCP 設定サンプル

## 導入される skill セット

- `crate`
- `crate-dev-ops`
- `crate-pr-ops`
- `crate-continuity-ledger`
- `crate-create-context`
- `crate-create-snapshot`
- `crate-task-ops`
- `crate-session-ops`

## 1. MCP 接続設定

`~/.codex/config.json` へ、次の `mcpServers.crate` 設定を追加してください。

```json
{
  "mcpServers": {
    "crate": {
      "type": "http",
      "url": "https://crateio.com/api/mcp?project_id=<project_id>",
      "headers": {
        "x-crate-ingest-token": "<project_token>"
      }
    }
  }
}
```

## 2. Skill 導入

### 方法A: Codex に導入依頼（推奨）

```txt
https://github.com/arrhq/crate-codex-skills/tree/main/codex/skills/README.md を確認して、crate系スキルをインストールしてください。
```

### 方法B: スクリプトで導入

```bash
git clone https://github.com/arrhq/crate-codex-skills.git
cd crate-codex-skills
./scripts/install.sh
```

`AGENTS.md` 追記まで自動化する場合:

```bash
./scripts/install.sh --append-agents
```

## 3. `AGENTS.md` 追記

テンプレート: `templates/AGENTS.crate.md`

## 4. 動作確認

導入後、Codex 上で次を順に実行して成功することを確認してください。

1. `list_project_tasks`
2. `get_session_continuity`
3. `upsert_session_continuity`

## 5. outbox 再送（任意）

snapshot 送信失敗で `~/.codex/state/crate-snapshot-outbox.ndjson` に pending が残った場合は、次で再送できます。

```bash
~/.codex/skills/crate/crate-create-snapshot/scripts/replay_snapshot_outbox.sh
```

事前確認のみの場合:

```bash
~/.codex/skills/crate/crate-create-snapshot/scripts/replay_snapshot_outbox.sh --dry-run
```
