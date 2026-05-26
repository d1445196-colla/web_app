"""
Recording Model — 錄音紀錄資料表操作

負責 recordings 資料表的 CRUD 方法，管理每一次音訊上傳的
基本資訊與轉寫處理狀態。

資料表欄位：
    id, original_filename, stored_filename, file_path, file_size,
    mime_type, duration, full_text, status, error_message, language,
    created_at, completed_at
"""

import sqlite3
from datetime import datetime


def get_db():
    """
    取得資料庫連線（由 Flask app context 提供）。

    使用 Flask 的 g 物件確保同一次請求中共用同一個連線，
    並啟用外鍵約束、設定 row_factory 讓查詢結果可用欄位名稱取值。

    Returns:
        sqlite3.Connection: 資料庫連線物件
    """
    from flask import current_app, g
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def create(original_filename, stored_filename, file_path, file_size, mime_type):
    """
    建立新的錄音紀錄。

    Args:
        original_filename (str): 使用者上傳的原始檔名
        stored_filename (str): UUID 重新命名後的儲存檔名
        file_path (str): 伺服器端的完整儲存路徑
        file_size (int): 檔案大小 (bytes)
        mime_type (str): 檔案 MIME 類型

    Returns:
        int: 新建立紀錄的 id

    Raises:
        sqlite3.Error: 資料庫寫入失敗時拋出
    """
    try:
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO recordings
                (original_filename, stored_filename, file_path, file_size, mime_type, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
            """,
            (original_filename, stored_filename, file_path, file_size, mime_type)
        )
        db.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"建立錄音紀錄失敗：{e}")


def get_all():
    """
    取得所有錄音紀錄，依建立時間降序排列。

    Returns:
        list[sqlite3.Row]: 所有錄音紀錄列表

    Raises:
        sqlite3.Error: 資料庫查詢失敗時拋出
    """
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM recordings ORDER BY created_at DESC"
        ).fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"查詢所有錄音紀錄失敗：{e}")


def get_by_id(recording_id):
    """
    根據 ID 取得單筆錄音紀錄。

    Args:
        recording_id (int): 錄音紀錄 ID

    Returns:
        sqlite3.Row | None: 錄音紀錄，若不存在則回傳 None

    Raises:
        sqlite3.Error: 資料庫查詢失敗時拋出
    """
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM recordings WHERE id = ?",
            (recording_id,)
        ).fetchone()
        return row
    except sqlite3.Error as e:
        raise Exception(f"查詢錄音紀錄 (id={recording_id}) 失敗：{e}")


def update_status(recording_id, status, error_message=None):
    """
    更新錄音紀錄的處理狀態。

    狀態流轉：pending → processing → completed / failed

    Args:
        recording_id (int): 錄音紀錄 ID
        status (str): 新狀態 ('processing' / 'completed' / 'failed')
        error_message (str | None): 失敗時的錯誤訊息

    Raises:
        sqlite3.Error: 資料庫更新失敗時拋出
    """
    try:
        db = get_db()
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        db.execute(
            """
            UPDATE recordings
            SET status = ?, error_message = ?, completed_at = ?
            WHERE id = ?
            """,
            (status, error_message, completed_at, recording_id)
        )
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"更新錄音紀錄狀態 (id={recording_id}) 失敗：{e}")


def update_transcription(recording_id, full_text, duration=None, language=None):
    """
    更新轉寫結果資訊。

    在 Whisper API 回傳結果後呼叫，將逐字稿全文、
    音訊時長與偵測語言寫入資料庫。

    Args:
        recording_id (int): 錄音紀錄 ID
        full_text (str): Whisper 回傳的完整逐字稿
        duration (float | None): 音訊總時長 (秒)
        language (str | None): Whisper 偵測到的語言代碼 (如 'zh')

    Raises:
        sqlite3.Error: 資料庫更新失敗時拋出
    """
    try:
        db = get_db()
        db.execute(
            """
            UPDATE recordings
            SET full_text = ?, duration = ?, language = ?
            WHERE id = ?
            """,
            (full_text, duration, language, recording_id)
        )
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"更新轉寫結果 (id={recording_id}) 失敗：{e}")


def delete(recording_id):
    """
    刪除指定的錄音紀錄。

    由於 schema 設定了 ON DELETE CASCADE，
    刪除錄音紀錄時會自動級聯刪除相關的 segments 與 markers。

    Args:
        recording_id (int): 錄音紀錄 ID

    Raises:
        sqlite3.Error: 資料庫刪除失敗時拋出
    """
    try:
        db = get_db()
        db.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"刪除錄音紀錄 (id={recording_id}) 失敗：{e}")
