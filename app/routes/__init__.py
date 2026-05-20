# app/routes/__init__.py
# 路由套件初始化

from app.routes.main import main_bp
from app.routes.recording import recording_bp
from app.routes.marker import marker_bp
from app.routes.api import api_bp
from app.routes.stats import stats_bp

__all__ = ['main_bp', 'recording_bp', 'marker_bp', 'api_bp', 'stats_bp']
