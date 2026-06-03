"""
app/models/category.py
分類 Model

負責 categories 資料表的 CRUD 操作。
管理收入與支出的分類標籤。
"""

from datetime import datetime
from app.models.database import get_db, close_db


def create_category(name, type):
    """
    新增一個分類。

    參數：
        name (str): 分類名稱
        type (str): 分類類型，'income' 或 'expense'

    回傳：
        int: 新建分類的 ID
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.execute(
            'INSERT INTO categories (name, type, created_at) VALUES (?, ?, ?)',
            (name, type, now)
        )
        db.commit()
        return cursor.lastrowid
    finally:
        close_db(db)


def get_all_categories():
    """
    取得所有分類。

    回傳：
        list[sqlite3.Row]: 分類列表
    """
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM categories ORDER BY type, name'
        ).fetchall()
        return rows
    finally:
        close_db(db)


def get_categories_by_type(type):
    """
    根據類型取得分類（收入或支出）。

    參數：
        type (str): 'income' 或 'expense'

    回傳：
        list[sqlite3.Row]: 該類型的分類列表
    """
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM categories WHERE type = ? ORDER BY name',
            (type,)
        ).fetchall()
        return rows
    finally:
        close_db(db)


def get_category_by_id(category_id):
    """
    根據 ID 取得單一分類。

    參數：
        category_id (int): 分類 ID

    回傳：
        sqlite3.Row 或 None
    """
    db = get_db()
    try:
        row = db.execute(
            'SELECT * FROM categories WHERE id = ?',
            (category_id,)
        ).fetchone()
        return row
    finally:
        close_db(db)


def update_category(category_id, name, type):
    """
    更新分類名稱與類型。

    參數：
        category_id (int): 分類 ID
        name (str): 新名稱
        type (str): 新類型
    """
    db = get_db()
    try:
        db.execute(
            'UPDATE categories SET name = ?, type = ? WHERE id = ?',
            (name, type, category_id)
        )
        db.commit()
    finally:
        close_db(db)


def delete_category(category_id):
    """
    刪除分類。

    注意：如果有交易紀錄引用此分類，刪除會失敗（外鍵約束）。

    參數：
        category_id (int): 分類 ID
    """
    db = get_db()
    try:
        db.execute('DELETE FROM categories WHERE id = ?', (category_id,))
        db.commit()
    finally:
        close_db(db)
