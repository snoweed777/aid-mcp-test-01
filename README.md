# aid-mcp-test-01

検証・デモ用の **架空社員名簿 MCP サーバー**（SSE 転送）と仕様メモです。データはすべて合成であり、実在の個人情報ではありません。

## 含まれるもの

| パス | 内容 |
|------|------|
| `mcp-server/` | FastMCP 実装、`employees.json`、テスト、依存関係 |
| `docs/mcp-demo-spec.md` | デモ仕様 |
| `docs/mcp-demo-work-plan.md` | 作業メモ |
| `docs/openapi (1).json` | 参考用 OpenAPI（プロダクト連携のスキーマ例） |

## 再現手順（MCP サーバー）

前提: Python 3.10+（3.11+ 推奨）。Debian/Ubuntu で `ensurepip is not available` となる場合は `sudo apt install python3-venv` を先に実行してください。

```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # テスト実行時のみ
```

### 起動

```bash
python mcp_server.py
```

既定で `http://0.0.0.0:8765` にバインドし、SSE は `/sse`、ヘルスチェックは `GET /health` です。

環境変数（任意）:

- `MCP_HOST` / `MCP_PORT` — バインド先
- `EMPLOYEES_JSON_PATH` — 従業員 JSON のパス（未指定時は `mcp-server/employees.json`）
- `LOG_LEVEL` — `DEBUG` など

### テスト

```bash
cd mcp-server
source .venv/bin/activate
pytest
```

## Cursor / MCP クライアント接続例

SSE URL は `http://<ホスト>:8765/sse` を指定してください（ローカルなら `http://127.0.0.1:8765/sse`）。

## ライセンス・利用上の注意

承認されたラボ・検証環境での利用を想定しています。`my_number` 等は JSON のダミー項目であり、公的番号や本番の社員 ID ではありません。
