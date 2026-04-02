# aid-mcp-test-01

Cisco AI Defense（AID）の MCP スキャン・ゲートウェイ検証用の **架空社員名簿 MCP サーバー** です。  
`employees.json` のデータはすべて合成であり、実在の個人情報ではありません。

## リポジトリ構成

| パス | 内容 |
|------|------|
| `mcp-server/mcp_server.py` | FastMCP サーバー本体（SSE / Streamable HTTP） |
| `mcp-server/employees.json` | 架空社員データ（20 件） |
| `mcp-server/tests/` | pytest テスト |
| `mcp-server/requirements.txt` | 実行依存 |
| `mcp-server/requirements-dev.txt` | テスト依存 |

## セットアップ

Python 3.10 以上が必要です（3.11+ 推奨）。  
Debian/Ubuntu で `python3 -m venv` が失敗する場合は先に `sudo apt install python3-venv` を実行してください。

```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 起動

### ローカル確認用（SSE・最小構成）

```bash
cd mcp-server
source .venv/bin/activate
python mcp_server.py
```

- 待ち受け: `http://0.0.0.0:8765`
- SSE エンドポイント: `GET /sse`
- ヘルスチェック: `GET /health`

### 外部公開・AID 連携用（Streamable HTTP）

AID は `POST /mcp` を使うため `MCP_TRANSPORT=streamable-http` で起動します。  
EC2 などでは `MCP_HOST=0.0.0.0` が必須です（`127.0.0.1` では外部から届きません）。

**フォアグラウンド:**

```bash
cd mcp-server
source .venv/bin/activate
export MCP_HOST=0.0.0.0
export MCP_PORT=8765
export MCP_TRANSPORT=streamable-http
export LOG_LEVEL=INFO
python mcp_server.py
```

**バックグラウンド（nohup）:**

```bash
cd mcp-server
export MCP_HOST=0.0.0.0
export MCP_PORT=8765
export MCP_TRANSPORT=streamable-http
export LOG_LEVEL=INFO
nohup .venv/bin/python mcp_server.py >> /tmp/mcp_server.log 2>&1 &
```

AID の **Remote Server URL** には次を指定します。

```
http://<パブリックIPv4>:8765/mcp
```

## 環境変数

| 変数 | 既定値 | 説明 |
|------|--------|------|
| `MCP_HOST` | `0.0.0.0` | バインドアドレス |
| `MCP_PORT` | `8765` | 待ち受けポート |
| `MCP_TRANSPORT` | `sse` | `sse` または `streamable-http` |
| `EMPLOYEES_JSON_PATH` | `mcp-server/employees.json` | 従業員 JSON のパス |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `WARNING` など |

## MCP クライアント接続 URL

| 転送方式 | URL |
|----------|-----|
| SSE | `http://<ホスト>:8765/sse` |
| Streamable HTTP | `http://<ホスト>:8765/mcp` |

## AID 連携時の注意

- **セキュリティグループ:** AID の送信元 IP は [AI Defense User Guide](https://securitydocs.cisco.com/docs/ai-def/user/97360.ditamap)（Administration → Regional Points of Presence）を参照し、該当リージョンの Service Address を SG インバウンドに追加してください（IP の桁を 1 字でも間違えると届きません）。
- **疎通確認:** `curl -sS http://127.0.0.1:8765/health` が `{"status":"ok","employee_count":20}` を返し、`ss -tlnp | grep 8765` で `0.0.0.0:8765` が LISTEN 状態であることを確認してください。
- **405 が返る場合:** AID が `GET /sse` ではなく `POST` を使っています。`MCP_TRANSPORT=streamable-http` で起動し URL を `/mcp` に変更してください。
- **HTTPS が必要な場合:** このリポジトリには TLS 終端は含まれていません。ALB やリバースプロキシを前段に置いてください。

## テスト

```bash
cd mcp-server
pip install -r requirements-dev.txt
pytest
```

## 注意事項

承認されたラボ・検証環境での利用を想定しています。`my_number` 等は JSON のダミーキーであり、実在の個人番号や業務データではありません。
