# app/models/__init__.py
# 資料庫模型套件初始化 — 整合錄音系統與轉寫系統

# 【錄音系統】Models
from app.models.recording import Recording
from app.models.marker import Marker
from app.models.marker_type import MarkerType

# 【轉寫系統】Models（以模組方式匯入）
from app.models import transcription
from app.models import transcription_segment
from app.models import transcription_marker

__all__ = [
    'Recording', 'Marker', 'MarkerType',
    'transcription', 'transcription_segment', 'transcription_marker',
]
