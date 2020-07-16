SET PGUSER=postgres
SET PGPASSWORD=postgres

psql -U postgres -w -c "DROP DATABASE snaccbot;"

call heroku pg:pull DATABASE_URL snaccbot -a snacc-bot

pg_dump -d snaccbot -w -f "D:\Program Files\OneDrive\Databases\snaccbot.sql"