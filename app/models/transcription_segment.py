"""
TranscriptionSegment Model — 轉寫段落資料表操作

負責 transcription_segments 資料表的 CRUD 方法。
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


def bulk_create(transcription_id, segments):
    """批次寫入多筆轉寫段落。"""
    try:
        db = get_db()
        data = [
            (transcription_id, seg['segment_index'], seg['start_time'], seg['end_time'], seg['text'])
            for seg in segments
        ]
        db.executemany(
            """
            INSERT INTO transcription_segments (transcription_id, segment_index, start_time, end_time, text)
            VALUES (?, ?, ?, ?, ?)
            """,
            data
        )
        db.commit()
        return len(data)
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"批次寫入轉寫段落失敗：{e}")


def get_by_transcription_id(transcription_id):
    """取得指定轉寫紀錄的所有段落，依順序索引排列。"""
    try:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM transcription_segments WHERE transcription_id = ? ORDER BY segment_index ASC",
            (transcription_id,)
        ).fetchall()
        return rows
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫段落 (transcription_id={transcription_id}) 失敗：{e}")


def get_by_id(segment_id):
    """根據 ID 取得單筆轉寫段落。"""
    try:
        db = get_db()
        row = db.execute(
            "SELECT * FROM transcription_segments WHERE id = ?",
            (segment_id,)
        ).fetchone()
        return row
    except sqlite3.Error as e:
        raise Exception(f"查詢轉寫段落 (id={segment_id}) 失敗：{e}")


def delete_by_transcription_id(transcription_id):
    """刪除指定轉寫紀錄的所有段落。"""
    try:
        db = get_db()
        db.execute("DELETE FROM transcription_segments WHERE transcription_id = ?", (transcription_id,))
        db.commit()
    except sqlite3.Error as e:
        db.rollback()
        raise Exception(f"刪除轉寫段落 (transcription_id={transcription_id}) 失敗：{e}")
