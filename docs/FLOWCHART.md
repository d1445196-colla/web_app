# 流程圖設計 — 即時標記錄音系統

> **文件版本：** v1.0
> **建立日期：** 2026-05-19
> **依據文件：** [PRD.md](PRD.md)、[ARCHITECTURE.md](ARCHITECTURE.md)

---

## 1. 使用者流程圖（User Flow）

### 1.1 整體操作流程

以下流程圖展示使用者從進入系統到完成錄音回顧的完整操作路徑：

```mermaid
flowchart LR
    A([使用者開啟網頁]) --> B[首頁 — 錄音主頁面]
    
    B --> C{要執行什麼操作？}
    
    C -->|開始錄音| D[點選開始錄音按鈕]
    C -->|查看歷史| E[進入錄音列表頁面]
    C -->|管理標記種類| F[進入標記種類設定]
    
    D --> G["錄音進行中<br/>（波形跳動 + 計時器運轉）"]
    
    G --> H{錄音中操作}
    H -->|標記重點| I[點選標記按鈕]
    I --> J["記錄時間戳 + 種類<br/>（可選輸入備註）"]
    J --> G
    
    H -->|暫停| K[錄音暫停<br/>波形靜止 / 計時器暫停]
    K --> L{繼續或停止？}
    L -->|繼續| G
    L -->|停止| M[結束錄音]
    
    H -->|停止| M
    
    M --> N[錄音儲存表單<br/>輸入標題 / 選分類]
    N --> O{儲存或捨棄？}
    O -->|儲存| P[上傳音訊 + 標記至後端]
    O -->|捨棄| B
    
    P --> Q[錄音詳情 / 回顧頁面]
    
    Q --> R{回顧操作}
    R -->|播放錄音| S[音訊播放器播放]
    R -->|點選標記跳轉| T[跳轉至標記時間點播放]
    R -->|篩選標記| U[依種類篩選標記清單]
    R -->|返回列表| E
    
    E --> V{列表操作}
    V -->|搜尋| W[依標題或分類搜尋]
    V -->|查看詳情| Q
    V -->|刪除| X[二次確認後刪除]
    V -->|下載| Y[下載錄音檔案]
    V -->|返回首頁| B
    
    F --> Z{標記種類管理}
    Z -->|新增| AA[輸入名稱 / 顏色 / 圖示]
    Z -->|編輯| AB[修改既有種類]
    Z -->|刪除| AC[刪除種類]
    Z -->|返回首頁| B
    AA --> F
    AB --> F
    AC --> F
```

### 1.2 錄音核心流程（詳細版）

聚焦於「錄音 + 標記」核心操作的詳細步驟：

