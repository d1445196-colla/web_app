-- ============================================
-- 即時標記錄音系統 + 語音轉寫系統 — 資料庫 Schema
-- 資料庫引擎：SQLite
-- ============================================

-- 啟用外鍵約束（SQLite 預設不啟用）
PRAGMA foreign_keys = ON;

-- ============================================
-- 【錄音系統】1. marker_types（標記種類）
-- ============================================
CREATE TABLE IF NOT EXISTS marker_types (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    color       TEXT    NOT NULL DEFAULT '#e94560',
    icon        TEXT    NOT NULL DEFAULT '🏷',
    is_default  INTEGER NOT NULL DEFAULT 0,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ============================================
-- 【錄音系統】2. recordings（錄音紀錄）
-- ============================================
CREATE TABLE IF NOT EXISTS recordings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    filepath      TEXT    NOT NULL,
    duration_sec  INTEGER NOT NULL DEFAULT 0,
    category      TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_recordings_created_at ON recordings(created_at);

-- ============================================
-- 【錄音系統】3. markers（標記）
-- ============================================
CREATE TABLE IF NOT EXISTS markers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    recording_id   INTEGER NOT NULL,
    type_id        INTEGER NOT NULL,
    timestamp_sec  INTEGER NOT NULL,
    note           TEXT,
    created_at     TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (recording_id) REFERENCES recordings(id) ON DELETE CASCADE,
    FOREIGN KEY (type_id)      REFERENCES marker_types(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_markers_recording_id ON markers(recording_id);
CREATE INDEX IF NOT EXISTS idx_markers_type_id ON markers(type_id);

-- ============================================
-- 【錄音系統】4. 預設資料（Seed Data）
-- ============================================
INSERT OR IGNORE INTO marker_types (name, color, icon, is_default, sort_order) VALUES
    ('關鍵重點', '#e94560', '🔑', 1, 1),
    ('故事',     '#0f3460', '📖', 1, 2),
    ('不清晰',   '#f39c12', '❓', 1, 3),
    ('行動項目', '#2ecc71', '⚡', 1, 4),
    ('靈感',     '#9b59b6', '💡', 1, 5);

-- ============================================
-- 【轉寫系統】5. transcriptions（轉寫紀錄）
-- ============================================
CREATE TABLE IF NOT EXISTS transcriptions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    original_filename TEXT    NOT NULL,
    stored_filename   TEXT    NOT NULL,
    file_path         TEXT    NOT NULL,
    file_size         INTEGER NOT NULL,
    mime_type         TEXT    NOT NULL,
    duration          REAL    DEFAULT NULL,
    full_text         TEXT    DEFAULT NULL,
    status            TEXT    NOT NULL DEFAULT 'pending',
    error_message     TEXT    DEFAULT NULL,
    language          TEXT    DEFAULT NULL,
    created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    completed_at      TEXT    DEFAULT NULL
);

-- ============================================
-- 【轉寫系統】6. transcription_segments（轉寫段落）
-- ============================================
CREATE TABLE IF NOT EXISTS transcription_segments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    transcription_id  INTEGER NOT NULL,
    segment_index     INTEGER NOT NULL,
    start_time        REAL    NOT NULL,
    end_time          REAL    NOT NULL,
    text              TEXT    NOT NULL,

    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tseg_transcription_id ON transcription_segments(transcription_id);

-- ============================================
-- 【轉寫系統】7. transcription_markers（轉寫標記）
-- ============================================
CREATE TABLE IF NOT EXISTS transcription_markers (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    transcription_id  INTEGER NOT NULL,
    segment_id        INTEGER DEFAULT NULL,
    marker_time       REAL    NOT NULL,
    label             TEXT    DEFAULT '',
    created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (segment_id)       REFERENCES transcription_segments(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tmarker_transcription_id ON transcription_markers(transcription_id);
