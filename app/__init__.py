"""
語音轉寫與 API 整合系統 — Flask 應用程式初始化

負責建立 Flask app 實例、載入設定、註冊 Blueprint、
初始化資料庫連線與關閉機制。
"""

import os
import sqlite3
from flask import Flask, g
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()


def create_app():
    """
    Flask Application Factory。

    建立並設定 Flask app 實例，註冊所有 Blueprint，
    設定資料庫連線的生命週期管理。
    """
    app = Flask(__name__, instance_relative_config=True)

    # --- 基本設定 ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['DATABASE'] = os.path.join(app.instance_path, 'database.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25MB 上限
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')

    # --- 確保 instance 與 uploads 資料夾存在 ---
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # --- 資料庫連線管理 ---
    @app.teardown_appcontext
    def close_db(exception):
        """請求結束時自動關閉資料庫連線。"""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # --- 註冊路由 Blueprint ---
    from app.routes import register_routes
    register_routes(app)

    return app


def init_db():
    """
    初始化資料庫：讀取 schema.sql 並執行建表語法。

    使用方式：
        python -c "from app import init_db; init_db()"
    """
    app = create_app()
    with app.app_context():
        db = sqlite3.connect(app.config['DATABASE'])
        db.execute("PRAGMA foreign_keys = ON")

        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql'
        )
        with open(schema_path, 'r', encoding='utf-8') as f:
            db.executescript(f.read())

        db.close()
        print(f"✅ 資料庫已初始化：{app.config['DATABASE']}")