```mermaid
flowchart TB
    START([使用者進入錄音主頁]) --> CHECK_MIC{瀏覽器請求<br/>麥克風權限}
    
    CHECK_MIC -->|允許| MIC_READY[麥克風就緒<br/>顯示靜態波形基準線]
    CHECK_MIC -->|拒絕| MIC_DENIED[顯示錯誤提示<br/>無法錄音]
    MIC_DENIED --> CHECK_MIC
    
    MIC_READY --> CLICK_REC[點選「開始錄音 ⏺」]
    
    CLICK_REC --> REC_START["錄音開始<br/>━━━━━━━━━━━━━━━━<br/>✅ MediaRecorder 啟動<br/>✅ 波形開始跳動<br/>✅ 計時器開始計時<br/>✅ 標記按鈕啟用"]
    
    REC_START --> REC_LOOP{使用者操作}
    
    REC_LOOP -->|點選標記按鈕| MARK["建立標記<br/>━━━━━━━━━━━━━━━━<br/>📌 記錄當前時間戳<br/>🏷 記錄標記種類<br/>✨ 按鈕漣漪動畫<br/>🔢 計數器 +1"]
    MARK --> NOTE_INPUT{輸入備註？}
    NOTE_INPUT -->|是| WRITE_NOTE[輸入簡短備註]
    NOTE_INPUT -->|否 / 跳過| MARK_DONE[標記完成<br/>波形上顯示旗標]
    WRITE_NOTE --> MARK_DONE
    MARK_DONE --> REC_LOOP
    
    REC_LOOP -->|按暫停 ⏸| PAUSE["錄音暫停<br/>━━━━━━━━━━━━━━━━<br/>⏸ 波形靜止灰色<br/>⏸ 計時器暫停閃爍"]
    PAUSE --> RESUME_OR_STOP{繼續或停止？}
    RESUME_OR_STOP -->|繼續 ▶| REC_START
    RESUME_OR_STOP -->|停止 ⏹| REC_STOP
    
    REC_LOOP -->|按停止 ⏹| REC_STOP
    
    REC_STOP["錄音結束<br/>━━━━━━━━━━━━━━━━<br/>🛑 MediaRecorder 停止<br/>📦 產生音訊 Blob<br/>⏱ 計時器顯示最終時長"]
    
    REC_STOP --> SAVE_FORM["儲存表單<br/>━━━━━━━━━━━━━━━━<br/>📝 輸入錄音標題<br/>🗂 選擇分類<br/>📊 顯示標記統計"]
    
    SAVE_FORM --> SAVE_DECIDE{儲存或捨棄？}
    SAVE_DECIDE -->|儲存| UPLOAD["上傳至後端<br/>━━━━━━━━━━━━━━━━<br/>📤 音訊檔案<br/>📋 標記 JSON<br/>📝 標題與分類"]
    SAVE_DECIDE -->|捨棄| DISCARD[捨棄錄音<br/>返回首頁]
    
    UPLOAD --> DETAIL([進入錄音詳情頁])
```

---

## 2. 系統序列圖（Sequence Diagram）

### 2.1 核心流程：錄音儲存

描述使用者完成錄音並儲存的完整資料流：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (JS)
    participant Flask as Flask Route
    participant Model as Model 層
    participant DB as SQLite
    participant FS as 檔案系統

    User->>Browser: 進入首頁
    Browser->>Flask: GET /
    Flask-->>Browser: 渲染 index.html（錄音主頁）

    User->>Browser: 允許麥克風權限
    Browser->>Browser: navigator.mediaDevices.getUserMedia()

    User->>Browser: 點選「開始錄音 ⏺」
    Browser->>Browser: MediaRecorder.start()
    Browser->>Browser: AnalyserNode 開始分析音量
    Browser->>Browser: Canvas 開始繪製波形
    Browser->>Browser: setInterval 開始計時

    loop 錄音進行中
        User->>Browser: 點選標記按鈕（如「🔑 關鍵重點」）
        Browser->>Browser: markers.push({timestamp, type, note})
        Browser->>Browser: 波形上繪製旗標 + 按鈕漣漪動畫
    end

    User->>Browser: 點選「停止錄音 ⏹」
    Browser->>Browser: MediaRecorder.stop()
    Browser->>Browser: 產生音訊 Blob
    Browser->>Browser: 計時器停止

    User->>Browser: 輸入標題「第三次訪談」，選擇分類
    User->>Browser: 點選「儲存」

    Browser->>Flask: POST /recordings<br/>FormData: audio_file + markers_json + title + category
    
    Flask->>FS: 儲存音訊檔案至 static/uploads/rec_20260519_211300.webm
    Flask->>Model: Recording.create(title, filepath, duration, category)
    Model->>DB: INSERT INTO recordings (title, filepath, duration, category, created_at)
    DB-->>Model: recording_id = 42
    Model-->>Flask: Recording 物件

    Flask->>Model: Marker.create_batch(recording_id=42, markers_list)
    Model->>DB: INSERT INTO markers (recording_id, type_id, timestamp_sec, note) × N
    DB-->>Model: 成功
    Model-->>Flask: Marker 物件列表

    Flask-->>Browser: 302 Redirect → /recordings/42
    Browser->>Flask: GET /recordings/42
    Flask->>Model: Recording.get(42)
    Model->>DB: SELECT * FROM recordings WHERE id=42
    DB-->>Model: 錄音資料
    Flask->>Model: Marker.get_by_recording(42)
    Model->>DB: SELECT * FROM markers WHERE recording_id=42
    DB-->>Model: 標記清單
    Flask-->>Browser: 渲染 detail.html（錄音詳情頁）
    Browser-->>User: 顯示錄音回顧頁面
