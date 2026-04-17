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

### 既定（Streamable HTTP・最小構成）

環境変数を付けずに起動すると **Streamable HTTP**（`POST /mcp`）です。AID 連携と同じ転送方式になります。

```bash
cd mcp-server
source .venv/bin/activate
python mcp_server.py
```

- 待ち受け: `http://0.0.0.0:8765`
- MCP エンドポイント: `POST /mcp`
- ヘルスチェック: `GET /health`

### 外部公開・運用時の明示設定（推奨）

EC2 などでは `MCP_HOST=0.0.0.0` を明示し、`127.0.0.1` のままにしないでください（外部から届きません）。

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

### SSE に切り替える場合（`GET /sse` のクライアント用）

```bash
cd mcp-server
source .venv/bin/activate
export MCP_TRANSPORT=sse
python mcp_server.py
```

- SSE エンドポイント: `GET /sse`（メッセージ用 POST は FastMCP の設定に従います）

## 環境変数


| 変数                    | 既定値                         | 説明                                          |
| --------------------- | --------------------------- | ------------------------------------------- |
| `PORT`                | —                           | **Render が自動設定**するポート番号（優先度最高）              |
| `MCP_HOST`            | `0.0.0.0`                   | バインドアドレス                                    |
| `MCP_PORT`            | `8765`                      | 待ち受けポート（`PORT` が未設定の場合に使用）                  |
| `MCP_TRANSPORT`       | `streamable-http`           | `streamable-http` または `sse`                 |
| `EMPLOYEES_JSON_PATH` | `mcp-server/employees.json` | 従業員 JSON のパス                                |
| `LOG_LEVEL`           | `INFO`                      | `DEBUG` / `WARNING` など                      |

ポートの優先順位: `PORT`（Render 自動設定）→ `MCP_PORT`（手動設定）→ `8765`（デフォルト）


## MCP クライアント接続 URL


| 転送方式            | URL                     |
| --------------- | ----------------------- |
| SSE             | `http://<ホスト>:8765/sse` |
| Streamable HTTP | `http://<ホスト>:8765/mcp` |


## Render へのデプロイ

このリポジトリには `render.yaml` が含まれており、[Render](https://render.com) へのワンクリックデプロイに対応しています。

### デプロイ手順

1. [https://dashboard.render.com/](https://dashboard.render.com/) にアクセスしてログイン
2. **「New +」→「Web Service」** をクリック
3. リポジトリ `aid-mcp-test-01` を選択
4. `render.yaml` が自動検出され、設定が入力済みになることを確認
5. **「Create Web Service」** をクリック

### 公開 URL（デプロイ後）

| エンドポイント        | URL                                          |
| -------------- | -------------------------------------------- |
| ヘルスチェック        | `https://aid-mcp-server.onrender.com/health` |
| MCP（Streamable HTTP） | `https://aid-mcp-server.onrender.com/mcp`    |

### 無料プランの制限事項

| 制限     | 内容                                          |
| ------ | ------------------------------------------- |
| スリープ   | 15 分間アクセスがないと停止。次回アクセス時に起動まで 30〜60 秒かかる    |
| 月間無料時間 | 750 時間 / 月（1 サービスなら実質常時稼働可）                 |
| HTTPS  | 自動で付与される                                    |

> **スリープ対策:** [UptimeRobot](https://uptimerobot.com/)（無料）で `/health` を 5 分ごとに ping する設定にすると常時起動を維持できます。


## AID 連携時の注意

- **セキュリティグループ:** AID の送信元 IP は [AI Defense User Guide](https://securitydocs.cisco.com/docs/ai-def/user/97360.ditamap)（Administration → Regional Points of Presence）を参照し、該当リージョンの Service Address を SG インバウンドに追加してください（IP の桁を 1 字でも間違えると届きません）。
- **疎通確認:** `curl -sS http://127.0.0.1:8765/health` が `{"status":"ok","employee_count":20}` を返し、`ss -tlnp | grep 8765` で `0.0.0.0:8765` が LISTEN 状態であることを確認してください。
- **405 が返る場合:** AID は `POST /mcp`（Streamable HTTP）向けです。`MCP_TRANSPORT=sse` で起動している、または接続先が `/sse` のままだと失敗しやすいので、既定どおり `streamable-http` で起動し URL を `/mcp` にしてください。
- **HTTPS が必要な場合:** このリポジトリには TLS 終端は含まれていません。ALB やリバースプロキシを前段に置いてください。

## テスト

```bash
cd mcp-server
pip install -r requirements-dev.txt
pytest
```

## 注意事項

承認されたラボ・検証環境での利用を想定しています。`my_number` 等は JSON のダミーキーであり、実在の個人番号や業務データではありません。