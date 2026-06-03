# app/routes/recording.py
# 錄音路由 Blueprint — 錄音的儲存、列表、詳情、更新、刪除、下載

from flask import Blueprint

recording_bp = Blueprint('recording', __name__)


@recording_bp.route('/recordings', methods=['POST'])
def create():
    """儲存錄音。

    接收前端上傳的音訊檔案與標記資料，儲存至伺服器。

    輸入：
        - request.files['audio_file']：音訊檔案（WebM/WAV）
        - request.form['title']：錄音標題
        - request.form['duration_sec']：時長（秒）
        - request.form['category']：分類（可選）
        - request.form['markers_json']：標記 JSON 陣列

    處理邏輯：
        1. 驗證必填欄位
        2. 儲存音訊檔案至 static/uploads/（生成唯一檔名）
        3. Recording.create(title, filepath, duration_sec, category)
        4. 解析 markers_json，Marker.create_batch(recording_id, markers_list)

    輸出：重導向至 /recordings/<id>
    錯誤：缺少必填欄位 → 400
    """
    # TODO: 實作
    pass


@recording_bp.route('/recordings', methods=['GET'])
def list_recordings():
    """錄音列表頁面。

    顯示所有歷史錄音，支援搜尋。

    輸入：request.args.get('q') — 搜尋關鍵字（可選）

    處理邏輯：
        1. 若有 q → Recording.search(q)
        2. 否則 → Recording.get_all()
        3. 為每筆錄音取得 Recording.get_marker_count(id)

    Template: templates/recordings/list.html
    """
    # TODO: 實作
    pass


@recording_bp.route('/recordings/<int:id>', methods=['GET'])
def detail(id):
    """錄音詳情 / 回顧頁面。

    播放錄音，顯示標記清單，支援跳轉回聽。

    輸入：URL 參數 id（錄音 ID）

    處理邏輯：
        1. Recording.get_by_id(id)
        2. Marker.get_by_recording(id)
        3. MarkerType.get_all()

    Template: templates/recordings/detail.html
    錯誤：找不到錄音 → 404
    """
    # TODO: 實作
    pass


@recording_bp.route('/recordings/<int:id>/update', methods=['POST'])
def update(id):
    """更新錄音的標題或分類。

    輸入：
        - URL 參數 id
        - request.form['title']
        - request.form['category']

    處理邏輯：Recording.update(id, title, category)
    輸出：重導向至 /recordings/<id>
    錯誤：找不到錄音 → 404
    """
    # TODO: 實作
    pass


@recording_bp.route('/recordings/<int:id>/delete', methods=['POST'])
def delete(id):
    """刪除錄音。

    刪除錄音紀錄、音訊檔案與所有標記。

    輸入：URL 參數 id

    處理邏輯：
        1. Recording.get_by_id(id) 取得檔案路徑
        2. 刪除音訊檔案
        3. Recording.delete(id)（標記因 CASCADE 自動刪除）

    輸出：重導向至 /recordings
    錯誤：找不到錄音 → 404
    """
    # TODO: 實作
    pass


@recording_bp.route('/recordings/<int:id>/download', methods=['GET'])
def download(id):
    """下載錄音音訊檔案。

    輸入：URL 參數 id

    處理邏輯：
        1. Recording.get_by_id(id)
        2. send_file() 回傳音訊檔案

    輸出：音訊檔案下載
    錯誤：找不到錄音或檔案 → 404
    """
    # TODO: 實作
    pass
