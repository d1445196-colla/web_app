"""
Segment Model — 轉寫段落資料表操作

負責 segments 資料表的 CRUD 方法，管理 Whisper API 回傳的
每一個句子段落（含起止時間與文字內容）。

資料表欄位：
    id, recording_id, segment_index, start_time, end_time, text
"""

import sqlite3


def get_db():
    """
    取得資料庫連線（由 Flask app context 提供）。

    Returns:
        sqlite3.Connection: 資料庫連線物件
    """
    from flask import current_app, g
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def bulk_create(recording_id, segments):
    """
    批次寫入多筆轉寫段落。

    將 Whisper API 回傳的 segments 陣列一次性寫入資料庫，
    使用 executemany 提升批次寫入效能。

    Args:
        recording_id (int): 所屬錄音紀錄 ID
        segments (list[dict]): 段落列表，每筆包含：
            - segment_index (int): 段落順序索引（從 0 開始）
            - start_time (float): 起始時間 (秒)
            - end_time (float): 結束時間 (秒)
            - text (str): 轉寫文字

    Returns:
        int: 成功寫入的筆數

    Raises:
        Exception: 資料庫寫入失敗時拋出
    """
    try:
        db = get_db()
        data = [
            (recording_id, seg['segment_index'], seg['start_time'], seg['end_time'], seg['text'])
            for seg in segments
        ]
        db.executemany(
            """
            INSERT INTO segments (recording_id, segment_index, start_time, end_time, text)
            VALUES (?, ?, ?, ?, ?)
            """,
            data
        )
        db.commit()
        return len(data)
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"批次寫入轉寫段落失敗：{e}")


def get_by_recording_id(recording_id):
    """
    取得指定錄音紀錄的所有轉寫段落，依順序索引排列。

    Args:
        recording_id (int): 錄音紀錄 ID

    Returns:
        list[sqlite3.Row]: 該錄音的所有轉寫段落

    Raises:
        Exception: 資料庫查詢失敗時拋出
    """
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM segments WHERE recording_id = ? ORDER BY segment_index ASC",
            (recording_id,)
        ).fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫段落 (recording_id={recording_id}) 失敗：{e}")


def get_by_id(segment_id):
    """
    根據 ID 取得單筆轉寫段落。

    Args:
        segment_id (int): 轉寫段落 ID

    Returns:
        sqlite3.Row | None: 轉寫段落，若不存在則回傳 None

    Raises:
        Exception: 資料庫查詢失敗時拋出
    """
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM segments WHERE id = ?",
            (segment_id,)
        ).fetchone()
        return row
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫段落 (id={segment_id}) 失敗：{e}")


def delete_by_recording_id(recording_id):
    """
    刪除指定錄音紀錄的所有轉寫段落。

    注意：通常不需要手動呼叫此方法，因為 schema 已設定
    ON DELETE CASCADE，刪除 recording 時會自動級聯刪除。

    Args:
        recording_id (int): 錄音紀錄 ID

    Raises:
        Exception: 資料庫刪除失敗時拋出
    """
    try:
        db = get_db()
        db.execute("DELETE FROM segments WHERE recording_id = ?", (recording_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"刪除轉寫段落 (recording_id={recording_id}) 失敗：{e}")
