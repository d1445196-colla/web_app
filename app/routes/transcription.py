"""
Transcription Routes — 轉寫結果相關路由

負責處理轉寫狀態查詢、結果頁面顯示、歷史紀錄列表與刪除功能。

Routes:
    GET  /transcriptions/<id>/status  → 查詢轉寫處理狀態 (JSON)
    GET  /transcriptions/<id>         → 查看單筆轉寫結果頁面
    GET  /transcriptions              → 轉寫歷史紀錄列表
    POST /transcriptions/<id>/delete  → 刪除錄音紀錄
"""

import os
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash, abort

from app.models import recording as Recording
from app.models import segment as Segment
from app.models import marker as Marker

transcription_bp = Blueprint('transcription', __name__)


@transcription_bp.route('/transcriptions/<int:id>/status', methods=['GET'])
def get_status(id):
    """
    查詢轉寫處理狀態

    供前端 JavaScript 輪詢使用，回傳 JSON 格式的處理狀態。

    - 輸入：URL 參數 id (錄音紀錄 ID)
    - 輸出：200 OK，JSON 格式
    - 錯誤：紀錄不存在 → 404
    """
    try:
        recording = Recording.get_by_id(id)
    except Exception as e:
        return jsonify({'error': f'查詢紀錄失敗：{e}'}), 500

    if recording is None:
        return jsonify({'error': '找不到此錄音紀錄'}), 404

    response = {'status': recording['status']}

    # 若轉寫失敗，附上錯誤訊息
    if recording['status'] == 'failed' and recording['error_message']:
        response['error'] = recording['error_message']

    # 若轉寫完成，附上 recording_id 供前端跳轉
    if recording['status'] == 'completed':
        response['recording_id'] = recording['id']

    return jsonify(response), 200


@transcription_bp.route('/transcriptions/<int:id>', methods=['GET'])
def show_result(id):
    """
    查看單筆轉寫結果頁面

    顯示完整的逐字稿、每句時間戳與標記對齊結果。

    - 輸入：URL 參數 id (錄音紀錄 ID)
    - 輸出：渲染 transcriptions/result.html
    - 錯誤：紀錄不存在 → 404 / 處理中 → 重導向
    """
    try:
        recording = Recording.get_by_id(id)
    except Exception as e:
        flash(f'查詢紀錄失敗：{e}', 'danger')
        return redirect(url_for('upload.index'))

    if recording is None:
        abort(404)

    # 若仍在處理中，重導向回首頁並提示
    if recording['status'] == 'processing':
        flash('此錄音仍在轉寫處理中，請稍後再查看。', 'warning')
        return redirect(url_for('upload.index'))

    # 若轉寫失敗，仍顯示結果頁面但帶錯誤訊息
    if recording['status'] == 'failed':
        flash(f"轉寫失敗：{recording['error_message'] or '未知錯誤'}", 'danger')

    # 取得轉寫段落與即時標記
    try:
        segments = Segment.get_by_recording_id(id)
        markers = Marker.get_by_recording_id(id)
    except Exception as e:
        flash(f'載入轉寫資料失敗：{e}', 'danger')
        segments = []
        markers = []

    # 建立 segment_id → segment 的映射，方便模板中查找標記對應的段落
    segment_map = {seg['id']: seg for seg in segments}

    return render_template(
        'transcriptions/result.html',
        recording=recording,
        segments=segments,
        markers=markers,
        segment_map=segment_map,
    )


@transcription_bp.route('/transcriptions', methods=['GET'])
def history():
    """
    轉寫歷史紀錄列表

    列出所有錄音紀錄，包含檔名、狀態、上傳時間等資訊。

    - 輸入：無
    - 輸出：渲染 transcriptions/history.html
    """
    try:
        recordings = Recording.get_all()
    except Exception as e:
        flash(f'載入歷史紀錄失敗：{e}', 'danger')
        recordings = []

    return render_template(
        'transcriptions/history.html',
        recordings=recordings,
    )


@transcription_bp.route('/transcriptions/<int:id>/delete', methods=['POST'])
def delete(id):
    """
    刪除錄音紀錄

    刪除指定的錄音紀錄及其關聯資料，同時清除暫存的音訊檔案。

    - 輸入：URL 參數 id (錄音紀錄 ID)
    - 輸出：302 Redirect 至 /transcriptions
    - 錯誤：紀錄不存在 → 404
    """
    try:
        recording = Recording.get_by_id(id)
    except Exception as e:
        flash(f'查詢紀錄失敗：{e}', 'danger')
        return redirect(url_for('transcription.history'))

    if recording is None:
        abort(404)

    # 刪除暫存的音訊檔案
    try:
        file_path = recording['file_path']
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except OSError as e:
        # 檔案刪除失敗不中斷流程，僅記錄
        pass

    # 刪除資料庫紀錄（級聯刪除 segments 與 markers）
    try:
        Recording.delete(id)
        flash('錄音紀錄已成功刪除。', 'success')
    except Exception as e:
        flash(f'刪除紀錄失敗：{e}', 'danger')

    return redirect(url_for('transcription.history'))
