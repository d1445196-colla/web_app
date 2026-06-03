# app/routes/marker.py
# 標記路由 Blueprint — 標記 CRUD + 標記種類管理

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from app.models.marker import Marker
from app.models.marker_type import MarkerType

marker_bp = Blueprint('marker', __name__)


# ============================================
# 標記 CRUD
# ============================================

@marker_bp.route('/markers/<int:id>/update', methods=['POST'])
def update_marker(id):
    """更新標記備註。
    """
    marker = Marker.get_by_id(id)
    if marker is None:
        abort(404)

    note = request.form.get('note', '').strip()
    Marker.update(id, note=note)
    flash('[OK] 標記備註已更新', 'success')
    return redirect(url_for('recording.detail', id=marker.recording_id))


@marker_bp.route('/markers/<int:id>/delete', methods=['POST'])
def delete_marker(id):
    """刪除單一標記。
    """
    marker = Marker.get_by_id(id)
    if marker is None:
        abort(404)

    recording_id = marker.recording_id
    Marker.delete(id)
    flash('[OK] 標記已刪除', 'success')
    return redirect(url_for('recording.detail', id=recording_id))


# ============================================
# 標記種類管理
# ============================================

@marker_bp.route('/settings/markers', methods=['GET'])
def list_marker_types():
    """標記種類列表頁面。
    """
    marker_types = MarkerType.get_all()
    # Build list of dicts with 'type' and 'usage_count' keys
    marker_types_data = []
    for mt in marker_types:
        usage = MarkerType.get_usage_count(mt.id)
        marker_types_data.append({
            'type': mt,
            'usage_count': usage
        })

    return render_template('settings/marker_types.html', marker_types=marker_types_data)


@marker_bp.route('/settings/markers', methods=['POST'])
def create_marker_type():
    """新增標記種類。
    """
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#e94560').strip()
    icon = request.form.get('icon', '🏷').strip()

    if not name:
        flash('[ERROR] 名稱不可為空', 'danger')
        return redirect(url_for('marker.list_marker_types'))

    MarkerType.create(name=name, color=color, icon=icon)
    flash('[OK] 標記種類已建立', 'success')
    return redirect(url_for('marker.list_marker_types'))


@marker_bp.route('/settings/markers/<int:id>/update', methods=['POST'])
def update_marker_type(id):
    """更新標記種類。
    """
    mt = MarkerType.get_by_id(id)
    if mt is None:
        abort(404)

    name = request.form.get('name', '').strip()
    color = request.form.get('color', '').strip()
    icon = request.form.get('icon', '').strip()

    if not name:
        flash('[ERROR] 名稱不可為空', 'danger')
        return redirect(url_for('marker.list_marker_types'))

    MarkerType.update(id, name=name, color=color if color else None, icon=icon if icon else None)
    flash('[OK] 標記種類已更新', 'success')
    return redirect(url_for('marker.list_marker_types'))


@marker_bp.route('/settings/markers/<int:id>/delete', methods=['POST'])
def delete_marker_type(id):
    """刪除標記種類。
    """
    mt = MarkerType.get_by_id(id)
    if mt is None:
        abort(404)

    success = MarkerType.delete(id)
    if not success:
        flash('[ERROR] 該標記種類已被使用，無法刪除', 'danger')
    else:
        flash('[OK] 標記種類已刪除', 'success')

    return redirect(url_for('marker.list_marker_types'))
