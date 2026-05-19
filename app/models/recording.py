# app/models/recording.py
# 錄音紀錄 Model — 負責 recordings 資料表的 CRUD 操作

import sqlite3


class Recording:
    """錄音紀錄的資料模型。

    對應資料表：recordings
    欄位：id, title, filepath, duration_sec, category, created_at
    """

    def __init__(self, id, title, filepath, duration_sec, category, created_at):
        self.id = id
        self.title = title
        self.filepath = filepath
        self.duration_sec = duration_sec
        self.category = category
        self.created_at = created_at

    @property
    def duration_display(self):
        """將秒數轉換為 HH:MM:SS 格式字串。"""
        hours = self.duration_sec // 3600
        minutes = (self.duration_sec % 3600) // 60
        seconds = self.duration_sec % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def _get_db():
        """取得資料庫連線（由 Flask app context 提供）。"""
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
        """將 Row 轉換為 Recording 實例。"""
        if row is None:
            return None
        return Recording(
            id=row['id'], title=row['title'], filepath=row['filepath'],
            duration_sec=row['duration_sec'], category=row['category'],
            created_at=row['created_at']
        )

    @classmethod
    def create(cls, title, filepath, duration_sec, category=None):
        """新增一筆錄音紀錄，回傳新建的 Recording 物件。"""
        db = cls._get_db()
        cursor = db.execute(
            "INSERT INTO recordings (title, filepath, duration_sec, category) VALUES (?, ?, ?, ?)",
            (title, filepath, duration_sec, category)
        )
        db.commit()
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def get_all(cls):
        """取得所有錄音，依建立時間倒序。"""
        db = cls._get_db()
        rows = db.execute("SELECT * FROM recordings ORDER BY created_at DESC").fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def get_by_id(cls, recording_id):
        """依 ID 取得單一錄音，不存在則回傳 None。"""
        db = cls._get_db()
        row = db.execute("SELECT * FROM recordings WHERE id = ?", (recording_id,)).fetchone()
        return cls._row_to_obj(row)

    @classmethod
    def search(cls, query):
        """依標題或分類搜尋錄音。"""
        db = cls._get_db()
        term = f"%{query}%"
        rows = db.execute(
            "SELECT * FROM recordings WHERE title LIKE ? OR category LIKE ? ORDER BY created_at DESC",
            (term, term)
        ).fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def update(cls, recording_id, title=None, category=None):
        """更新錄音的標題或分類。"""
        db = cls._get_db()
        rec = cls.get_by_id(recording_id)
        if rec is None:
            return None
        new_title = title if title is not None else rec.title
        new_cat = category if category is not None else rec.category
        db.execute("UPDATE recordings SET title = ?, category = ? WHERE id = ?",
                   (new_title, new_cat, recording_id))
        db.commit()
        return cls.get_by_id(recording_id)

    @classmethod
    def delete(cls, recording_id):
        """刪除錄音（標記因 CASCADE 自動刪除）。回傳是否成功。"""
        db = cls._get_db()
        if cls.get_by_id(recording_id) is None:
            return False
        db.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
        db.commit()
        return True

    @classmethod
    def get_marker_count(cls, recording_id):
        """取得某錄音的標記數量。"""
        db = cls._get_db()
        row = db.execute("SELECT COUNT(*) as count FROM markers WHERE recording_id = ?",
                         (recording_id,)).fetchone()
        return row['count'] if row else 0

    def to_dict(self):
        """轉換為字典（供 API JSON 回傳）。"""
        return {
            'id': self.id, 'title': self.title, 'filepath': self.filepath,
            'duration_sec': self.duration_sec, 'duration_display': self.duration_display,
            'category': self.category, 'created_at': self.created_at
        }
