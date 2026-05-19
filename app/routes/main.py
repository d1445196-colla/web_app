# app/routes/main.py
# 主頁路由 Blueprint — 錄音主頁面

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """錄音主頁面。

    顯示錄音核心介面，包含：
    - 即時音量波形視覺化（Canvas）
    - 錄音計時器（HH:MM:SS）
    - 標記按鈕區（依 MarkerType 動態產生）
    - 錄音控制按鈕（開始 / 暫停 / 停止）

    處理邏輯：
        1. MarkerType.get_all() 取得所有標記種類
        2. 渲染 index.html，傳入標記種類清單

    Template: templates/index.html
    """
    # TODO: 實作
    pass
