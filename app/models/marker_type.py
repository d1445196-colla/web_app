# app/models/marker_type.py
# 標記種類 Model — 負責 marker_types 資料表的 CRUD 操作

import sqlite3


class MarkerType:
    """標記種類的資料模型。

    對應資料表：marker_types
    欄位：id, name, color, icon, is_default, sort_order, created_at
    """

    def __init__(self, id, name, color, icon, is_default, sort_order, created_at):
        self.id = id
        self.name = name
        self.color = color
        self.icon = icon
        self.is_default = is_default
        self.sort_order = sort_order
        self.created_at = created_at

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
        """將 Row 轉換為 MarkerType 實例。"""
        if row is None:
            return None
        return MarkerType(
            id=row['id'], name=row['name'], color=row['color'],
            icon=row['icon'], is_default=row['is_default'],
            sort_order=row['sort_order'], created_at=row['created_at']
        )

    @classmethod
    def create(cls, name, color='#e94560', icon='🏷', is_default=0, sort_order=0):
        """新增一個標記種類。"""
        db = cls._get_db()
        cursor = db.execute(
            "INSERT INTO marker_types (name, color, icon, is_default, sort_order) VALUES (?, ?, ?, ?, ?)",
            (name, color, icon, is_default, sort_order)
        )
        db.commit()
        return cls.get_by_id(cursor.lastrowid)

    @classmethod
    def get_all(cls):
        """取得所有標記種類，依 sort_order 排序。"""
        db = cls._get_db()
        rows = db.execute("SELECT * FROM marker_types ORDER BY sort_order ASC").fetchall()
        return [cls._row_to_obj(row) for row in rows]

    @classmethod
    def get_by_id(cls, type_id):
        """依 ID 取得單一標記種類。"""
        db = cls._get_db()
        row = db.execute("SELECT * FROM marker_types WHERE id = ?", (type_id,)).fetchone()
        return cls._row_to_obj(row)

    @classmethod
    def update(cls, type_id, name=None, color=None, icon=None, sort_order=None):
        """更新標記種類的屬性。"""
        db = cls._get_db()
        mt = cls.get_by_id(type_id)
        if mt is None:
            return None
        new_name = name if name is not None else mt.name
        new_color = color if color is not None else mt.color
        new_icon = icon if icon is not None else mt.icon
        new_order = sort_order if sort_order is not None else mt.sort_order
        db.execute(
            "UPDATE marker_types SET name = ?, color = ?, icon = ?, sort_order = ? WHERE id = ?",
            (new_name, new_color, new_icon, new_order, type_id)
        )
        db.commit()
        return cls.get_by_id(type_id)

    @classmethod
    def delete(cls, type_id):
        """刪除標記種類。若仍有標記引用此種類，會因 RESTRICT 約束失敗。

        Returns:
            True 刪除成功，False 找不到或刪除失敗
        """
        db = cls._get_db()
        if cls.get_by_id(type_id) is None:
            return False
        try:
            db.execute("DELETE FROM marker_types WHERE id = ?", (type_id,))
            db.commit()
            return True
        except sqlite3.IntegrityError:
            # 仍有標記引用此種類，無法刪除
            return False

    @classmethod
    def get_usage_count(cls, type_id):
        """取得某標記種類被使用的次數。"""
        db = cls._get_db()
        row = db.execute(
            "SELECT COUNT(*) as count FROM markers WHERE type_id = ?", (type_id,)
        ).fetchone()
        return row['count'] if row else 0

    def to_dict(self):
        """轉換為字典（供 API JSON 回傳）。"""
        return {
            'id': self.id, 'name': self.name, 'color': self.color,
            'icon': self.icon, 'is_default': bool(self.is_default),
            'sort_order': self.sort_order, 'created_at': self.created_at
        }
