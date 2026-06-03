# config.py
# 系統設定檔

import os

class Config:
    # Flask Session Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-recording-secret-key-12345'
    
    # 專案根目錄
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLite 資料庫檔案路徑
    DATABASE = os.path.join(BASE_DIR, 'instance', 'database.db')
    
    # 錄音檔案上傳儲存目錄
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    
    # 限制上傳最大容量 (100MB)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
