from sqlalchemy import inspect, text
from app.core.database import engine


MIGRATIONS = {
    "001_owner_and_audio": [
        "ALTER TABLE profiles ADD COLUMN owner_user_id VARCHAR DEFAULT 'default'",
        "CREATE INDEX IF NOT EXISTS ix_profiles_owner_user_id ON profiles(owner_user_id)",
        "UPDATE profiles SET owner_user_id = 'default' WHERE owner_user_id IS NULL",
        "CREATE TABLE IF NOT EXISTS audio_recordings (id VARCHAR PRIMARY KEY, owner_user_id VARCHAR NOT NULL, session_id VARCHAR, turn_id VARCHAR, file_path VARCHAR NOT NULL, content_type VARCHAR NOT NULL, size_bytes INTEGER NOT NULL, duration_ms INTEGER, created_at DATETIME NOT NULL, retention_at DATETIME)",
        "CREATE INDEX IF NOT EXISTS ix_audio_recordings_owner_user_id ON audio_recordings(owner_user_id)",
        "CREATE INDEX IF NOT EXISTS ix_audio_recordings_session_id ON audio_recordings(session_id)",
        "CREATE INDEX IF NOT EXISTS ix_audio_recordings_retention_at ON audio_recordings(retention_at)",
    ],
    "002_resource_owner_columns": [
        "ALTER TABLE sessions ADD COLUMN owner_user_id VARCHAR DEFAULT 'default'",
        "ALTER TABLE turns ADD COLUMN owner_user_id VARCHAR DEFAULT 'default'",
        "ALTER TABLE mistakes ADD COLUMN owner_user_id VARCHAR DEFAULT 'default'",
        "ALTER TABLE daily_stats ADD COLUMN owner_user_id VARCHAR DEFAULT 'default'",
        "UPDATE sessions SET owner_user_id = COALESCE((SELECT owner_user_id FROM profiles WHERE profiles.id = sessions.user_id), 'default') WHERE owner_user_id IS NULL",
        "UPDATE turns SET owner_user_id = COALESCE((SELECT owner_user_id FROM sessions WHERE sessions.id = turns.session_id), 'default') WHERE owner_user_id IS NULL",
        "UPDATE mistakes SET owner_user_id = COALESCE((SELECT owner_user_id FROM profiles WHERE profiles.id = mistakes.user_id), 'default') WHERE owner_user_id IS NULL",
        "UPDATE daily_stats SET owner_user_id = COALESCE((SELECT owner_user_id FROM profiles WHERE profiles.id = daily_stats.user_id), 'default') WHERE owner_user_id IS NULL",
        "CREATE INDEX IF NOT EXISTS ix_sessions_owner_user_id ON sessions(owner_user_id)",
        "CREATE INDEX IF NOT EXISTS ix_turns_owner_user_id ON turns(owner_user_id)",
        "CREATE INDEX IF NOT EXISTS ix_mistakes_owner_user_id ON mistakes(owner_user_id)",
        "CREATE INDEX IF NOT EXISTS ix_daily_stats_owner_user_id ON daily_stats(owner_user_id)",
    ],
    "003_turn_client_turn_id": [
        "ALTER TABLE turns ADD COLUMN client_turn_id VARCHAR",
        "CREATE INDEX IF NOT EXISTS ix_turns_client_turn_id ON turns(client_turn_id)",
    ],
    "004_mistake_learning_state": [
        "ALTER TABLE mistakes ADD COLUMN error_type VARCHAR DEFAULT 'grammar'",
        "ALTER TABLE mistakes ADD COLUMN subtype VARCHAR DEFAULT 'general'",
        "ALTER TABLE mistakes ADD COLUMN successful_reuse_count INTEGER DEFAULT 0",
        "ALTER TABLE mistakes ADD COLUMN next_review_at DATETIME",
        "ALTER TABLE mistakes ADD COLUMN last_reviewed_at DATETIME",
        "ALTER TABLE mistakes ADD COLUMN mastery_state VARCHAR DEFAULT 'learning'",
        "ALTER TABLE mistakes ADD COLUMN example_sentence TEXT",
        "UPDATE mistakes SET error_type = COALESCE(error_type, category), subtype = COALESCE(subtype, 'general'), mastery_state = COALESCE(mastery_state, CASE WHEN resolved THEN 'mastered' ELSE 'learning' END) WHERE error_type IS NULL OR subtype IS NULL OR mastery_state IS NULL",
        "CREATE INDEX IF NOT EXISTS ix_mistakes_next_review_at ON mistakes(next_review_at)",
        "CREATE INDEX IF NOT EXISTS ix_mistakes_mastery_state ON mistakes(mastery_state)",
    ],
    "005_adaptive_plan_cache": [
        "CREATE TABLE IF NOT EXISTS adaptive_plans (id VARCHAR PRIMARY KEY, owner_user_id VARCHAR NOT NULL, plan_date VARCHAR NOT NULL, payload_json TEXT NOT NULL, evidence_count VARCHAR DEFAULT '0', created_at DATETIME NOT NULL)",
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_adaptive_plan_owner_date ON adaptive_plans(owner_user_id, plan_date)",
        "CREATE INDEX IF NOT EXISTS ix_adaptive_plans_owner_user_id ON adaptive_plans(owner_user_id)",
    ],
    "006_time_metric_dimensions": [
        "ALTER TABLE sessions ADD COLUMN actual_speaking_ms INTEGER DEFAULT 0",
        "ALTER TABLE sessions ADD COLUMN audio_duration_ms INTEGER DEFAULT 0",
        "ALTER TABLE sessions ADD COLUMN typing_practice_ms INTEGER DEFAULT 0",
        "ALTER TABLE sessions ADD COLUMN session_duration_ms INTEGER DEFAULT 0",
    ],
    "007_scoring_calibration_qa": [
        "CREATE TABLE IF NOT EXISTS evaluation_feedback (id VARCHAR PRIMARY KEY, session_id VARCHAR NOT NULL, owner_user_id VARCHAR NOT NULL, flag VARCHAR NOT NULL, comment TEXT, scoring_version VARCHAR NOT NULL DEFAULT 'phase8-v1', created_at DATETIME NOT NULL)",
        "CREATE INDEX IF NOT EXISTS ix_evaluation_feedback_session_id ON evaluation_feedback(session_id)",
        "CREATE INDEX IF NOT EXISTS ix_evaluation_feedback_owner_user_id ON evaluation_feedback(owner_user_id)",
        "CREATE TABLE IF NOT EXISTS calibration_samples (id VARCHAR PRIMARY KEY, sample_key VARCHAR NOT NULL UNIQUE, level VARCHAR NOT NULL, transcript TEXT NOT NULL, human_fc FLOAT, human_lr FLOAT, human_gra FLOAT, human_pronunciation FLOAT, ai_payload_json TEXT, consented VARCHAR NOT NULL DEFAULT 'false', created_at DATETIME NOT NULL)",
    ],
    "008_controlled_pilot": [
        "CREATE TABLE IF NOT EXISTS pilot_runs (id VARCHAR PRIMARY KEY, owner_user_id VARCHAR NOT NULL, participant_code VARCHAR NOT NULL, consent_audio BOOLEAN NOT NULL DEFAULT 0, consent_feedback BOOLEAN NOT NULL DEFAULT 0, status VARCHAR NOT NULL DEFAULT 'active', created_at DATETIME NOT NULL, completed_at DATETIME)",
        "CREATE INDEX IF NOT EXISTS ix_pilot_runs_owner_user_id ON pilot_runs(owner_user_id)",
        "CREATE TABLE IF NOT EXISTS pilot_events (id VARCHAR PRIMARY KEY, pilot_run_id VARCHAR NOT NULL, owner_user_id VARCHAR NOT NULL, task_key VARCHAR NOT NULL, outcome VARCHAR NOT NULL, help_used BOOLEAN NOT NULL DEFAULT 0, understood_quote TEXT, created_at DATETIME NOT NULL)",
        "CREATE INDEX IF NOT EXISTS ix_pilot_events_pilot_run_id ON pilot_events(pilot_run_id)",
        "CREATE TABLE IF NOT EXISTS pilot_feedback (id VARCHAR PRIMARY KEY, pilot_run_id VARCHAR NOT NULL UNIQUE, owner_user_id VARCHAR NOT NULL, next_action_clear INTEGER NOT NULL, correction_useful INTEGER NOT NULL, score_too_certain INTEGER NOT NULL, would_return INTEGER NOT NULL, free_text TEXT, created_at DATETIME NOT NULL)",
    ],
}


def run_migrations() -> None:
    inspector = inspect(engine)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE IF NOT EXISTS schema_migrations (version VARCHAR PRIMARY KEY, applied_at DATETIME NOT NULL)"))
        applied = {row[0] for row in connection.execute(text("SELECT version FROM schema_migrations"))}
        for version, statements in MIGRATIONS.items():
            if version in applied:
                continue
            for statement in statements:
                try:
                    connection.execute(text(statement))
                except Exception as exc:
                    # SQLite cannot add an already-existing column; the version marker
                    # still makes this idempotent after an older partial startup.
                    if "ADD COLUMN" in statement and "duplicate column name" in str(exc).lower():
                        continue
                    if "ADD COLUMN" not in statement or "owner_user_id" not in statement:
                        raise
            connection.execute(text("INSERT INTO schema_migrations(version, applied_at) VALUES (:version, CURRENT_TIMESTAMP)"), {"version": version})
