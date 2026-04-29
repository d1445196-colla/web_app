"""
app/routes/main.py
首頁儀表板路由

Blueprint: main_bp
負責首頁的餘額統計、即將到期帳單、近期交易顯示。
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    首頁儀表板

    GET /

    處理邏輯：
    1. 呼叫 transaction.get_balance() 取得總餘額
    2. 呼叫 transaction.get_monthly_summary(year, month) 取得本月收支
    3. 呼叫 transaction.get_recent_transactions(5) 取得近期 5 筆交易
    4. 呼叫 reminder.get_upcoming_reminders(7) 取得 7 天內到期帳單

    輸出：渲染 index.html
    """
    pass
