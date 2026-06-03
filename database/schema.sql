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

-- ============================================
-- 【記帳系統】8. categories（分類）
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    type        TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ============================================
-- 【記帳系統】9. transactions（交易紀錄）
-- ============================================
CREATE TABLE IF NOT EXISTS transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    type         TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
    amount       REAL    NOT NULL,
    category_id  INTEGER NOT NULL,
    date         TEXT    NOT NULL,
    note         TEXT    NOT NULL DEFAULT '',
    created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);

-- ============================================
-- 【記帳系統】10. reminders（繳費提醒）
-- ============================================
CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    amount      REAL    NOT NULL,
    due_day     INTEGER NOT NULL,
    is_paid     TEXT    NOT NULL DEFAULT 'no' CHECK(is_paid IN ('yes', 'no')),
    paid_date   TEXT,
    note        TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ============================================
-- 【記帳系統】11. templates（常用模板）
-- ============================================
CREATE TABLE IF NOT EXISTS templates (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    type         TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
    amount       REAL    NOT NULL,
    category_id  INTEGER NOT NULL,
    note         TEXT    NOT NULL DEFAULT '',
    created_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at   TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),

    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- ============================================
-- 【記帳系統】12. 預設資料（Seed Data）
-- ============================================
INSERT OR IGNORE INTO categories (name, type) VALUES
    ('薪水',     'income'),
    ('獎金',     'income'),
    ('投資收入', 'income'),
    ('其他收入', 'income'),
    ('餐飲',     'expense'),
    ('交通',     'expense'),
    ('住房',     'expense'),
    ('娛樂',     'expense'),
    ('購物',     'expense'),
    ('醫療',     'expense'),
    ('教育',     'expense'),
    ('其他支出', 'expense');
