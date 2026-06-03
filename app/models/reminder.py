"""
app/models/reminder.py
繳費提醒 Model

負責 reminders 資料表的 CRUD 操作。
管理每月定期帳單的提醒設定。
"""

from datetime import datetime, date
from app.models.database import get_db, close_db


def create_reminder(name, amount, due_day, note=''):
    """
    新增一個繳費提醒。

    參數：
        name (str): 帳單名稱
        amount (float): 應繳金額
        due_day (int): 每月到期日（1–31）
        note (str): 備註（選填）

    回傳：
        int: 新建提醒的 ID
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.execute(
            '''INSERT INTO reminders (name, amount, due_day, is_paid, note, created_at, updated_at)
               VALUES (?, ?, ?, 'no', ?, ?, ?)''',
            (name, amount, due_day, note, now, now)
        )
        db.commit()
        return cursor.lastrowid
    finally:
        close_db(db)


def get_all_reminders():
    """
    取得所有繳費提醒（依到期日排序）。

    回傳：
        list[sqlite3.Row]: 提醒列表
    """
    db = get_db()
    try:
        rows = db.execute(
            'SELECT * FROM reminders ORDER BY due_day ASC'
        ).fetchall()
        return rows
    finally:
        close_db(db)


def get_reminder_by_id(reminder_id):
    """
    根據 ID 取得單一提醒。

    參數：
        reminder_id (int): 提醒 ID

    回傳：
        sqlite3.Row 或 None
    """
    db = get_db()
    try:
        row = db.execute(
            'SELECT * FROM reminders WHERE id = ?',
            (reminder_id,)
        ).fetchone()
        return row
    finally:
        close_db(db)


def update_reminder(reminder_id, name, amount, due_day, note=''):
    """
    更新繳費提醒。

    參數：
        reminder_id (int): 提醒 ID
        name (str): 帳單名稱
        amount (float): 應繳金額
        due_day (int): 每月到期日
        note (str): 備註
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            '''UPDATE reminders
               SET name = ?, amount = ?, due_day = ?, note = ?, updated_at = ?
               WHERE id = ?''',
            (name, amount, due_day, note, now, reminder_id)
        )
        db.commit()
    finally:
        close_db(db)


def delete_reminder(reminder_id):
    """
    刪除繳費提醒。

    參數：
        reminder_id (int): 提醒 ID
    """
    db = get_db()
    try:
        db.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
        db.commit()
    finally:
        close_db(db)


def mark_as_paid(reminder_id):
    """
    標記提醒為已繳費。

    參數：
        reminder_id (int): 提醒 ID
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        today = date.today().strftime('%Y-%m-%d')
        db.execute(
            '''UPDATE reminders
               SET is_paid = 'yes', paid_date = ?, updated_at = ?
               WHERE id = ?''',
            (today, now, reminder_id)
        )
        db.commit()
    finally:
        close_db(db)


def mark_as_unpaid(reminder_id):
    """
    標記提醒為未繳費（重置狀態）。

    參數：
        reminder_id (int): 提醒 ID
    """
    db = get_db()
    try:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            '''UPDATE reminders
               SET is_paid = 'no', paid_date = NULL, updated_at = ?
               WHERE id = ?''',
            (now, reminder_id)
        )
        db.commit()
    finally:
        close_db(db)


def get_upcoming_reminders(days=7):
    """
    取得即將到期的未繳帳單（到期日在今天起 N 天內）。

    參數：
        days (int): 提前幾天提醒，預設 7 天

    回傳：
        list[sqlite3.Row]: 即將到期的未繳提醒列表
    """
    db = get_db()
    try:
        today = date.today()
        current_day = today.day

        # 計算 N 天後的日期
        target_day = current_day + days

        if target_day <= 31:
            # 同一個月內
            rows = db.execute(
                '''SELECT * FROM reminders
                   WHERE is_paid = 'no'
                   AND due_day BETWEEN ? AND ?
                   ORDER BY due_day ASC''',
                (current_day, target_day)
            ).fetchall()
        else:
            # 跨月（到期日在本月底或下月初）
            rows = db.execute(
                '''SELECT * FROM reminders
                   WHERE is_paid = 'no'
                   AND (due_day >= ? OR due_day <= ?)
                   ORDER BY due_day ASC''',
                (current_day, target_day - 31)
            ).fetchall()

        return rows
    finally:
        close_db(db)
