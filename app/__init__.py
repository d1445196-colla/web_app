# app/__init__.py
# Flask 應用程式工廠

import os
from flask import Flask
from config import Config

def create_app(config_class=Config):
    """建立並設定 Flask 應用程式實例。"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 確保 instance 資料夾與上傳資料夾存在
    os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 註冊 Blueprints
    from app.routes.main import main_bp
    from app.routes.recording import recording_bp
    from app.routes.marker import marker_bp
    from app.routes.api import api_bp
    from app.routes.stats import stats_bp
    
    # 繳費提醒與記帳相關（如果有的話，一併註冊）
    try:
        from app.routes.reminder import reminder_bp
        app.register_blueprint(reminder_bp)
    except ImportError:
        pass
        
    try:
        from app.routes.transaction import transaction_bp
        app.register_blueprint(transaction_bp)
    except ImportError:
        pass

    app.register_blueprint(main_bp)
    app.register_blueprint(recording_bp)
    app.register_blueprint(marker_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(stats_bp)

    # 關閉資料庫連線
    @app.teardown_appcontext
    def close_db(error):
        from flask import g
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app
