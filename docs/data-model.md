# Data Model

## Fact / Dimension design (Week 1)

- `fact_transaction` — one row per ticket purchase (grain: transaction_id)
- `dim_player`
- `dim_game`
- `dim_location`
- `dim_date`
- `dim_channel`

To be expanded as the star schema is implemented in `sql/ddl/`.
