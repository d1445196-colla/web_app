# app/routes/recording.py
# 錄音路由 Blueprint — 錄音的儲存、列表、詳情、更新、刪除、下載

import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, send_file
from werkzeug.utils import secure_filename
from app.models.recording import Recording
from app.models.marker import Marker
from app.models.marker_type import MarkerType

recording_bp = Blueprint('recording', __name__)


@recording_bp.route('/recordings', methods=['POST'])
def create():
    """儲存錄音。

    接收前端上傳的音訊檔案與標記資料，儲存至伺服器。
    """
    # 驗證必填欄位
    if 'audio_file' not in request.files:
        flash('未偵測到錄音檔案', 'error')
        return redirect(url_for('main.index'))
    
    audio_file = request.files['audio_file']
    title = request.form.get('title', '').strip()
    duration_sec_str = request.form.get('duration_sec', '0')
    category = request.form.get('category', '').strip() or None
    markers_json = request.form.get('markers_json', '[]')

    if not title:
        # 如果沒有標題，使用當前時間作為預設標題
        title = f"錄音_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        duration_sec = int(float(duration_sec_str))
    except ValueError:
        duration_sec = 0

    # 1. 儲存音訊檔案至 static/uploads/
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    # 產生安全且唯一的檔名
    ext = '.webm' # 預設副檔名
    if audio_file.filename and '.' in audio_file.filename:
        ext = os.path.splitext(audio_file.filename)[1]
    
    unique_filename = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(upload_dir, unique_filename)
    
    try:
        audio_file.save(filepath)
    except Exception as e:
        current_app.logger.error(f"檔案儲存失敗: {e}")
        flash('音訊檔案儲存失敗，請重試。', 'error')
        return redirect(url_for('main.index'))

    # 2. 建立資料庫紀錄 (將 filepath 存為相對 static 的路徑)
    # 例如：'uploads/rec_20260519_xxxx.webm'
    db_filepath = f"uploads/{unique_filename}"
    
    try:
        rec = Recording.create(
            title=title,
            filepath=db_filepath,
            duration_sec=duration_sec,
            category=category
        )
        
        # 3. 解析 markers_json 並批次儲存標記
        if markers_json:
            try:
                markers_list = json.loads(markers_json)
                if markers_list:
                    # 確保每個 marker 中的資料型態正確
                    sanitized_markers = []
                    for m in markers_list:
                        sanitized_markers.append({
                            'type_id': int(m.get('type_id')),
                            'timestamp_sec': int(float(m.get('timestamp_sec', 0))),
                            'note': m.get('note', '').strip() or None
                        })
                    Marker.create_batch(rec.id, sanitized_markers)
            except Exception as e:
                current_app.logger.error(f"儲存標記失敗: {e}")
                # 即使標記儲存失敗，錄音檔案已成功，故不阻斷
                flash('錄音已儲存，但部分時間點標記儲存失敗。', 'warning')
        
        flash('錄音與標記已成功儲存！', 'success')
        return redirect(url_for('recording.detail', id=rec.id))
        
    except Exception as e:
        current_app.logger.error(f"資料庫新增錄音失敗: {e}")
        # 清除已存檔的實體檔案
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass
        flash('儲存錄音紀錄至資料庫時發生錯誤。', 'error')
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
        
    # 為每筆錄音取得標記數量
    for rec in recordings:
        rec.marker_count = Recording.get_marker_count(rec.id)
        
    return render_template('recordings/list.html', recordings=recordings, query=q)


@recording_bp.route('/recordings/<int:id>', methods=['GET'])
def detail(id):
    """錄音詳情 / 回顧頁面。

    播放錄音，顯示標記清單，支援跳轉回聽。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        flash('找不到該筆錄音紀錄', 'error')
        return redirect(url_for('recording.list_recordings'))
        
    markers = Marker.get_by_recording(id)
    marker_types = MarkerType.get_all()
    
    # 建立標記種類的對照字典，方便在前端顯示標記的名稱與圖示
    marker_types_dict = {mt.id: mt for mt in marker_types}
    for m in markers:
        m.type = marker_types_dict.get(m.type_id)
        
    return render_template(
        'recordings/detail.html',
        recording=rec,
        markers=markers,
        marker_types=marker_types
    )


@recording_bp.route('/recordings/<int:id>/update', methods=['POST'])
def update(id):
    """更新錄音的標題或分類。"""
    rec = Recording.get_by_id(id)
    if rec is None:
        flash('找不到該筆錄音紀錄，無法更新。', 'error')
        return redirect(url_for('recording.list_recordings'))
        
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip() or None
    
    if not title:
        flash('標題不得為空。', 'error')
        return redirect(url_for('recording.detail', id=id))
        
    try:
        Recording.update(id, title=title, category=category)
        flash('錄音資料已成功更新。', 'success')
    except Exception as e:
        current_app.logger.error(f"更新錄音失敗: {e}")
        flash('更新錄音資料時發生錯誤。', 'error')
        
    return redirect(url_for('recording.detail', id=id))


@recording_bp.route('/recordings/<int:id>/delete', methods=['POST'])
def delete(id):
    """刪除錄音。

    刪除錄音紀錄、音訊檔案與所有標記。
    """
    rec = Recording.get_by_id(id)
    if rec is None:
        flash('找不到該筆錄音紀錄，無法刪除。', 'error')
        return redirect(url_for('recording.list_recordings'))
        
    # 1. 取得檔案路徑並刪除音訊檔案
    # rec.filepath 格式為 'uploads/rec_xxxx.webm'
    static_dir = os.path.join(current_app.root_path, 'static')
    full_filepath = os.path.join(static_dir, rec.filepath)
    
    if os.path.exists(full_filepath):
        try:
            os.remove(full_filepath)
        except Exception as e:
            current_app.logger.error(f"實體檔案刪除失敗: {e}")
            # 檔案刪除失敗仍繼續刪除資料庫紀錄
            
    # 2. 刪除資料庫紀錄 (標記會因外鍵約束 ON DELETE CASCADE 自動被刪除)
    try:
        Recording.delete(id)
        flash('錄音紀錄已成功刪除。', 'success')
    except Exception as e:
        current_app.logger.error(f"資料庫刪除錄音紀錄失敗: {e}")
        flash('刪除錄音紀錄時發生錯誤。', 'error')
        
    return redirect(url_for('recording.list_recordings'))


@recording_bp.route('/recordings/<int:id>/download', methods=['GET'])
def download(id):
    """下載錄音音訊檔案。"""
    rec = Recording.get_by_id(id)
    if rec is None:
        flash('找不到該筆錄音紀錄，無法下載。', 'error')
        return redirect(url_for('recording.list_recordings'))
        
    static_dir = os.path.join(current_app.root_path, 'static')
    full_filepath = os.path.join(static_dir, rec.filepath)
    
    if not os.path.exists(full_filepath):
        flash('錄音音訊實體檔案已遺失，無法下載。', 'error')
        return redirect(url_for('recording.detail', id=id))
        
    # 下載時的自訂呈現名稱
    safe_title = secure_filename(rec.title) or "recording"
    ext = os.path.splitext(full_filepath)[1] or ".webm"
    download_name = f"{safe_title}{ext}"
    
    try:
        return send_file(
            full_filepath,
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        current_app.logger.error(f"下載檔案失敗: {e}")
        flash('下載音訊檔案時發生錯誤。', 'error')
        return redirect(url_for('recording.detail', id=id))
