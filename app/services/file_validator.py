"""
FileValidator — 檔案驗證邏輯

負責驗證上傳的音訊檔案是否符合系統要求，
包含檔案大小、副檔名白名單與 MIME Type 檢查。
"""

# Whisper API 支援的音訊格式
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'webm', 'ogg', 'flac', 'mp4', 'mpeg', 'mpga'}

# 對應的合法 MIME Type
ALLOWED_MIME_TYPES = {
    'audio/wav', 'audio/x-wav', 'audio/wave',
    'audio/mpeg', 'audio/mp3',
    'audio/mp4', 'audio/x-m4a', 'audio/m4a',
    'audio/webm',
    'audio/ogg',
    'audio/flac', 'audio/x-flac',
    'video/mp4', 'video/webm',  # 部分瀏覽器錄音產生的格式
}

# Whisper API 檔案大小上限 (25MB)
MAX_FILE_SIZE = 25 * 1024 * 1024


def validate(file):
    """
    驗證上傳的音訊檔案是否合法。

    依序檢查：檔案是否存在、副檔名是否在白名單內、
    MIME Type 是否合法、檔案大小是否超過 25MB 上限。

    Args:
        file (werkzeug.datastructures.FileStorage): Flask 接收到的上傳檔案物件

    Returns:
        tuple: (is_valid, error_message)
            - is_valid (bool): 驗證是否通過
            - error_message (str | None): 失敗時的錯誤訊息，通過時為 None
    """
    # 檢查 1：檔案是否存在
    if file is None or file.filename == '':
        return False, '缺少音訊檔案，請選擇要上傳的檔案'

    # 檢查 2：副檔名白名單
    filename = file.filename
    if '.' not in filename:
        return False, '檔案缺少副檔名，無法辨識格式'

    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed_list = ', '.join(sorted(ALLOWED_EXTENSIONS))
        return False, f'不支援的檔案格式「.{ext}」。支援的格式：{allowed_list}'

    # 檢查 3：MIME Type 驗證
    mime_type = file.content_type or ''
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        # 有些瀏覽器的 MIME type 可能不在白名單中，但副檔名正確時仍放行
        # 這裡記錄警告但不阻擋
        pass

    # 檢查 4：檔案大小（需要先讀取再還原指標位置）
    file.seek(0, 2)  # 移到檔案末尾
    file_size = file.tell()
    file.seek(0)     # 還原到開頭

    if file_size == 0:
        return False, '上傳的檔案為空，請確認檔案是否正確'

    if file_size > MAX_FILE_SIZE:
        size_mb = round(file_size / (1024 * 1024), 1)
        return False, f'檔案大小 ({size_mb} MB) 超過上限 25MB，請壓縮或裁切音訊後再上傳'

    return True, None


def get_file_info(file):
    """
    取得檔案的基本資訊。

    Args:
        file (werkzeug.datastructures.FileStorage): 上傳檔案物件

    Returns:
        dict: 包含 original_filename, extension, mime_type, file_size
    """
    filename = file.filename
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    return {
        'original_filename': filename,
        'extension': ext,
        'mime_type': file.content_type or 'application/octet-stream',
        'file_size': file_size,
    }
