# crate-codex-skills

Crate を Codex で運用開始するための公開サンプルです。

このリポジトリには次の 3 点を含みます。

- Crate 用 skill のサンプル実装
- ユーザー環境へ skill を配置するインストールスクリプト
- `AGENTS.md` へ追記するためのテンプレート

## リポジトリ構成

- `codex/skills/crate/SKILL.md`: Crate 運用用 skill
- `scripts/install.sh`: skill インストール補助スクリプト
- `templates/AGENTS.crate.md`: `AGENTS.md` 追記テンプレート
- `examples/mcp-config.json`: MCP 設定サンプル

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

- `project_id`: Crate の project UUID
- `project_token`: Crate で発行した token

## 2. Crate 用 skill を導入

### 方法A: Codex にインストール依頼（推奨）

次をそのまま Codex に渡してください。

```txt
https://github.com/arrhq/crate-codex-skills/tree/main/codex/skills/crate を参照して、crate skill をインストールしてください。
```

### 方法B: スクリプトで導入

```bash
git clone https://github.com/arrhq/crate-codex-skills.git
cd crate-codex-skills
./scripts/install.sh
```

`AGENTS.md` への追記まで自動化する場合:

```bash
./scripts/install.sh --append-agents
```

## 3. `AGENTS.md` へ追記

手動で追記する場合は `templates/AGENTS.crate.md` を既存の `AGENTS.md` にコピーしてください。

## 4. 動作確認

導入後、Codex 上で次を順に実行して成功することを確認してください。

1. `list_project_tasks`
2. `get_session_continuity`
3. `upsert_session_continuity`

## セキュリティ注意

- token は最小権限で発行してください
- token を Git 管理しないでください
- `AGENTS.md` は運用ルールの正本として PR レビュー対象にしてください
