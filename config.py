# config.py
# 應用程式設定 — 集中管理所有設定值

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Flask 應用程式設定。"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DATABASE = os.path.join(BASE_DIR, 'instance', 'database.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB 上限
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
