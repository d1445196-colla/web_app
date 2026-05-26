"""
Marker Model — 即時標記資料表操作

負責 markers 資料表的 CRUD 方法，管理前端錄音時使用者按下的
即時標記時間點，以及與轉寫段落的對齊關聯。

資料表欄位：
    id, recording_id, segment_id, marker_time, label, created_at
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


def bulk_create(recording_id, markers):
    """
    批次寫入多筆即時標記。

    前端錄音時產生的 Markers 隨音訊一起上傳，
    經過時間軸對齊後批次寫入資料庫。

    Args:
        recording_id (int): 所屬錄音紀錄 ID
        markers (list[dict]): 標記列表，每筆包含：
            - marker_time (float): 標記的時間點 (秒)
            - label (str): 標記備註文字（可選，預設空字串）
            - segment_id (int | None): 對齊到的段落 ID（可選）

    Returns:
        int: 成功寫入的筆數

    Raises:
        Exception: 資料庫寫入失敗時拋出
    """
    try:
        db = get_db()
        data = [
            (
                recording_id,
                m.get('segment_id'),
                m['marker_time'],
                m.get('label', '')
            )
            for m in markers
        ]
        db.executemany(
            """
            INSERT INTO markers (recording_id, segment_id, marker_time, label)
            VALUES (?, ?, ?, ?)
            """,
            data
        )
        db.commit()
        return len(data)
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"批次寫入即時標記失敗：{e}")


def get_by_recording_id(recording_id):
    """
    取得指定錄音紀錄的所有即時標記，依時間點升序排列。

    Args:
        recording_id (int): 錄音紀錄 ID

    Returns:
        list[sqlite3.Row]: 該錄音的所有即時標記

    Raises:
        Exception: 資料庫查詢失敗時拋出
    """
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM markers WHERE recording_id = ? ORDER BY marker_time ASC",
            (recording_id,)
        ).fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"查詢即時標記 (recording_id={recording_id}) 失敗：{e}")


def get_by_id(marker_id):
    """
    根據 ID 取得單筆標記。

    Args:
        marker_id (int): 標記 ID

    Returns:
        sqlite3.Row | None: 標記資料，若不存在則回傳 None

    Raises:
        Exception: 資料庫查詢失敗時拋出
    """
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM markers WHERE id = ?",
            (marker_id,)
        ).fetchone()
        return row
    except sqlite3.Error as e:
        raise Exception(f"查詢即時標記 (id={marker_id}) 失敗：{e}")


def update_segment_alignment(marker_id, segment_id):
    """
    更新標記的段落對齊結果。

    在時間軸對齊完成後，將每個 Marker 對應到的
    Segment ID 寫回資料庫。

    Args:
        marker_id (int): 標記 ID
        segment_id (int | None): 對齊到的段落 ID（若未對齊到任何段落則為 None）

    Raises:
        Exception: 資料庫更新失敗時拋出
    """
    try:
        db = get_db()
        db.execute(
            "UPDATE markers SET segment_id = ? WHERE id = ?",
            (segment_id, marker_id)
        )
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"更新標記對齊結果 (id={marker_id}) 失敗：{e}")


def delete_by_recording_id(recording_id):
    """
    刪除指定錄音紀錄的所有即時標記。

    注意：通常不需要手動呼叫此方法，因為 schema 已設定
    ON DELETE CASCADE，刪除 recording 時會自動級聯刪除。

    Args:
        recording_id (int): 錄音紀錄 ID

    Raises:
        Exception: 資料庫刪除失敗時拋出
    """
    try:
        db = get_db()
        db.execute("DELETE FROM markers WHERE recording_id = ?", (recording_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"刪除即時標記 (recording_id={recording_id}) 失敗：{e}")
