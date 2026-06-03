"""
app/models/transaction.py
交易紀錄 Model

負責 transactions 資料表的 CRUD 操作。
收入與支出共用同一張表，透過 type 欄位區分。
"""

from datetime import datetime
from app.models.database import get_db, close_db


def create_transaction(type, amount, category_id, date, note=''):
    """
    新增一筆交易紀錄。

    參數：
        type (str): 交易類型，'income' 或 'expense'
        amount (float): 金額（正數）
        category_id (int): 分類 ID
        date (str): 交易日期（YYYY-MM-DD）
        note (str): 備註（選填）

    回傳：
        int: 新建交易的 ID
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.execute(
            '''INSERT INTO transactions (type, amount, category_id, date, note, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (type, amount, category_id, date, note, now, now)
        )
        db.commit()
        return cursor.lastrowid
    finally:
        close_db(db)


def get_all_transactions():
    """
    取得所有交易紀錄（依日期降序排列）。

    回傳：
        list[sqlite3.Row]: 交易紀錄列表，每筆包含分類名稱
    """
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT t.*, c.name as category_name
               FROM transactions t
               LEFT JOIN categories c ON t.category_id = c.id
               ORDER BY t.date DESC, t.created_at DESC'''
        ).fetchall()
        return rows
    finally:
        close_db(db)


def get_transaction_by_id(transaction_id):
    """
    根據 ID 取得單筆交易紀錄。

    參數：
        transaction_id (int): 交易 ID

    回傳：
        sqlite3.Row 或 None
    """
    db = get_db()
    try:
        row = db.execute(
            '''SELECT t.*, c.name as category_name
               FROM transactions t
               LEFT JOIN categories c ON t.category_id = c.id
               WHERE t.id = ?''',
            (transaction_id,)
        ).fetchone()
        return row
    finally:
        close_db(db)


def update_transaction(transaction_id, type, amount, category_id, date, note=''):
    """
    更新一筆交易紀錄。

    參數：
        transaction_id (int): 交易 ID
        type (str): 交易類型
        amount (float): 金額
        category_id (int): 分類 ID
        date (str): 交易日期
        note (str): 備註
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            '''UPDATE transactions
               SET type = ?, amount = ?, category_id = ?, date = ?, note = ?, updated_at = ?
               WHERE id = ?''',
            (type, amount, category_id, date, note, now, transaction_id)
        )
        db.commit()
    finally:
        close_db(db)


def delete_transaction(transaction_id):
    """
    刪除一筆交易紀錄。

    參數：
        transaction_id (int): 交易 ID
    """
    db = get_db()
    try:
        db.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        db.commit()
    finally:
        close_db(db)


def get_balance():
    """
    計算總餘額（所有收入 - 所有支出）。

    回傳：
        float: 總餘額
    """
    db = get_db()
    try:
        row = db.execute(
            '''SELECT
                 COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0)
                 - COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0)
                 AS balance
               FROM transactions'''
        ).fetchone()
        return row['balance']
    finally:
        close_db(db)


def get_monthly_summary(year, month):
    """
    取得指定月份的收支摘要。

    參數：
        year (int): 年份
        month (int): 月份

    回傳：
        dict: {'income': float, 'expense': float}
    """
    db = get_db()
    try:
        month_str = f'{year}-{month:02d}'
        row = db.execute(
            '''SELECT
                 COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) AS income,
                 COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS expense
               FROM transactions
               WHERE strftime('%Y-%m', date) = ?''',
            (month_str,)
        ).fetchone()
        return {'income': row['income'], 'expense': row['expense']}
    finally:
        close_db(db)


def get_recent_transactions(limit=5):
    """
    取得最近的交易紀錄。

    參數：
        limit (int): 回傳筆數，預設 5

    回傳：
        list[sqlite3.Row]: 交易紀錄列表
    """
    db = get_db()
    try:
        rows = db.execute(
            '''SELECT t.*, c.name as category_name
               FROM transactions t
               LEFT JOIN categories c ON t.category_id = c.id
               ORDER BY t.date DESC, t.created_at DESC
               LIMIT ?''',
            (limit,)
        ).fetchall()
        return rows
    finally:
        close_db(db)
