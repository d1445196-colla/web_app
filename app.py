# app.py
# 應用程式啟動入口

import os
from app import create_app
from app.models.database import init_db

app = create_app()

@app.cli.command("init-db")
def init_db_command():
    """初始化資料庫（建立資料表與預設資料）。"""
    init_db()
    print("Database initialized successfully.")

# 當直接執行 python app.py 時
if __name__ == '__main__':
    # 如果資料庫檔案不存在，自動進行初始化
    if not os.path.exists(app.config['DATABASE']):
        with app.app_context():
            init_db()
    
    # 啟動 Flask 開發伺服器
    app.run(host='127.0.0.1', port=5000, debug=True)
