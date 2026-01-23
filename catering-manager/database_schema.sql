CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY,
    budget_warning_threshold REAL DEFAULT 0.8,
    budget_alert_threshold REAL DEFAULT 0.9,
    budget_critical_threshold REAL DEFAULT 1.0,
    default_currency TEXT DEFAULT 'RUB',
    language TEXT DEFAULT 'ru',
    theme TEXT DEFAULT 'dark',
    auto_backup_enabled BOOLEAN DEFAULT 1,
    backup_interval_days INTEGER DEFAULT 7,
    reports_format TEXT DEFAULT 'excel',
    created_at TEXT,
    updated_at TEXT
);

-- Добавление индекса для оптимизации поиска
CREATE INDEX IF NOT EXISTS idx_settings_id ON settings(id);
