#  Flask + PostgreSQL Quick Setup Guide (Mac / Homebrew)

This guide helps you set up your Flask + PostgreSQL environment from scratch.

---

## Install PostgreSQL (via Homebrew)
```bash
brew install postgresql
```

---

## Start PostgreSQL Service
讓 PostgreSQL 在背景常駐（開機自動啟動）：
```bash
brew services start postgresql
```

確認服務是否正在運行：
```bash
brew services list
```

---

## Create Database
進入 PostgreSQL：
```bash
psql postgres
```

建立專案用的資料庫（例如 `shift_scheduling`）：
```sql
CREATE DATABASE shift_scheduling;
\l       -- 查看所有資料庫
\q       -- 離開
```

---

## Initialize Flask Migrations
第一次使用 Alembic：
```bash
flask db init
```

建立初始 migration 檔：
```bash
flask db migrate -m "init database"
```

套用變更（建立資料表）：
```bash
flask db upgrade
```

---

## Run Flask Server
啟動開發伺服器：
```bash
flask run
```

預設會運行在：
```
http://127.0.0.1:5050
```

若看到：
```
* Debug mode: on
* Running on http://127.0.0.1:5050
```
代表一切設定成功

---

## Optional Commands
| 動作 | 指令 |
|------|------|
| 停止 PostgreSQL | `brew services stop postgresql` |
| 登入資料庫 CLI | `psql shift_scheduling` |
| 檢查目前 migrations | `flask db history` |
| 回滾到前一版本 | `flask db downgrade` |

---

##Environment Example (`.env`)
```bash
DATABASE_URL=postgresql+psycopg2://user:yourpassword@localhost:portnumber/databaseName
FLASK_APP=app:create_app
FLASK_ENV=development
FLASK_RUN_PORT=5050
FLASK_DEBUG=1
```

---

**Now you're ready to run your Flask + PostgreSQL project**
