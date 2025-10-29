-- migrate:up

CREATE TABLE secrets (
    name VARCHAR(255) PRIMARY KEY,
    content BYTEA NOT NULL
);

-- migrate:down

DROP TABLE secrets;
