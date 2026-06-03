# app/routes/recording.py
# 錄音路由 Blueprint — 錄音的儲存、列表、詳情、更新、刪除、下載

import os
import json
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, send_file, current_app

from app.models.recording import Recording
from app.models.marker import Marker
from app.models.marker_type import MarkerType

recording_bp = Blueprint('recording', __name__)


@recording_bp.route('/recordings', methods=['POST'])
def create():
    """儲存錄音。

    接收前端上傳的音訊檔案與標記資料，儲存至伺服器。
    """
    if 'audio_file' not in request.files:
        flash('[ERROR] 缺少音訊檔案，無法儲存', 'danger')
        return redirect(url_for('main.index'))

    audio_file = request.files['audio_file']
    title = request.form.get('title', '').strip()
    duration_sec = request.form.get('duration_sec', '0')
    category = request.form.get('category', '').strip()
    markers_json = request.form.get('markers_json', '[]')

    if not title:
        flash('[ERROR] 標題不可為空', 'danger')
        return redirect(url_for('main.index'))

    try:
        duration_sec = int(float(duration_sec))
    except ValueError:
        duration_sec = 0

    # Ensure uploads folder exists
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    # Save audio file with unique name
    ext = os.path.splitext(audio_file.filename)[1] or '.webm'
    if ext.lower() not in ['.webm', '.wav', '.mp3', '.m4a']:
        ext = '.webm'
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_folder, filename)

    try:
        audio_file.save(filepath)
    except Exception as e:
        flash(f'[ERROR] 檔案儲存失敗: {e}', 'danger')
        return redirect(url_for('main.index'))

    # Create database records
    try:
        # Create recording record
        rec = Recording.create(title, filepath, duration_sec, category if category else None)
        
        # Parse and save markers
        try:
            markers_list = json.loads(markers_json)
            if isinstance(markers_list, list) and len(markers_list) > 0:
                Marker.create_batch(rec.id, markers_list)
        except Exception as e:
            current_app.logger.error(f"Error parsing markers json: {e}")
            flash('[WARNING] 錄音已儲存，但標記資料匯入失敗', 'warning')

        flash('[OK] 錄音儲存成功', 'success')
        return redirect(url_for('recording.detail', id=rec.id))
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        flash(f'[ERROR] 儲存錄音紀錄失敗: {e}', 'danger')
        return redirect(url_for('main.index'))


@recording_bp.route('/recordings', methods=['GET'])
def list_recordings():
    """錄音列表頁面。

    顯示所有歷史錄音，支援搜尋。
    """
    q = request.args.get('q', '').strip()
    if q:
        recordings = Recording.search(q)
    else:
        recordings = Recording.get_all()

    # Attach marker counts to recordings dynamically
    for rec in recordings:
        rec.marker_count = Recording.get_marker_count(rec.id)

    return render_template('recordings/list.html', recordings=recordings, q=q)


@recording_bp.route('/recordings/<int:id>', methods=['GET'])
def detail(id):
    """錄音詳情 / 回顧頁面。

    播放錄音，顯示標記清單，支援跳轉回聽。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        abort(404)

    markers = Marker.get_by_recording(id)
    marker_types = MarkerType.get_all()
    marker_types_map = {mt.id: mt for mt in marker_types}

    return render_template(
        'recordings/detail.html',
        recording=rec,
        markers=markers,
        marker_types=marker_types,
        marker_types_map=marker_types_map
    )


@recording_bp.route('/recordings/<int:id>/update', methods=['POST'])
def update(id):
    """更新錄音的標題或分類。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        abort(404)

    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()

    if not title:
        flash('[ERROR] 標題不可為空', 'danger')
        return redirect(url_for('recording.detail', id=id))

    Recording.update(id, title=title, category=category if category else None)
    flash('[OK] 錄音資訊更新成功', 'success')
    return redirect(url_for('recording.detail', id=id))


@recording_bp.route('/recordings/<int:id>/delete', methods=['POST'])
def delete(id):
    """刪除錄音。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        abort(404)

    # Delete local file
    if rec.filepath and os.path.exists(rec.filepath):
        try:
            os.remove(rec.filepath)
        except OSError as e:
            current_app.logger.error(f"Error removing file {rec.filepath}: {e}")

    # Delete database record
    Recording.delete(id)
    flash('[OK] 錄音已刪除', 'success')
    return redirect(url_for('recording.list_recordings'))


@recording_bp.route('/recordings/<int:id>/download', methods=['GET'])
def download(id):
    """下載錄音音訊檔案。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        abort(404)

    if not rec.filepath or not os.path.exists(rec.filepath):
        abort(404)

    return send_file(rec.filepath)
