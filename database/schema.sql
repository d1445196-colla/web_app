-- ============================================
-- 即時標記錄音系統 — 資料庫 Schema
-- 資料庫引擎：SQLite
-- 建立日期：2026-05-19
-- ============================================

-- 啟用外鍵約束（SQLite 預設不啟用）
PRAGMA foreign_keys = ON;

-- ============================================
-- 1. marker_types（標記種類）
-- 儲存系統預設與使用者自訂的標記種類
-- ============================================
CREATE TABLE IF NOT EXISTS marker_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,                        -- 種類名稱（如「關鍵重點」）
    color       TEXT    NOT NULL DEFAULT '#e94560',      -- 顯示顏色（HEX 色碼）
    icon        TEXT    NOT NULL DEFAULT '🏷',           -- 圖示（Emoji）
    is_default  INTEGER NOT NULL DEFAULT 0,              -- 是否為系統預設（1=是, 0=否）
    sort_order  INTEGER NOT NULL DEFAULT 0,              -- 排序順序
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))  -- 建立時間
);

-- ============================================
-- 2. recordings（錄音紀錄）
-- 儲存每一次錄音的後設資料與檔案路徑
-- ============================================
CREATE TABLE IF NOT EXISTS recordings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,                      -- 錄音標題
    filepath      TEXT    NOT NULL,                      -- 音訊檔案相對路徑
    duration_sec  INTEGER NOT NULL DEFAULT 0,            -- 錄音時長（秒）
    category      TEXT,                                  -- 錄音分類（可為空）
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))  -- 建立時間
);

-- 建立索引：依建立時間排序查詢
CREATE INDEX IF NOT EXISTS idx_recordings_created_at ON recordings(created_at);

-- ============================================
-- 3. markers（標記）
-- 儲存每個錄音中的時間標記與備註
-- ============================================
CREATE TABLE IF NOT EXISTS markers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id   INTEGER NOT NULL,                     -- 所屬錄音 ID
    type_id        INTEGER NOT NULL,                     -- 標記種類 ID
    timestamp_sec  INTEGER NOT NULL,                     -- 標記時間戳（秒）
    note           TEXT,                                 -- 備註（可為空）
    created_at     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),  -- 建立時間

    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id)      REFERENCES marker_types(id) ON DELETE RESTRICT
);

-- 建立索引：依錄音 ID 查詢標記
CREATE INDEX IF NOT EXISTS idx_markers_recording_id ON markers(recording_id);
-- 建立索引：依標記種類篩選
CREATE INDEX IF NOT EXISTS idx_markers_type_id ON markers(type_id);

-- ============================================
-- 4. 預設資料（Seed Data）
-- 系統預設的 5 種標記種類
-- ============================================
INSERT INTO marker_types (name, color, icon, is_default, sort_order) VALUES
    ('關鍵重點', '#e94560', '🔑', 1, 1),
    ('故事',     '#0f3460', '📖', 1, 2),
    ('不清晰',   '#f39c12', '❓', 1, 3),
    ('行動項目', '#2ecc71', '⚡', 1, 4),
    ('靈感',     '#9b59b6', '💡', 1, 5);
