# app/routes/api.py
# API 路由 Blueprint — RESTful JSON 端點（供外部系統整合）

from flask import Blueprint, jsonify

from app.models.recording import Recording
from app.models.marker import Marker
from app.models.marker_type import MarkerType

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/recordings', methods=['GET'])
def get_recordings():
    """錄音列表 API。
    """
    recordings = Recording.get_all()
    return jsonify({
        "recordings": [rec.to_dict() for rec in recordings]
    })


@api_bp.route('/recordings/<int:id>', methods=['GET'])
def get_recording(id):
    """錄音詳情 API。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        return jsonify({"error": "Recording not found"}), 404

    markers = Marker.get_by_recording(id)
    return jsonify({
        "recording": rec.to_dict(),
        "markers": [m.to_dict() for m in markers]
    })


@api_bp.route('/recordings/<int:id>/markers', methods=['GET'])
def get_markers(id):
    """標記列表 API。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        return jsonify({"error": "Recording not found"}), 404

    markers = Marker.get_by_recording(id)
    return jsonify({
        "markers": [m.to_dict() for m in markers]
    })


@api_bp.route('/marker-types', methods=['GET'])
def get_marker_types():
    """標記種類 API。
    """
    types = MarkerType.get_all()
    return jsonify({
        "marker_types": [mt.to_dict() for mt in types]
    })
