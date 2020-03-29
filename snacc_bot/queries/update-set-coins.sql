UPDATE
coins
SET
balance = total + %s
WHERE
user_id = %s