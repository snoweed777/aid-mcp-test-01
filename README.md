# aid-mcp-test-01

Cisco AI Defense（AID）の MCP スキャン・ゲートウェイ検証用の **架空社員名簿 MCP サーバー** です。  
`employees.json` のデータはすべて合成であり、実在の個人情報ではありません。

## リポジトリ構成

| パス                                | 内容                                    |
| --------------------------------- | ------------------------------------- |
| `mcp-server/mcp_server.py`        | FastMCP サーバー本体（SSE / Streamable HTTP） |
| `mcp-server/employees.json`       | 架空社員データ（20 件）                         |
| `mcp-server/tests/`               | pytest テスト                            |
| `mcp-server/requirements.txt`     | 実行依存                                  |
| `mcp-server/requirements-dev.txt` | テスト依存                                 |
| `render.yaml`                     | Render デプロイ設定                         |

## ローカル開発用セットアップ

Python 3.10 以上が必要です（3.11+ 推奨）。

```bash
cd mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ローカル起動

```bash
cd mcp-server
source .venv/bin/activate
python mcp_server.py
```

- MCP エンドポイント: `POST http://localhost:8765/mcp`
- ヘルスチェック: `GET http://localhost:8765/health`

SSE で起動する場合:

```bash
export MCP_TRANSPORT=sse
python mcp_server.py
```

- SSE エンドポイント: `GET http://localhost:8765/sse`

## 環境変数

| 変数                    | 既定値               | 説明                                          |
| --------------------- | ----------------- | ------------------------------------------- |
| `PORT`                | —                 | **Render が自動設定**するポート番号（優先度最高）              |
| `MCP_HOST`            | `0.0.0.0`         | バインドアドレス                                    |
| `MCP_PORT`            | `8765`            | 待ち受けポート（`PORT` が未設定の場合に使用）                  |
| `MCP_TRANSPORT`       | `streamable-http` | `streamable-http` または `sse`                 |
| `EMPLOYEES_JSON_PATH` | `employees.json`  | 従業員 JSON のパス（`mcp_server.py` と同ディレクトリ基準）    |
| `LOG_LEVEL`           | `INFO`            | `DEBUG` / `WARNING` など                      |

ポートの優先順位: `PORT`（Render 自動設定）→ `MCP_PORT`（手動設定）→ `8765`（デフォルト）

## Render へのデプロイ

### デプロイ手順

1. [https://dashboard.render.com/](https://dashboard.render.com/) にアクセスしてログイン
2. **「New +」→「Web Service」** をクリック
3. リポジトリ `aid-mcp-test-01` を選択
4. 以下を確認・入力する

   | 設定項目          | 値                                               |
   | ------------- | ----------------------------------------------- |
   | Root Directory | `mcp-server`                                   |
   | Build Command | `pip install -r requirements.txt`               |
   | Start Command | `python mcp_server.py`                          |

5. **「Create Web Service」** をクリック

> `render.yaml` をリポジトリルートに配置しているため、上記設定が自動入力される場合があります。

### デプロイ後の接続 URL

Render がサービス名をもとに URL を発行します（例: `https://aid-mcp-server.onrender.com`）。

| エンドポイント               | パス       |
| --------------------- | -------- |
| ヘルスチェック               | `/health` |
| MCP（Streamable HTTP） | `/mcp`   |

### 無料プランの注意事項

- 一定時間アクセスがないとサービスがスリープし、次のアクセス時に起動まで時間がかかります
- HTTPS は自動で付与されます

## AID 連携時の注意

- **接続 URL:** AID の Remote Server URL には `https://<RenderのURL>/mcp` を指定してください
- **405 が返る場合:** AID は `POST /mcp`（Streamable HTTP）向けです。`MCP_TRANSPORT=sse` で起動している場合や接続先が `/sse` になっている場合は失敗します。既定の `streamable-http` で起動し、URL を `/mcp` にしてください
- **疎通確認:** `/health` が `{"status":"ok","employee_count":20}` を返せば正常です

## テスト

```bash
cd mcp-server
pip install -r requirements-dev.txt
pytest
```

## 注意事項

承認されたラボ・検証環境での利用を想定しています。`my_number` 等は JSON のダミーキーであり、実在の個人番号や業務データではありません。
