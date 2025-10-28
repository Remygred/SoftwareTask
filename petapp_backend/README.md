# 智慧宠物APP · Backend (FastAPI 最小骨架)

## 快速开始

```bash
python -m venv venv && source venv/bin/activate  # Windows 用 venv\Scripts\activate
pip install -r requirements.txt

# 修改 .env 中 DATABASE_URL（默认 sqlite）
uvicorn app.main:app --reload --port 8000
# 健康检查
curl http://127.0.0.1:8000/healthz
```

## 目录结构

```
app/
  ├─ main.py
  ├─ db.py
  ├─ models.py
  ├─ schemas.py
  └─ routers/
      ├─ auth.py
      ├─ pets.py
      ├─ health.py
      ├─ reminders.py
      ├─ recipes.py
      ├─ articles.py
      └─ lost.py
```

## 提示

- 这是可运行的最小骨架，数据库默认 SQLite，便于直接跑通。
- 上线建议切换 PostgreSQL，并把 `models.py` 的枚举/索引补充完整。
- 对齐你仓库中的 “原型” 页面后，我会把字段/接口再做逐项映射与完善。
