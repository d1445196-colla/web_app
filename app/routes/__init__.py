# app/routes/__init__.py
# 路由套件初始化 — 整合錄音系統與轉寫系統

# 【錄音系統】Blueprint
from app.routes.main import main_bp
from app.routes.recording import recording_bp
from app.routes.marker import marker_bp
from app.routes.api import api_bp
from app.routes.stats import stats_bp

# 【轉寫系統】Blueprint
from app.routes.upload import upload_bp
from app.routes.transcription import transcription_bp

__all__ = [
    'main_bp', 'recording_bp', 'marker_bp', 'api_bp', 'stats_bp',
    'upload_bp', 'transcription_bp',
]
