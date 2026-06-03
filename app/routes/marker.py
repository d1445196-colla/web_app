# app/routes/marker.py
# 標記路由 Blueprint — 標記 CRUD + 標記種類管理

from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app
from app.models.marker import Marker
from app.models.marker_type import MarkerType

marker_bp = Blueprint('marker', __name__)


# ============================================
# 標記 CRUD
# ============================================

@marker_bp.route('/markers/<int:id>/update', methods=['POST'])
def update_marker(id):
    """更新標記備註。

    輸入：
        - URL 參數 id（標記 ID）
        - request.form['note']：新備註

    輸出：重導向至 /recordings/<recording_id>
    """
    marker = Marker.get_by_id(id)
    if marker is None:
        flash('找不到該筆標記，無法更新。', 'error')
        return redirect(url_for('recording.list_recordings'))
        
    note = request.form.get('note', '').strip()
    
    try:
        Marker.update(id, note=note)
        flash('標記備註已更新。', 'success')
    except Exception as e:
        current_app.logger.error(f"更新標記備註失敗: {e}")
        flash('更新標記備註時發生錯誤。', 'error')
        
    return redirect(url_for('recording.detail', id=marker.recording_id))


@marker_bp.route('/markers/<int:id>/delete', methods=['POST'])
def delete_marker(id):
    """刪除單一標記。

    輸入：URL 參數 id（標記 ID）

    輸出：重導向至 /recordings/<recording_id>
    """
    marker = Marker.get_by_id(id)
    if marker is None:
        flash('找不到該筆標記，無法刪除。', 'error')
        return redirect(url_for('recording.list_recordings'))
        
    try:
        Marker.delete(id)
        flash('標記已刪除。', 'success')
    except Exception as e:
        current_app.logger.error(f"刪除標記失敗: {e}")
        flash('刪除標記時發生錯誤。', 'error')
        
    return redirect(url_for('recording.detail', id=marker.recording_id))


# ============================================
# 標記種類管理
# ============================================

@marker_bp.route('/settings/markers', methods=['GET'])
def list_marker_types():
    """標記種類列表頁面。

    顯示所有標記種類，支援新增 / 編輯 / 刪除。
    """
    marker_types = MarkerType.get_all()
    
    # 為每個種類取得使用次數
    for mt in marker_types:
        mt.usage_count = MarkerType.get_usage_count(mt.id)
        
    return render_template('settings/marker_types.html', marker_types=marker_types)


@marker_bp.route('/settings/markers', methods=['POST'])
def create_marker_type():
    """新增標記種類。

    輸入：
        - request.form['name']：種類名稱
        - request.form['color']：顏色 HEX
        - request.form['icon']：圖示 Emoji
    """
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#e94560').strip()
    icon = request.form.get('icon', '🏷').strip()
    
    if not name:
        flash('標記種類名稱不得為空。', 'error')
        return redirect(url_for('marker.list_marker_types'))
        
    try:
        MarkerType.create(name=name, color=color, icon=icon)
        flash(f'已成功新增標記種類「{name}」。', 'success')
    except Exception as e:
        current_app.logger.error(f"建立標記種類失敗: {e}")
        flash('新增標記種類時發生錯誤。', 'error')
        
    return redirect(url_for('marker.list_marker_types'))


@marker_bp.route('/settings/markers/<int:id>/update', methods=['POST'])
def update_marker_type(id):
    """更新標記種類。

    輸入：
        - URL 參數 id
        - request.form['name']、request.form['color']、request.form['icon']
    """
    mt = MarkerType.get_by_id(id)
    if mt is None:
        flash('找不到該筆標記種類。', 'error')
        return redirect(url_for('marker.list_marker_types'))
        
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '').strip()
    icon = request.form.get('icon', '').strip()
    
    if not name:
        flash('標記種類名稱不得為空。', 'error')
        return redirect(url_for('marker.list_marker_types'))
        
    try:
        MarkerType.update(id, name=name, color=color, icon=icon)
        flash('標記種類已更新。', 'success')
    except Exception as e:
        current_app.logger.error(f"更新標記種類失敗: {e}")
        flash('更新標記種類時發生錯誤。', 'error')
        
    return redirect(url_for('marker.list_marker_types'))


@marker_bp.route('/settings/markers/<int:id>/delete', methods=['POST'])
def delete_marker_type(id):
    """刪除標記種類。

    輸入：URL 參數 id
    """
    mt = MarkerType.get_by_id(id)
    if mt is None:
        flash('找不到該標記種類，無法刪除。', 'error')
        return redirect(url_for('marker.list_marker_types'))
        
    try:
        success = MarkerType.delete(id)
        if success:
            flash(f'標記種類「{mt.name}」已刪除。', 'success')
        else:
            flash(f'刪除失敗！該標記種類「{mt.name}」已被部分錄音的標記引用，無法刪除。', 'error')
    except Exception as e:
        current_app.logger.error(f"刪除標記種類錯誤: {e}")
        flash('刪除標記種類時發生資料庫錯誤。', 'error')
        
    return redirect(url_for('marker.list_marker_types'))
