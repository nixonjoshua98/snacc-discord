
CREATE TABLE IF NOT EXISTS arena_stats (
arena_stat_id   SERIAL,
user_id         BIGINT,
level           SMALLINT                    DEFAULT 0   CHECK (level >= 0),
trophies        SMALLINT                    DEFAULT 0   CHECK (trophies >= 0),
date_set        TIMESTAMP WITHOUT time zone DEFAULT (now() at time zone 'utc')
);

CREATE table IF NOT EXISTS hangman (
user_id     BIGINT  PRIMARY KEY,
wins        INTEGER DEFAULT 0
);

CREATE table IF NOT EXISTS servers (
server_id       BIGINT  PRIMARY KEY,
default_role    BIGINT  DEFAULT 0,
member_role     BIGINT  DEFAULT 0,
prefix          VARCHAR DEFAULT "!",
display_joins   BOOL    DEFAULT True
);

CREATE table IF NOT EXISTS bank (
user_id BIGINT PRIMARY KEY,
money   BIGINT DEFAULT 1000 CHECK (money >= 0)
);


CREATE TABLE IF NOT EXISTS population (
population_id 	BIGINT      PRIMARY KEY,

-- Money Making Units
farmers 	    SMALLINT 	DEFAULT 0 CHECK (farmers    >= 0),
butchers 	    SMALLINT 	DEFAULT 0 CHECK (butchers   >= 0),
cooks 		    SMALLINT 	DEFAULT 0 CHECK (cooks      >= 0),
bakers 		    SMALLINT 	DEFAULT 0 CHECK (bakers     >= 0),
winemakers 	    SMALLINT 	DEFAULT 0 CHECK (winemakers >= 0),

-- Military Units
peasants        SMALLINT    DEFAULT 0 CHECK (peasants >= 0)
);


CREATE TABLE IF NOT EXISTS empire (
empire_id       BIGINT                      PRIMARY KEY,
name            VARCHAR                     DEFAULT 'My Empire',
last_update     TIMESTAMP WITHOUT time zone DEFAULT (now() at time zone 'utc')
);