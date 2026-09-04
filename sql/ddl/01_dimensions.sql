-- Dimension tables: describe context (who, what, where, when).
-- Attributes here reflect "current" state, except where noted (SCD comes later).

CREATE TABLE dim_player (
    player_id           INT PRIMARY KEY,
    signup_date         DATE NOT NULL,
    birth_year          INT,
    preferred_channel    VARCHAR(20)
);

CREATE TABLE dim_game (
    game_id             INT PRIMARY KEY,
    game_name           VARCHAR(100) NOT NULL,
    game_type           VARCHAR(30) NOT NULL,   -- scratch_card / draw_game / instant_win
    ticket_price        NUMERIC(10, 2) NOT NULL,
    active               BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE dim_location (
    location_id         INT PRIMARY KEY,
    location_name       VARCHAR(100) NOT NULL,
    city                 VARCHAR(50)
);

-- dim_date is generated, not sourced from raw data (see 02_populate_dim_date.sql)
CREATE TABLE dim_date (
    date_id             INT PRIMARY KEY,        -- YYYYMMDD as integer
    full_date            DATE NOT NULL UNIQUE,
    year                 INT NOT NULL,
    quarter              INT NOT NULL,
    month                INT NOT NULL,
    day_of_week          INT NOT NULL,           -- 1 = Monday ... 7 = Sunday
    is_weekend           BOOLEAN NOT NULL
);
