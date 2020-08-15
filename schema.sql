
CREATE TABLE IF NOT EXISTS arena_stats (
arena_stat_id   SERIAL,
user_id         BIGINT,
level           SMALLINT                    DEFAULT 0   CHECK (level >= 0),
trophies        SMALLINT                    DEFAULT 0   CHECK (trophies >= 0),
date_set        TIMESTAMP WITHOUT time zone DEFAULT (now() at time zone 'utc')
);