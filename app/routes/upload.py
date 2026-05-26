"""
Upload Routes — 音訊上傳相關路由

負責處理音訊檔案上傳頁面的顯示與上傳請求的接收。
包含檔案安全驗證、Whisper API 串接觸發、轉寫結果儲存等完整流程。

Routes:
    GET  /          → 顯示上傳頁面
    POST /upload    → 接收音訊檔案與 Markers，觸發轉寫
"""

import os
import json
import uuid
from flask import Blueprint, render_template, request, jsonify, current_app, flash

from app.models import recording as Recording
from app.models import segment as Segment
from app.models import marker as Marker
from app.services import file_validator as FileValidator
from app.services.whisper_client import transcribe, WhisperError
from app.services import timeline_align as TimelineAlign

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/', methods=['GET'])
def index():
    """
    首頁 / 音訊上傳頁面

    - 輸入：無
    - 處理：直接渲染上傳表單頁面
    - 輸出：渲染 transcriptions/upload.html
    """
    return render_template('transcriptions/upload.html')


@upload_bp.route('/upload', methods=['POST'])
def upload_audio():
    """
    提交音訊檔案上傳

    接收 multipart/form-data，包含音訊檔案與可選的 Markers JSON。
    完成驗證後依序執行：儲存檔案 → 建立紀錄 → 呼叫 Whisper API →
    儲存段落 → 時間軸對齊 → 儲存標記 → 更新狀態。

    - 輸入：audio_file (音訊檔案), markers (JSON 字串)
    - 輸出：成功 → 202 JSON，失敗 → 對應的錯誤狀態碼
    """
    # ============================
    # 階段一：檢查是否有上傳檔案
    # ============================
    if 'audio_file' not in request.files:
        return jsonify({'error': '缺少音訊檔案，請選擇要上傳的檔案'}), 400

    audio_file = request.files['audio_file']

    # ============================
    # 階段二：檔案安全驗證
    # ============================
    is_valid, error_msg = FileValidator.validate(audio_file)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    # 取得檔案資訊
    file_info = FileValidator.get_file_info(audio_file)

    # ============================
    # 階段三：以 UUID 重新命名並儲存
    # ============================
    ext = file_info['extension']
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, stored_filename)

    try:
        audio_file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'檔案儲存失敗：{e}'}), 500

    # ============================
    # 階段四：建立錄音紀錄
    # ============================
    try:
        recording_id = Recording.create(
            original_filename=file_info['original_filename'],
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_info['file_size'],
            mime_type=file_info['mime_type'],
        )
    except Exception as e:
        # 清理已儲存的檔案
        _cleanup_file(file_path)
        return jsonify({'error': f'建立錄音紀錄失敗：{e}'}), 500

    # 解析前端傳來的 Markers
    markers_data = _parse_markers(request.form.get('markers', '[]'))

    # 更新狀態為 processing
    Recording.update_status(recording_id, 'processing')

    # 先回傳 202 給前端，讓前端可以開始輪詢
    # 注意：在 MVP 階段採用同步處理，轉寫完成後才真正回傳
    # 前端可以透過 /transcriptions/<id>/status 輪詢狀態

    # ============================
    # 階段五：呼叫 Whisper API
    # ============================
    try:
        whisper_result = transcribe(file_path)
    except WhisperError as e:
        Recording.update_status(recording_id, 'failed', error_message=e.message)
        return jsonify({
            'error': e.message,
            'recording_id': recording_id,
        }), e.status_code
    except Exception as e:
        Recording.update_status(recording_id, 'failed', error_message=str(e))
        return jsonify({
            'error': f'語音辨識過程發生未預期的錯誤：{e}',
            'recording_id': recording_id,
        }), 500

    # ============================
    # 階段六：儲存轉寫結果
    # ============================
    try:
        # 更新錄音紀錄的轉寫資訊
        Recording.update_transcription(
            recording_id,
            full_text=whisper_result['text'],
            duration=whisper_result['duration'],
            language=whisper_result['language'],
        )

        # 批次寫入轉寫段落
        Segment.bulk_create(recording_id, whisper_result['segments'])

    except Exception as e:
        Recording.update_status(recording_id, 'failed', error_message=f'儲存轉寫結果失敗：{e}')
        return jsonify({
            'error': f'儲存轉寫結果失敗：{e}',
            'recording_id': recording_id,
        }), 500

    # ============================
    # 階段七：時間軸對齊與儲存標記
    # ============================
    try:
        if markers_data:
            # 取得剛寫入的 segments（含資料庫 ID）
            db_segments = Segment.get_by_recording_id(recording_id)
            segments_for_align = [
                {
                    'id': seg['id'],
                    'start_time': seg['start_time'],
                    'end_time': seg['end_time'],
                }
                for seg in db_segments
            ]

            # 時間軸對齊
            aligned_markers = TimelineAlign.align(markers_data, segments_for_align)

            # 批次寫入標記
            Marker.bulk_create(recording_id, aligned_markers)
    except Exception as e:
        # 標記對齊失敗不影響轉寫結果，記錄錯誤但不中斷
        current_app.logger.error(f'時間軸對齊失敗 (recording_id={recording_id})：{e}')

    # ============================
    # 階段八：更新狀態為完成
    # ============================
    Recording.update_status(recording_id, 'completed')

    return jsonify({
        'recording_id': recording_id,
        'status': 'completed',
        'message': '語音轉寫完成',
    }), 200


def _parse_markers(markers_json):
    """
    解析前端傳來的 Markers JSON 字串。

    Args:
        markers_json (str): JSON 格式的標記陣列字串

    Returns:
        list[dict]: 標記列表，解析失敗時回傳空列表
    """
    try:
        markers = json.loads(markers_json)
        if not isinstance(markers, list):
            return []
        return markers
    except (json.JSONDecodeError, TypeError):
        return []


def _cleanup_file(file_path):
    """安全地刪除暫存檔案。"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
