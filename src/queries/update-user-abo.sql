INSERT INTO abo (userID, lvl, trophies, dateSet) VALUES (%s, %s, %s, %s)

ON CONFLICT (userID) DO UPDATE
SET lvl = excluded.lvl, trophies = excluded.trophies, dateSet = excluded.dateSet;