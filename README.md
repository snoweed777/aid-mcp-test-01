# aid-mcp-test-01

検証・デモ用の **架空社員名簿 MCP サーバー**（FastMCP: **SSE** または **Streamable HTTP**）です。データはすべて合成であり、実在の個人情報ではありません。

## 含まれるもの

| パス | 内容 |
|------|------|
| `mcp-server/` | FastMCP 実装、`employees.json`、テスト、依存関係 |

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

ヘルスチェックはどちらの転送でも **`GET /health`** です。

#### 最小例（SSE・既定どおり）

`MCP_HOST` / `MCP_TRANSPORT` を省略すると **`0.0.0.0:8765`** で **SSE**（`GET /sse`）になります。

```bash
cd mcp-server
source .venv/bin/activate   # 初回のみ venv 作成・pip install
python mcp_server.py
```

#### 環境変数を明示した例（SSE・IDE / curl クライアント向け）

```bash
cd mcp-server
source .venv/bin/activate
export MCP_HOST=0.0.0.0
export MCP_PORT=8765
export MCP_TRANSPORT=sse
export LOG_LEVEL=INFO
# 任意: 別パスの JSON を読む場合
# export EMPLOYEES_JSON_PATH=/path/to/employees.json
python mcp_server.py
```

**接続 URL（SSE）:** `http://<ホスト>:8765/sse`（続けて `POST .../messages/?session_id=...` を使うクライアント向け）

#### 環境変数を明示した例（Streamable HTTP・Cisco AID 向け）

AID は **`POST /mcp`** を使うため **`MCP_TRANSPORT=streamable-http`** で起動します。EC2 などでは **`MCP_HOST=0.0.0.0`** が必須です（`127.0.0.1` のままだと外部から届きません）。

**前景（フォアグラウンド）:**

```bash
cd mcp-server
source .venv/bin/activate
export MCP_HOST=0.0.0.0
export MCP_PORT=8765
export MCP_TRANSPORT=streamable-http
export LOG_LEVEL=INFO
# 任意: export EMPLOYEES_JSON_PATH=/path/to/employees.json
python mcp_server.py
```

**バックグラウンド（`nohup` 例・ログをファイルへ）:**

```bash
cd mcp-server
export MCP_HOST=0.0.0.0
export MCP_PORT=8765
export MCP_TRANSPORT=streamable-http
export LOG_LEVEL=INFO
nohup .venv/bin/python mcp_server.py >> /tmp/mcp_server.log 2>&1 &
```

**AID の Remote URL（HTTP）:** `http://<パブリックIPv4>:8765/mcp`

---

転送の違い:

- **`MCP_TRANSPORT` 未指定または `sse`:** **SSE** — `GET /sse` でイベントストリーム。クライアントは続けて **`POST .../messages/?session_id=...`** も使う（ファイアウォールは両方許可が必要な場合あり）。
- **`MCP_TRANSPORT=streamable-http`:** **Streamable HTTP** — **`POST /mcp`**。クライアントの **`Accept` に `application/json` と `text/event-stream` の両方**が必要です（欠けると **406**）。AID 側が仕様どおり送れば問題になりません。

環境変数一覧（参考）:

| 変数 | 既定 | 説明 |
|------|------|------|
| `MCP_HOST` | `0.0.0.0` | バインドアドレス。外部公開時は **`127.0.0.1` にしない** |
| `MCP_PORT` | `8765` | 待ち受けポート |
| `MCP_TRANSPORT` | `sse` | `sse` または `streamable-http` |
| `EMPLOYEES_JSON_PATH` | （`mcp-server/employees.json`） | 従業員 JSON の絶対パス |
| `LOG_LEVEL` | `INFO` | `DEBUG` など |

### EC2・Cisco AI Defense（AID）など外部から繋ぐ場合

- **AID で `405 Method Not Allowed` と `/sse` になる場合:** 登録先が **`POST` 前提**のことがあります。サーバを **`MCP_TRANSPORT=streamable-http` で起動**し、Remote URL を **`http://<パブリックIPv4>:8765/mcp`** にする（末尾 `/mcp`。パスは FastMCP 既定）。
- **SSE を使う場合の Remote URL（HTTP の例）:** `http://<パブリックIPv4>:8765/sse`（**GET のみ**が有効。`POST` だけ投げるチェックでは 405 になるのは正常）
- **セキュリティグループ:** AID が接続に使う送信元は **Cisco 公式の「Regional Points of Presence」（Service Address）** に合わせて許可する（リージョンごとに IP が異なる。**表の IP を桁違いなく** SG に入れる）
- **疎通確認:** インスタンス上で `curl -sS http://127.0.0.1:8765/health` が `200` かつ、`ss -tlnp` で **`0.0.0.0:8765`**（またはパブリック向けに意図したインタフェース）で LISTEN していること
- AID やクライアントが **HTTPS 必須**の場合は、443 で TLS 終端するリバースプロキシ等が別途必要（このリポジトリには含めていない）

### テスト

```bash
cd mcp-server
source .venv/bin/activate
pytest
```

## Cursor / MCP クライアント接続例

- SSE: `http://<ホスト>:8765/sse`（ローカルなら `http://127.0.0.1:8765/sse`）
- Streamable HTTP: `MCP_TRANSPORT=streamable-http` で起動し `http://<ホスト>:8765/mcp`

## ライセンス・利用上の注意

承認されたラボ・検証環境での利用を想定しています。`my_number` 等は JSON のダミー項目であり、公的番号や本番の社員 ID ではありません。
