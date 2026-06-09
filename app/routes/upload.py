"""
Upload Routes — 音訊上傳相關路由（轉寫系統）

Routes:
    GET  /upload         → 顯示上傳頁面
    POST /upload         → 接收音訊檔案與 Markers，觸發轉寫
"""

import os
import json
import uuid
from flask import Blueprint, render_template, request, jsonify, current_app, flash

from app.models import transcription as Transcription
from app.models import transcription_segment as Segment
from app.models import transcription_marker as TMarker
from app.services import file_validator as FileValidator
from app.services.whisper_client import transcribe, WhisperError
from app.services import timeline_align as TimelineAlign

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/upload', methods=['GET'])
def upload_page():
    """顯示音訊上傳頁面。"""
    return render_template('transcriptions/upload.html')


@upload_bp.route('/upload', methods=['POST'])
def upload_audio():
    """
    提交音訊檔案上傳，完整流程：
    驗證 → UUID 命名 → 建立紀錄 → Whisper API → 儲存段落 → 對齊標記 → 更新狀態
    """
    # 階段一：檢查是否有上傳檔案
    if 'audio_file' not in request.files:
        return jsonify({'error': '缺少音訊檔案，請選擇要上傳的檔案'}), 400

    audio_file = request.files['audio_file']

    # 階段二：檔案安全驗證
    is_valid, error_msg = FileValidator.validate(audio_file)
    if not is_valid:
        return jsonify({'error': error_msg}), 400

    file_info = FileValidator.get_file_info(audio_file)

    # 階段三：以 UUID 重新命名並儲存
    ext = file_info['extension']
    stored_filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, stored_filename)

    try:
        audio_file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'檔案儲存失敗：{e}'}), 500

    # 階段四：建立轉寫紀錄
    try:
        transcription_id = Transcription.create(
            original_filename=file_info['original_filename'],
            stored_filename=stored_filename,
            file_path=file_path,
            file_size=file_info['file_size'],
            mime_type=file_info['mime_type'],
        )
    except Exception as e:
        _cleanup_file(file_path)
        return jsonify({'error': f'建立轉寫紀錄失敗：{e}'}), 500

    markers_data = _parse_markers(request.form.get('markers', '[]'))
    Transcription.update_status(transcription_id, 'processing')

    # 階段五：呼叫 Whisper API
    try:
        whisper_result = transcribe(file_path)
    except WhisperError as e:
        Transcription.update_status(transcription_id, 'failed', error_message=e.message)
        return jsonify({'error': e.message, 'transcription_id': transcription_id}), e.status_code
    except Exception as e:
        Transcription.update_status(transcription_id, 'failed', error_message=str(e))
        return jsonify({'error': f'語音辨識過程發生未預期的錯誤：{e}', 'transcription_id': transcription_id}), 500

    # 階段六：儲存轉寫結果
    try:
        Transcription.update_transcription(
            transcription_id,
            full_text=whisper_result['text'],
            duration=whisper_result['duration'],
            language=whisper_result['language'],
        )
        Segment.bulk_create(transcription_id, whisper_result['segments'])
    except Exception as e:
        Transcription.update_status(transcription_id, 'failed', error_message=f'儲存轉寫結果失敗：{e}')
        return jsonify({'error': f'儲存轉寫結果失敗：{e}', 'transcription_id': transcription_id}), 500

    # 階段七：時間軸對齊與儲存標記
    try:
        if markers_data:
            db_segments = Segment.get_by_transcription_id(transcription_id)
            segments_for_align = [
                {'id': seg['id'], 'start_time': seg['start_time'], 'end_time': seg['end_time']}
                for seg in db_segments
            ]
            aligned_markers = TimelineAlign.align(markers_data, segments_for_align)
            TMarker.bulk_create(transcription_id, aligned_markers)
    except Exception as e:
        current_app.logger.error(f'時間軸對齊失敗 (transcription_id={transcription_id})：{e}')

    # 階段八：更新狀態為完成
    Transcription.update_status(transcription_id, 'completed')

    return jsonify({
        'transcription_id': transcription_id,
        'status': 'completed',
        'message': '語音轉寫完成',
    }), 200


def _parse_markers(markers_json):
    """解析前端傳來的 Markers JSON 字串。"""
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
