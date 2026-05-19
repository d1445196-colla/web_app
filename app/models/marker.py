# app/models/marker.py
# 標記 Model — 負責 markers 資料表的 CRUD 操作

import sqlite3


class Marker:
    """標記的資料模型。

    對應資料表：markers
    欄位：id, recording_id, type_id, timestamp_sec, note, created_at
    """

    def __init__(self, id, recording_id, type_id, timestamp_sec, note, created_at):
        self.id = id
        self.recording_id = recording_id
        self.type_id = type_id
        self.timestamp_sec = timestamp_sec
        self.note = note
        self.created_at = created_at

    @property
    def timestamp_display(self):
        """將秒數轉換為 MM:SS 或 HH:MM:SS 格式。"""
        hours = self.timestamp_sec // 3600
        minutes = (self.timestamp_sec % 3600) // 60
        seconds = self.timestamp_sec % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def _get_db():
        """取得資料庫連線。"""
        from flask import current_app, g
        if 'db' not in g:
            g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @staticmethod
    def _row_to_obj(row):
        """將 Row 轉換為 Marker 實例。"""
        if row is None:
            return None
        return Marker(
            id=row['id'], recording_id=row['recording_id'],
            type_id=row['type_id'], timestamp_sec=row['timestamp_sec'],
            note=row['note'], created_at=row['created_at']
        )

    @classmethod
    def create(cls, recording_id, type_id, timestamp_sec, note=None):
        """新增一筆標記。"""
        db = cls._get_db()
        cursor = db.execute(
            "INSERT INTO markers (recording_id, type_id, timestamp_sec, note) VALUES (?, ?, ?, ?)",
            (recording_id, type_id, timestamp_sec, note)
        )
        db.commit()
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def create_batch(cls, recording_id, markers_list):
        """批次新增多筆標記。

        Args:
            recording_id: 所屬錄音 ID
            markers_list: 標記清單，每個元素為 dict，包含 type_id, timestamp_sec, note

        Returns:
            新建立的 Marker 物件列表
        """
        db = cls._get_db()
        created = []
        for m in markers_list:
            cursor = db.execute(
                "INSERT INTO markers (recording_id, type_id, timestamp_sec, note) VALUES (?, ?, ?, ?)",
                (recording_id, m.get('type_id'), m.get('timestamp_sec'), m.get('note'))
            )
            created.append(cursor.lastrowid)
        db.commit()
        return [cls.get_by_id(mid) for mid in created]

    @classmethod
    def get_by_id(cls, marker_id):
        """依 ID 取得單一標記。"""
        db = cls._get_db()
        row = db.execute("SELECT * FROM markers WHERE id = ?", (marker_id,)).fetchone()
        return cls._row_to_obj(row)

    @classmethod
    def get_by_recording(cls, recording_id):
        """取得某錄音的所有標記，依時間戳排序。"""
        db = cls._get_db()
        rows = db.execute(
            "SELECT * FROM markers WHERE recording_id = ? ORDER BY timestamp_sec ASC",
            (recording_id,)
        ).fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def get_by_recording_and_type(cls, recording_id, type_id):
        """取得某錄音中特定種類的標記。"""
        db = cls._get_db()
        rows = db.execute(
            "SELECT * FROM markers WHERE recording_id = ? AND type_id = ? ORDER BY timestamp_sec ASC",
            (recording_id, type_id)
        ).fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def update(cls, marker_id, note=None):
        """更新標記的備註。"""
        db = cls._get_db()
        marker = cls.get_by_id(marker_id)
        if marker is None:
            return None
        new_note = note if note is not None else marker.note
        db.execute("UPDATE markers SET note = ? WHERE id = ?", (new_note, marker_id))
        db.commit()
        return cls.get_by_id(marker_id)

    @classmethod
    def delete(cls, marker_id):
        """刪除單一標記。回傳是否成功。"""
        db = cls._get_db()
        if cls.get_by_id(marker_id) is None:
            return False
        db.execute("DELETE FROM markers WHERE id = ?", (marker_id,))
        db.commit()
        return True

    @classmethod
    def delete_by_recording(cls, recording_id):
        """刪除某錄音的所有標記。"""
        db = cls._get_db()
        db.execute("DELETE FROM markers WHERE recording_id = ?", (recording_id,))
        db.commit()

    def to_dict(self):
        """轉換為字典（供 API JSON 回傳）。"""
        return {
            'id': self.id, 'recording_id': self.recording_id,
            'type_id': self.type_id, 'timestamp_sec': self.timestamp_sec,
            'timestamp_display': self.timestamp_display,
            'note': self.note, 'created_at': self.created_at
        }
