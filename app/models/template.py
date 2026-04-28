"""
app/models/template.py
常用模板 Model

負責 templates 資料表的 CRUD 操作。
管理使用者建立的常用交易模板，用於一鍵快速記帳。
"""

from datetime import datetime
from app.models.database import get_db, close_db


def create_template(name, type, amount, category_id, note=''):
    """
    新增一個常用模板。

    參數：
        name (str): 模板名稱（如「午餐」）
        type (str): 交易類型，'income' 或 'expense'
        amount (float): 預設金額
        category_id (int): 分類 ID
        note (str): 預設備註（選填）

    回傳：
        int: 新建模板的 ID
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.execute(
            '''INSERT INTO templates (name, type, amount, category_id, note, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (name, type, amount, category_id, note, now, now)
        )
        db.commit()
        return cursor.lastrowid
    finally:
        close_db(db)


def get_all_templates():
    """
    取得所有常用模板。

    回傳：
        list[sqlite3.Row]: 模板列表，每筆包含分類名稱
    """
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT t.*, c.name as category_name
               FROM templates t
               LEFT JOIN categories c ON t.category_id = c.id
               ORDER BY t.name ASC'''
        ).fetchall()
        return rows
    finally:
        close_db(db)


def get_template_by_id(template_id):
    """
    根據 ID 取得單一模板。

    參數：
        template_id (int): 模板 ID

    回傳：
        sqlite3.Row 或 None
    """
    db = get_db()
    try:
        row = db.execute(
            '''SELECT t.*, c.name as category_name
               FROM templates t
               LEFT JOIN categories c ON t.category_id = c.id
               WHERE t.id = ?''',
            (template_id,)
        ).fetchone()
        return row
    finally:
        close_db(db)


def update_template(template_id, name, type, amount, category_id, note=''):
    """
    更新常用模板。

    參數：
        template_id (int): 模板 ID
        name (str): 模板名稱
        type (str): 交易類型
        amount (float): 預設金額
        category_id (int): 分類 ID
        note (str): 預設備註
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            '''UPDATE templates
               SET name = ?, type = ?, amount = ?, category_id = ?, note = ?, updated_at = ?
               WHERE id = ?''',
            (name, type, amount, category_id, note, now, template_id)
        )
        db.commit()
    finally:
        close_db(db)


def delete_template(template_id):
    """
    刪除常用模板。

    參數：
        template_id (int): 模板 ID
    """
    db = get_db()
    try:
        db.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        db.commit()
    finally:
        close_db(db)
