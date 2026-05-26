# app/routes/__init__.py
"""
路由套件初始化 — 註冊所有 Blueprint。

在 Flask app 初始化時呼叫 register_routes(app) 即可
將所有路由 Blueprint 註冊到應用程式上。
"""


def register_routes(app):
    """將所有 Blueprint 註冊到 Flask app。"""
    from .upload import upload_bp
    from .transcription import transcription_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(transcription_bp)
