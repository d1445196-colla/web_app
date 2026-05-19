# app/routes/marker.py
# 標記路由 Blueprint — 標記 CRUD + 標記種類管理

from flask import Blueprint

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

    處理邏輯：Marker.update(id, note)
    輸出：重導向至 /recordings/<recording_id>
    錯誤：找不到標記 → 404
    """
    # TODO: 實作
    pass


@marker_bp.route('/markers/<int:id>/delete', methods=['POST'])
def delete_marker(id):
    """刪除單一標記。

    輸入：URL 參數 id（標記 ID）

    處理邏輯：
        1. Marker.get_by_id(id) 取得 recording_id
        2. Marker.delete(id)

    輸出：重導向至 /recordings/<recording_id>
    錯誤：找不到標記 → 404
    """
    # TODO: 實作
    pass


# ============================================
# 標記種類管理
# ============================================

@marker_bp.route('/settings/markers', methods=['GET'])
def list_marker_types():
    """標記種類列表頁面。

    顯示所有標記種類，支援新增 / 編輯 / 刪除。

    處理邏輯：
        1. MarkerType.get_all()
        2. 為每個種類取得 MarkerType.get_usage_count(id)

    Template: templates/settings/marker_types.html
    """
    # TODO: 實作
    pass


@marker_bp.route('/settings/markers', methods=['POST'])
def create_marker_type():
    """新增標記種類。

    輸入：
        - request.form['name']：種類名稱
        - request.form['color']：顏色 HEX
        - request.form['icon']：圖示 Emoji

    處理邏輯：MarkerType.create(name, color, icon)
    輸出：重導向至 /settings/markers
    """
    # TODO: 實作
    pass


@marker_bp.route('/settings/markers/<int:id>/update', methods=['POST'])
def update_marker_type(id):
    """更新標記種類。

    輸入：
        - URL 參數 id
        - request.form['name']、request.form['color']、request.form['icon']

    處理邏輯：MarkerType.update(id, name, color, icon)
    輸出：重導向至 /settings/markers
    錯誤：找不到種類 → 404
    """
    # TODO: 實作
    pass


@marker_bp.route('/settings/markers/<int:id>/delete', methods=['POST'])
def delete_marker_type(id):
    """刪除標記種類。

    輸入：URL 參數 id

    處理邏輯：MarkerType.delete(id)
    輸出：重導向至 /settings/markers
    錯誤：找不到種類 → 404；仍有標記引用 → flash 錯誤訊息
    """
    # TODO: 實作
    pass
