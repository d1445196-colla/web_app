# app/routes/__init__.py
"""
路由套件初始化 — 整合錄音系統與轉寫系統的所有 Blueprint。
"""


def register_routes(app):
    """將所有 Blueprint 註冊到 Flask app。"""
    # 【錄音系統】Blueprint
    from app.routes.main import main_bp
    from app.routes.recording import recording_bp
    from app.routes.marker import marker_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(recording_bp)
    app.register_blueprint(marker_bp)
    app.register_blueprint(api_bp)

    # 【轉寫系統】Blueprint
    from app.routes.upload import upload_bp
    from app.routes.transcription import transcription_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(transcription_bp)
