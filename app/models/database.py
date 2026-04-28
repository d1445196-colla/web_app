"""
app/models/database.py
資料庫連線與初始化模組

負責：
- 取得資料庫連線（get_db）
- 關閉資料庫連線（close_db）
- 初始化資料庫（init_db）
"""

import sqlite3
import os


# 資料庫檔案路徑
DATABASE_PATH = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    'instance',
    'database.db'
)

# SQL Schema 檔案路徑
SCHEMA_PATH = os.path.join(
    os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    'database',
    'schema.sql'
)


def get_db():
    """
    取得資料庫連線。
    回傳的 Row 可以用欄位名稱存取（如 row['id']）。
    """
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row  # 讓查詢結果可以用欄位名稱存取
    db.execute("PRAGMA foreign_keys = ON")  # 啟用外鍵約束
    return db


def close_db(db):
    """關閉資料庫連線。"""
    if db is not None:
        db.close()


def init_db():
    """
    初始化資料庫：建立資料表並插入預設資料。
    如果資料表已存在則不會重複建立（CREATE TABLE IF NOT EXISTS）。
    """
    # 確保 instance 資料夾存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    db = get_db()
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        print(f"✅ 資料庫初始化完成：{DATABASE_PATH}")
    except Exception as e:
        print(f"❌ 資料庫初始化失敗：{e}")
        raise
    finally:
        close_db(db)
