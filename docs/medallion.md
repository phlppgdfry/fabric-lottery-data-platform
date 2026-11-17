# Medallion Architecture

- **Bronze**: raw data as ingested, plus ingestion timestamp and source tag. No transformation.
- **Silver**: deduplicated, validated, typed, standardized business keys.
- **Gold**: business-ready aggregates for reporting (e.g. daily_sales, game_performance, player_activity).

Bronze is retained so Silver/Gold can always be rebuilt from source.

## Local implementation

`local/pipeline.py` builds all three layers on DuckDB:

- **Bronze** keeps every column as text, plus `_ingested_at` and `_source`.
- **Silver** types the data, removes exact re-deliveries and moves invalid rows to
  `silver.rejects` with a reason (bad timestamp, non-positive or missing amount, unknown
  player, unknown game, retail sale without a known location). Rows that are valid but
  suspicious stay, with a flag: `sale_on_inactive_game` needs a review because the game
  dimension only knows the *current* active flag, not when a game was retired (an SCD2
  candidate).
- **Gold** holds the star schema from `sql/ddl` plus `daily_sales`, `game_performance` and
  `player_activity`.
