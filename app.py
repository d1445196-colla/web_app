"""
語音轉寫與 API 整合系統 — 應用程式啟動入口

使用方式：
    flask run
    或
    python app.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
