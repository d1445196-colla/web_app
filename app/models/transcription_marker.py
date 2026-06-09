"""
TranscriptionMarker Model — 轉寫標記資料表操作

負責 transcription_markers 資料表的 CRUD 方法。
"""

import sqlite3


def get_db():
    """取得資料庫連線。"""
    from flask import current_app, g
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def bulk_create(transcription_id, markers):
    """批次寫入多筆轉寫標記。"""
    try:
        db = get_db()
        data = [
            (transcription_id, m.get('segment_id'), m['marker_time'], m.get('label', ''))
            for m in markers
        ]
        db.executemany(
            """
            INSERT INTO transcription_markers (transcription_id, segment_id, marker_time, label)
            VALUES (?, ?, ?, ?)
            """,
            data
        )
        db.commit()
        return len(data)
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"批次寫入轉寫標記失敗：{e}")


def get_by_transcription_id(transcription_id):
    """取得指定轉寫紀錄的所有標記，依時間點升序排列。"""
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM transcription_markers WHERE transcription_id = ? ORDER BY marker_time ASC",
            (transcription_id,)
        ).fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫標記 (transcription_id={transcription_id}) 失敗：{e}")


def get_by_id(marker_id):
    """根據 ID 取得單筆標記。"""
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM transcription_markers WHERE id = ?",
            (marker_id,)
        ).fetchone()
        return row
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫標記 (id={marker_id}) 失敗：{e}")


def update_segment_alignment(marker_id, segment_id):
    """更新標記的段落對齊結果。"""
    try:
        db = get_db()
        db.execute(
            "UPDATE transcription_markers SET segment_id = ? WHERE id = ?",
            (segment_id, marker_id)
        )
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"更新標記對齊結果 (id={marker_id}) 失敗：{e}")


def delete_by_transcription_id(transcription_id):
    """刪除指定轉寫紀錄的所有標記。"""
    try:
        db = get_db()
        db.execute("DELETE FROM transcription_markers WHERE transcription_id = ?", (transcription_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"刪除轉寫標記 (transcription_id={transcription_id}) 失敗：{e}")
