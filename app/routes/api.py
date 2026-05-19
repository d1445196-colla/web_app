# app/routes/api.py
# API 路由 Blueprint — RESTful JSON 端點（供外部系統整合）

from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/recordings', methods=['GET'])
def get_recordings():
    """錄音列表 API。

    回傳所有錄音的後設資料（JSON 格式）。

    處理邏輯：
        1. Recording.get_all()
        2. 回傳 { "recordings": [ rec.to_dict(), ... ] }

    輸出：JSON
    """
    # TODO: 實作
    pass


@api_bp.route('/recordings/<int:id>', methods=['GET'])
def get_recording(id):
    """錄音詳情 API。

    回傳單一錄音的後設資料與所有標記（JSON 格式）。

    輸入：URL 參數 id

    處理邏輯：
        1. Recording.get_by_id(id)
        2. Marker.get_by_recording(id)
        3. 回傳 { "recording": rec.to_dict(), "markers": [ m.to_dict(), ... ] }

    輸出：JSON
    錯誤：找不到 → 404 JSON
    """
    # TODO: 實作
    pass


@api_bp.route('/recordings/<int:id>/markers', methods=['GET'])
def get_markers(id):
    """標記列表 API。

    回傳某錄音的所有標記（JSON 格式）。

    輸入：URL 參數 id（錄音 ID）

    處理邏輯：
        1. Marker.get_by_recording(id)
        2. 回傳 { "markers": [ m.to_dict(), ... ] }

    輸出：JSON
    """
    # TODO: 實作
    pass


@api_bp.route('/marker-types', methods=['GET'])
def get_marker_types():
    """標記種類 API。

    回傳所有標記種類（JSON 格式）。

    處理邏輯：
        1. MarkerType.get_all()
        2. 回傳 { "marker_types": [ mt.to_dict(), ... ] }

    輸出：JSON
    """
    # TODO: 實作
    pass
