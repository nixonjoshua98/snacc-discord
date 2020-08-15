
CREATE TABLE IF NOT EXISTS arena_stats (
arena_stat_id   SERIAL,
user_id         BIGINT,
level           SMALLINT                    DEFAULT 0   CHECK (level >= 0),
trophies        SMALLINT                    DEFAULT 0   CHECK (trophies >= 0),
date_set        TIMESTAMP WITHOUT time zone DEFAULT (now() at time zone 'utc')
);


CREATE TABLE IF NOT EXISTS population (
population_id 	BIGINT      PRIMARY KEY,

-- Money Making Units
farmers 	    SMALLINT 	DEFAULT 0 CHECK (farmers        >= 0),
butchers 	    SMALLINT 	DEFAULT 0 CHECK (butchers       >= 0),
cooks 		    SMALLINT 	DEFAULT 0 CHECK (cooks          >= 0),
bakers 		    SMALLINT 	DEFAULT 0 CHECK (bakers         >= 0),
winemakers 	    SMALLINT 	DEFAULT 0 CHECK (winemakers     >= 0),
blacksmiths     SMALLINT 	DEFAULT 0 CHECK (blacksmiths    >= 0),
taylors 	    SMALLINT 	DEFAULT 0 CHECK (taylors        >= 0),
stonemason 	    SMALLINT 	DEFAULT 0 CHECK (stonemason     >= 0),
weaver 	        SMALLINT 	DEFAULT 0 CHECK (weaver         >= 0),
shoemakers      SMALLINT 	DEFAULT 0 CHECK (shoemakers     >= 0),
falconers       SMALLINT 	DEFAULT 0 CHECK (falconers      >= 0),

-- Military Units
peasants        SMALLINT    DEFAULT 0 CHECK (peasants   >= 0),
soldiers        SMALLINT    DEFAULT 0 CHECK (soldiers   >= 0),
warriors        SMALLINT    DEFAULT 0 CHECK (warriors   >= 0),
spearmen        SMALLINT    DEFAULT 0 CHECK (spearmen   >= 0),
knights         SMALLINT    DEFAULT 0 CHECK (knights    >= 0),
archers         SMALLINT    DEFAULT 0 CHECK (archers    >= 0)
);