-- Fact table: grain = one row per ticket purchase (transaction_id).
-- amount is stored here (not looked up from dim_game.ticket_price) because it
-- reflects what was actually charged at purchase time -- dim_game.ticket_price
-- can change later without rewriting history. See docs/data-model.md.

CREATE TABLE fact_transaction (
    transaction_id      UUID PRIMARY KEY,
    player_id           INT NOT NULL REFERENCES dim_player(player_id),
    game_id             INT NOT NULL REFERENCES dim_game(game_id),
    location_id         INT REFERENCES dim_location(location_id),  -- NULL for online/mobile_app
    date_id             INT NOT NULL REFERENCES dim_date(date_id),
    channel              VARCHAR(20) NOT NULL,
    amount               NUMERIC(10, 2) NOT NULL,
    transaction_ts       TIMESTAMP NOT NULL
);

CREATE INDEX idx_fact_transaction_player ON fact_transaction(player_id);
CREATE INDEX idx_fact_transaction_game ON fact_transaction(game_id);
CREATE INDEX idx_fact_transaction_date ON fact_transaction(date_id);
