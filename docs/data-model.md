# Data Model

## Star schema

```
        dim_player
             |
dim_game -- fact_transaction -- dim_location
             |
         dim_date
```

- `fact_transaction` -- grain: one row per ticket purchase (`transaction_id`).
  Holds `amount`, the price actually charged at purchase time -- not looked
  up from `dim_game.ticket_price`, because that price can change over time
  and facts must preserve history as it happened.
- `dim_player` -- signup date, birth year, preferred channel
- `dim_game` -- name, type, current ticket price, active flag
- `dim_location` -- retail location name and city (NULL on the fact for
  online/mobile_app channels)
- `dim_date` -- generated calendar dimension (year, quarter, month,
  day_of_week, is_weekend), not sourced from raw data

## Why star schema over one flat table

- Avoids repeating descriptive attributes (e.g. city name) on every fact row
- A dimension attribute change (e.g. a player's preferred channel) updates
  one row instead of thousands of transaction rows
- Keeps the fact table narrow and fast to scan/aggregate

## Fact vs dimension rule of thumb

A fact table holds measurements that were true at the moment of the event.
A dimension table holds descriptive attributes that hold *now*, and can
change without rewriting historical facts (see: Slowly Changing Dimensions,
covered later).

DDL: see `sql/ddl/`. Example queries (GROUP BY/HAVING, window functions,
dedup pattern): see `sql/queries/player_activity.sql`.
