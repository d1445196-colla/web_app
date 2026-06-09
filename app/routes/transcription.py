"""
Transcription Routes — 轉寫結果相關路由

Routes:
    GET  /transcriptions/<id>/status  → 查詢轉寫處理狀態 (JSON)
    GET  /transcriptions/<id>         → 查看單筆轉寫結果頁面
    GET  /transcriptions              → 轉寫歷史紀錄列表
    POST /transcriptions/<id>/delete  → 刪除轉寫紀錄
"""

import os
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, abort

from app.models import transcription as Transcription
from app.models import transcription_segment as Segment
from app.models import transcription_marker as TMarker

transcription_bp = Blueprint('transcription', __name__)


@transcription_bp.route('/transcriptions/<int:id>/status', methods=['GET'])
def get_status(id):
    """查詢轉寫處理狀態，供前端輪詢。"""
    try:
        record = Transcription.get_by_id(id)
    except Exception as e:
        return jsonify({'error': f'查詢紀錄失敗：{e}'}), 500

    if record is None:
        return jsonify({'error': '找不到此轉寫紀錄'}), 404

    response = {'status': record['status']}
    if record['status'] == 'failed' and record['error_message']:
        response['error'] = record['error_message']
    if record['status'] == 'completed':
        response['transcription_id'] = record['id']

    return jsonify(response), 200


@transcription_bp.route('/transcriptions/<int:id>', methods=['GET'])
def show_result(id):
    """查看單筆轉寫結果頁面。"""
    try:
        record = Transcription.get_by_id(id)
    except Exception as e:
        flash(f'查詢紀錄失敗：{e}', 'danger')
        return redirect(url_for('upload.upload_page'))

    if record is None:
        abort(404)

    if record['status'] == 'processing':
        flash('此錄音仍在轉寫處理中，請稍後再查看。', 'warning')
        return redirect(url_for('upload.upload_page'))

    if record['status'] == 'failed':
        flash(f"轉寫失敗：{record['error_message'] or '未知錯誤'}", 'danger')

    try:
        segments = Segment.get_by_transcription_id(id)
        markers = TMarker.get_by_transcription_id(id)
    except Exception as e:
        flash(f'載入轉寫資料失敗：{e}', 'danger')
        segments = []
        markers = []

    segment_map = {seg['id']: seg for seg in segments}

    return render_template(
        'transcriptions/result.html',
        recording=record,
        segments=segments,
        markers=markers,
        segment_map=segment_map,
    )


@transcription_bp.route('/transcriptions', methods=['GET'])
def history():
    """轉寫歷史紀錄列表。"""
    try:
        records = Transcription.get_all()
    except Exception as e:
        flash(f'載入歷史紀錄失敗：{e}', 'danger')
        records = []

    return render_template(
        'transcriptions/history.html',
        recordings=records,
    )


@transcription_bp.route('/transcriptions/<int:id>/delete', methods=['POST'])
def delete(id):
    """刪除轉寫紀錄。"""
    try:
        record = Transcription.get_by_id(id)
    except Exception as e:
        flash(f'查詢紀錄失敗：{e}', 'danger')
        return redirect(url_for('transcription.history'))

    if record is None:
        abort(404)

    try:
        file_path = record['file_path']
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass

    try:
        Transcription.delete(id)
        flash('轉寫紀錄已成功刪除。', 'success')
    except Exception as e:
        flash(f'刪除紀錄失敗：{e}', 'danger')

    return redirect(url_for('transcription.history'))
