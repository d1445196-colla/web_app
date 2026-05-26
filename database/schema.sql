-- ============================================================
-- 語音轉寫與 API 整合系統 — SQLite Schema
-- ============================================================
-- 執行方式：sqlite3 instance/database.db < database/schema.sql
-- ============================================================

-- 啟用外鍵約束（SQLite 預設關閉）
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------
-- 1. recordings — 錄音紀錄表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS recordings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT    NOT NULL,                          -- 原始上傳檔名
    stored_filename   TEXT    NOT NULL,                          -- UUID 重新命名後的檔名
    file_path         TEXT    NOT NULL,                          -- 伺服器端儲存路徑
    file_size         INTEGER NOT NULL,                          -- 檔案大小 (bytes)
    mime_type         TEXT    NOT NULL,                          -- MIME 類型
    duration          REAL    DEFAULT NULL,                      -- 音訊時長 (秒)
    full_text         TEXT    DEFAULT NULL,                      -- 完整轉寫文字
    status            TEXT    NOT NULL DEFAULT 'pending',        -- pending/processing/completed/failed
    error_message     TEXT    DEFAULT NULL,                      -- 錯誤訊息
    language          TEXT    DEFAULT NULL,                      -- 偵測到的語言代碼
    created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    completed_at      TEXT    DEFAULT NULL
);

-- -----------------------------------------------------------
-- 2. segments — 轉寫段落表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS segments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id    INTEGER NOT NULL,                            -- 所屬錄音紀錄
    segment_index   INTEGER NOT NULL,                            -- 段落順序索引
    start_time      REAL    NOT NULL,                            -- 起始時間 (秒)
    end_time        REAL    NOT NULL,                            -- 結束時間 (秒)
    text            TEXT    NOT NULL,                            -- 轉寫文字

    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE
);

-- 建立索引：加速依 recording_id 查詢段落
CREATE INDEX IF NOT EXISTS idx_segments_recording_id ON segments(recording_id);

-- -----------------------------------------------------------
-- 3. markers — 即時標記表
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS markers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id    INTEGER NOT NULL,                            -- 所屬錄音紀錄
    segment_id      INTEGER DEFAULT NULL,                        -- 對齊到的段落 (轉寫後填入)
    marker_time     REAL    NOT NULL,                            -- 標記時間點 (秒)
    label           TEXT    DEFAULT '',                           -- 標記備註文字
    created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE,
    FOREIGN KEY (segment_id)   REFERENCES segments(id)   ON DELETE SET NULL
);

-- 建立索引：加速依 recording_id 查詢標記
CREATE INDEX IF NOT EXISTS idx_markers_recording_id ON markers(recording_id);
