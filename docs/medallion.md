# Medallion Architecture

- **Bronze**: raw data as ingested, plus ingestion timestamp and source tag. No transformation.
- **Silver**: deduplicated, validated, typed, standardized business keys.
- **Gold**: business-ready aggregates for reporting (e.g. daily_sales, game_performance, player_activity).

Bronze is retained so Silver/Gold can always be rebuilt from source.