```

### 2.2 標記跳轉播放

描述使用者在回顧頁面點選標記跳轉到特定時間點的流程：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (JS)
    participant Audio as HTML5 Audio Player

    User->>Browser: 進入錄音詳情頁
    Note over Browser: 頁面載入錄音播放器 + 標記清單

    User->>Browser: 點選標記「🔑 關鍵重點 @ 05:23」
    Browser->>Audio: audio.currentTime = 323
    Browser->>Audio: audio.play()
    Audio-->>User: 從 05:23 開始播放錄音

    User->>Browser: 點選另一標記「📖 故事 @ 12:07」
    Browser->>Audio: audio.currentTime = 727
    Audio-->>User: 跳轉至 12:07 播放

    User->>Browser: 依種類篩選「只看 ❓ 不清晰」
    Browser->>Browser: DOM 過濾，僅顯示不清晰標記
    Browser-->>User: 清單只剩不清晰標記
```

### 2.3 標記種類管理

描述使用者自訂標記種類的 CRUD 流程：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Model 層
    participant DB as SQLite

    User->>Browser: 進入標記種類管理頁
    Browser->>Flask: GET /settings/markers
    Flask->>Model: MarkerType.get_all()
    Model->>DB: SELECT * FROM marker_types
    DB-->>Model: 標記種類清單
    Model-->>Flask: MarkerType 列表
    Flask-->>Browser: 渲染 marker_types.html

    User->>Browser: 點選「新增標記種類」
    User->>Browser: 輸入名稱「📎 引用」，選顏色 #3498db
    User->>Browser: 點選「確認新增」
    Browser->>Flask: POST /settings/markers<br/>name=引用 & color=#3498db & icon=📎
    Flask->>Model: MarkerType.create(name, color, icon)
    Model->>DB: INSERT INTO marker_types (name, color, icon)
    DB-->>Model: type_id
    Flask-->>Browser: 302 Redirect → /settings/markers
    Browser-->>User: 重新載入頁面，顯示新種類

    User->>Browser: 點選「刪除」某個標記種類
    Browser-->>User: 彈出確認對話框
    User->>Browser: 確認刪除
    Browser->>Flask: POST /settings/markers/5/delete
    Flask->>Model: MarkerType.delete(5)
    Model->>DB: DELETE FROM marker_types WHERE id=5
    Flask-->>Browser: 302 Redirect → /settings/markers
```

### 2.4 錄音列表管理

描述使用者瀏覽、搜尋與刪除錄音的流程：

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器
    participant Flask as Flask Route
    participant Model as Model 層
    participant DB as SQLite
    participant FS as 檔案系統

    User->>Browser: 點選導覽列「錄音列表」
    Browser->>Flask: GET /recordings
    Flask->>Model: Recording.get_all()
    Model->>DB: SELECT * FROM recordings ORDER BY created_at DESC
    DB-->>Model: 錄音清單
    Flask-->>Browser: 渲染 list.html

    User->>Browser: 搜尋「訪談」
    Browser->>Flask: GET /recordings?q=訪談
    Flask->>Model: Recording.search("訪談")
    Model->>DB: SELECT * FROM recordings WHERE title LIKE '%訪談%'
    DB-->>Model: 篩選結果
    Flask-->>Browser: 渲染 list.html（篩選後）

    User->>Browser: 點選某錄音的「刪除」
    Browser-->>User: 彈出二次確認
    User->>Browser: 確認刪除
    Browser->>Flask: POST /recordings/42/delete
    Flask->>Model: Marker.delete_by_recording(42)
    Model->>DB: DELETE FROM markers WHERE recording_id=42
    Flask->>Model: Recording.delete(42)
    Model->>DB: DELETE FROM recordings WHERE id=42
    Flask->>FS: 刪除 static/uploads/rec_xxx.webm
    Flask-->>Browser: 302 Redirect → /recordings
    Browser-->>User: 重新載入錄音列表
```

