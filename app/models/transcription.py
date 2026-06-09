"""
Transcription Model — 轉寫紀錄資料表操作

負責 transcriptions 資料表的 CRUD 方法，管理每一次音訊上傳的
基本資訊與轉寫處理狀態。

資料表欄位：
    id, original_filename, stored_filename, file_path, file_size,
    mime_type, duration, full_text, status, error_message, language,
    created_at, completed_at
"""

import sqlite3
from datetime import datetime


def get_db():
    """取得資料庫連線（由 Flask app context 提供）。"""
    from flask import current_app, g
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def create(original_filename, stored_filename, file_path, file_size, mime_type):
    """建立新的轉寫紀錄，回傳新建立紀錄的 id。"""
    try:
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO transcriptions
                (original_filename, stored_filename, file_path, file_size, mime_type, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
            """,
            (original_filename, stored_filename, file_path, file_size, mime_type)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"建立轉寫紀錄失敗：{e}")


def get_all():
    """取得所有轉寫紀錄，依建立時間降序排列。"""
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM transcriptions ORDER BY created_at DESC"
        ).fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"查詢所有轉寫紀錄失敗：{e}")


def get_by_id(transcription_id):
    """根據 ID 取得單筆轉寫紀錄。"""
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM transcriptions WHERE id = ?",
            (transcription_id,)
        ).fetchone()
        return row
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫紀錄 (id={transcription_id}) 失敗：{e}")


def update_status(transcription_id, status, error_message=None):
    """更新轉寫紀錄的處理狀態。"""
    try:
        db = get_db()
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        db.execute(
            """
            UPDATE transcriptions
            SET status = ?, error_message = ?, completed_at = ?
            WHERE id = ?
            """,
            (status, error_message, completed_at, transcription_id)
        )
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"更新轉寫紀錄狀態 (id={transcription_id}) 失敗：{e}")


def update_transcription(transcription_id, full_text, duration=None, language=None):
    """更新轉寫結果資訊（逐字稿全文、時長、語言）。"""
    try:
        db = get_db()
        db.execute(
            """
            UPDATE transcriptions
            SET full_text = ?, duration = ?, language = ?
            WHERE id = ?
            """,
            (full_text, duration, language, transcription_id)
        )
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"更新轉寫結果 (id={transcription_id}) 失敗：{e}")


def delete(transcription_id):
    """刪除指定的轉寫紀錄（級聯刪除 segments 與 markers）。"""
    try:
        db = get_db()
        db.execute("DELETE FROM transcriptions WHERE id = ?", (transcription_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"刪除轉寫紀錄 (id={transcription_id}) 失敗：{e}")
