# app/routes/stats.py
# 統計報表路由

from flask import Blueprint, render_template
from datetime import datetime
from app.models import transaction

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
    months = []
    now = datetime.now()
    
    # 計算最近 6 個月 (包含當月)
    for i in range(5, -1, -1):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
            
        summary = transaction.get_monthly_summary(year, month)
        months.append({
            'label': f'{year}-{month:02d}',
            'income': summary['income'],
            'expense': summary['expense']
        })
        
    return render_template('stats/index.html', monthly_data=months)