---

## 3. 功能清單對照表

| 功能 | 頁面 | URL 路徑 | HTTP 方法 | 說明 |
|------|------|---------|-----------|------|
| 錄音主頁面 | 首頁 | `/` | `GET` | 顯示錄音介面（波形 + 計時器 + 標記 + 控制按鈕） |
| 儲存錄音 | — | `/recordings` | `POST` | 接收音訊檔案 + 標記 JSON，儲存至資料庫與檔案系統 |
| 錄音列表 | 列表頁 | `/recordings` | `GET` | 顯示所有歷史錄音，支援搜尋 |
| 錄音詳情 | 詳情頁 | `/recordings/<id>` | `GET` | 播放錄音 + 顯示標記清單 + 跳轉回聽 |
| 刪除錄音 | — | `/recordings/<id>/delete` | `POST` | 刪除錄音及其標記（需二次確認） |
| 下載錄音 | — | `/recordings/<id>/download` | `GET` | 下載錄音音訊檔案 |
| 編輯標記 | — | `/markers/<id>` | `POST` | 更新標記備註 |
| 刪除標記 | — | `/markers/<id>/delete` | `POST` | 刪除單一標記 |
| 標記種類列表 | 設定頁 | `/settings/markers` | `GET` | 顯示所有標記種類 |
| 新增標記種類 | — | `/settings/markers` | `POST` | 新增自訂標記種類 |
| 編輯標記種類 | — | `/settings/markers/<id>` | `POST` | 修改標記種類（名稱、顏色、圖示） |
| 刪除標記種類 | — | `/settings/markers/<id>/delete` | `POST` | 刪除標記種類 |
| **API** 錄音列表 | — | `/api/recordings` | `GET` | JSON 格式回傳所有錄音後設資料 |
| **API** 錄音詳情 | — | `/api/recordings/<id>` | `GET` | JSON 格式回傳單一錄音 + 標記資料 |
| **API** 標記列表 | — | `/api/recordings/<id>/markers` | `GET` | JSON 格式回傳該錄音的所有標記 |

---

## 4. 頁面導覽地圖

```mermaid
flowchart TB
    NAV["導覽列（所有頁面共用）"]
    
    NAV --> HOME["首頁 / 錄音主頁<br/>GET /"]
    NAV --> LIST["錄音列表<br/>GET /recordings"]
    NAV --> SETTINGS["標記種類管理<br/>GET /settings/markers"]
    
    HOME -->|停止錄音後儲存| SAVE["POST /recordings<br/>（上傳音訊 + 標記）"]
    SAVE -->|成功| DETAIL
    
    LIST --> DETAIL["錄音詳情 / 回顧<br/>GET /recordings/id"]
    LIST -->|搜尋| LIST
    LIST -->|刪除| LIST
    
    DETAIL -->|返回| LIST
    SETTINGS -->|返回| HOME

    style HOME fill:#e94560,stroke:#1a1a2e,color:#fff
    style LIST fill:#0f3460,stroke:#1a1a2e,color:#fff
    style DETAIL fill:#533483,stroke:#1a1a2e,color:#fff
    style SETTINGS fill:#16213e,stroke:#1a1a2e,color:#fff
```

---

> **下一步：** 流程圖確認後，請進入資料庫設計階段（`/db-design`），定義資料表結構與關聯。
