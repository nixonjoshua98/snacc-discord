CREATE table IF NOT EXISTS server_config (
serverID BIGINT PRIMARY KEY,

prefix VARCHAR(255),

channels JSON,
roles JSON
);