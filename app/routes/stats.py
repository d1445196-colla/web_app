"""
app/routes/stats.py
統計報表路由

Blueprint: stats_bp
負責收支趨勢圖表與統計資料。
"""

from flask import Blueprint, render_template

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/stats')
def index():
    """
    統計報表頁面

    GET /stats

    處理邏輯：
    1. 取得最近 6 個月的月份列表
    2. 對每個月呼叫 transaction.get_monthly_summary(year, month)
    3. 組合成圖表所需的資料格式（月份標籤、收入陣列、支出陣列）

    輸出：渲染 stats/index.html，傳入 monthly_data
    """
    pass
