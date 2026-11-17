"""Local medallion pipeline on DuckDB: Bronze -> Silver -> Gold.

Runs the same layering the Fabric design describes (docs/medallion.md) on a laptop, so the data
model, quality rules and gold outputs can be built and tested before a Fabric workspace exists.
The Fabric versions (Lakehouse, PySpark notebooks, pipelines) are not implemented yet.

Usage:
    python local/pipeline.py --input data-generator/output --db local/lottery.duckdb --summary local/summary.json
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import duckdb

SOURCES = {
    "players": "players.csv",
    "games": "games.csv",
    "retail_locations": "retail_locations.csv",
    "transactions": "transactions.csv",
}

# Each rule rejects a row from Silver with a reason. Order matters: the first failing rule wins.
REJECT_RULES = [
    ("missing_or_bad_timestamp", "ts IS NULL"),
    ("non_positive_or_missing_amount", "amount IS NULL OR amount <= 0"),
    ("unknown_player", "player_id IS NULL OR player_id NOT IN (SELECT player_id FROM silver.players)"),
    ("unknown_game", "game_id IS NULL OR game_id NOT IN (SELECT game_id FROM silver.games)"),
    (
        "retail_without_known_location",
        "channel = 'retail' AND (location_id IS NULL OR location_id NOT IN (SELECT location_id FROM silver.locations))",
    ),
]

# Rows that stay in Silver but are flagged for a business owner to review.
WARNING_FLAGS = {
    "purchase_before_signup": "CAST(t.ts AS DATE) < p.signup_date",
    "sale_on_inactive_game": "NOT g.active",
}


def bronze(con: duckdb.DuckDBPyConnection, input_dir: Path, ingested_at: str) -> None:
    """Raw data as delivered: every column as text, plus ingestion time and source file."""
    con.execute("CREATE SCHEMA IF NOT EXISTS bronze")
    for table, filename in SOURCES.items():
        path = (input_dir / filename).as_posix()
        con.execute(
            f"""CREATE OR REPLACE TABLE bronze.{table} AS
                SELECT *, TIMESTAMP '{ingested_at}' AS _ingested_at, '{filename}' AS _source
                FROM read_csv('{path}', all_varchar = true, header = true)"""
        )


def silver(con: duckdb.DuckDBPyConnection) -> None:
    """Typed, deduplicated and validated. Rejected rows go to silver.rejects with a reason."""
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("""CREATE OR REPLACE TABLE silver.players AS
        SELECT DISTINCT TRY_CAST(player_id AS INT) AS player_id, TRY_CAST(signup_date AS DATE) AS signup_date,
               TRY_CAST(birth_year AS INT) AS birth_year, preferred_channel
        FROM bronze.players WHERE TRY_CAST(player_id AS INT) IS NOT NULL""")
    con.execute("""CREATE OR REPLACE TABLE silver.games AS
        SELECT DISTINCT TRY_CAST(game_id AS INT) AS game_id, game_name, game_type,
               TRY_CAST(ticket_price AS DECIMAL(10, 2)) AS ticket_price, lower(active) = 'true' AS active
        FROM bronze.games WHERE TRY_CAST(game_id AS INT) IS NOT NULL""")
    con.execute("""CREATE OR REPLACE TABLE silver.locations AS
        SELECT DISTINCT TRY_CAST(location_id AS INT) AS location_id, location_name, city
        FROM bronze.retail_locations WHERE TRY_CAST(location_id AS INT) IS NOT NULL""")
    # Exact re-deliveries share every column; keep one copy and count the rest.
    con.execute("""CREATE OR REPLACE TEMP TABLE typed AS
        WITH dedup AS (
            SELECT * EXCLUDE (_ingested_at, _source),
                   ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY transaction_ts) AS _rn
            FROM bronze.transactions)
        SELECT transaction_id,
               TRY_CAST(player_id AS INT) AS player_id,
               TRY_CAST(game_id AS INT) AS game_id,
               TRY_CAST(NULLIF(location_id, '') AS INT) AS location_id,   -- '' means "no location"
               channel,
               TRY_CAST(NULLIF(amount, '') AS DECIMAL(10, 2)) AS amount,
               TRY_CAST(NULLIF(transaction_ts, '') AS TIMESTAMP) AS ts,
               _rn
        FROM dedup""")
    case = " ".join(f"WHEN {cond} THEN '{name}'" for name, cond in REJECT_RULES)
    con.execute(f"""CREATE OR REPLACE TEMP TABLE judged AS
        SELECT *, CASE WHEN _rn > 1 THEN 'duplicate_delivery' {case} ELSE NULL END AS reject_reason
        FROM typed""")
    con.execute("""CREATE OR REPLACE TABLE silver.rejects AS
        SELECT * EXCLUDE (_rn) FROM judged WHERE reject_reason IS NOT NULL""")
    flags = ", ".join(f"({cond}) AS {name}" for name, cond in WARNING_FLAGS.items())
    con.execute(f"""CREATE OR REPLACE TABLE silver.transactions AS
        SELECT t.* EXCLUDE (_rn, reject_reason), {flags}
        FROM judged t JOIN silver.players p USING (player_id) JOIN silver.games g USING (game_id)
        WHERE t.reject_reason IS NULL""")


def gold(con: duckdb.DuckDBPyConnection) -> None:
    """Star schema (see sql/ddl, written for the warehouse) plus reporting aggregates."""
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")
    con.execute("CREATE OR REPLACE TABLE gold.dim_player AS SELECT * FROM silver.players")
    con.execute("CREATE OR REPLACE TABLE gold.dim_game AS SELECT * FROM silver.games")
    con.execute("CREATE OR REPLACE TABLE gold.dim_location AS SELECT * FROM silver.locations")
    con.execute("""CREATE OR REPLACE TABLE gold.dim_date AS
        SELECT CAST(strftime(d, '%Y%m%d') AS INT) AS date_id, CAST(d AS DATE) AS full_date,
               year(d) AS year, quarter(d) AS quarter, month(d) AS month,
               isodow(d) AS day_of_week, isodow(d) IN (6, 7) AS is_weekend
        FROM generate_series(DATE '2023-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS g(d)""")
    con.execute("""CREATE OR REPLACE TABLE gold.fact_transaction AS
        SELECT transaction_id, player_id, game_id, location_id,
               CAST(strftime(ts, '%Y%m%d') AS INT) AS date_id, channel, amount, ts AS transaction_ts
        FROM silver.transactions""")
    con.execute("""CREATE OR REPLACE TABLE gold.daily_sales AS
        SELECT d.full_date, f.channel, COUNT(*) AS tickets, SUM(f.amount) AS revenue
        FROM gold.fact_transaction f JOIN gold.dim_date d USING (date_id)
        GROUP BY ALL ORDER BY ALL""")
    con.execute("""CREATE OR REPLACE TABLE gold.game_performance AS
        SELECT g.game_id, g.game_name, g.game_type, g.active, COUNT(*) AS tickets, SUM(f.amount) AS revenue,
               COUNT(DISTINCT f.player_id) AS players
        FROM gold.fact_transaction f JOIN gold.dim_game g USING (game_id)
        GROUP BY ALL ORDER BY revenue DESC""")
    con.execute("""CREATE OR REPLACE TABLE gold.player_activity AS
        SELECT player_id, COUNT(*) AS num_transactions, SUM(amount) AS total_spent,
               MIN(transaction_ts) AS first_purchase, MAX(transaction_ts) AS last_purchase
        FROM gold.fact_transaction GROUP BY player_id""")


def summary(con: duckdb.DuckDBPyConnection) -> dict:
    one = lambda q: con.execute(q).fetchone()[0]  # noqa: E731
    rows = lambda q: [dict(zip([c[0] for c in con.description], r)) for r in con.execute(q).fetchall()]  # noqa: E731
    return {
        "layers": {
            "bronze_transactions": one("SELECT COUNT(*) FROM bronze.transactions"),
            "silver_transactions": one("SELECT COUNT(*) FROM silver.transactions"),
            "rejected": one("SELECT COUNT(*) FROM silver.rejects"),
            "gold_fact_rows": one("SELECT COUNT(*) FROM gold.fact_transaction"),
        },
        "rejects_by_reason": rows("SELECT reject_reason AS reason, COUNT(*) AS rows FROM silver.rejects GROUP BY 1 ORDER BY 2 DESC"),
        "warnings": {name: one(f"SELECT COUNT(*) FROM silver.transactions WHERE {name}") for name in WARNING_FLAGS},
        "dimensions": {t: one(f"SELECT COUNT(*) FROM gold.{t}") for t in ("dim_player", "dim_game", "dim_location", "dim_date")},
        "revenue_by_channel": rows("SELECT channel, SUM(tickets) AS tickets, CAST(SUM(revenue) AS DOUBLE) AS revenue FROM gold.daily_sales GROUP BY 1 ORDER BY 3 DESC"),
        "monthly_revenue": rows("SELECT strftime(full_date, '%Y-%m') AS month, CAST(SUM(revenue) AS DOUBLE) AS revenue FROM gold.daily_sales GROUP BY 1 ORDER BY 1"),
        "top_games": rows("SELECT game_name, game_type, active, tickets, CAST(revenue AS DOUBLE) AS revenue, players FROM gold.game_performance LIMIT 8"),
        "orphan_fact_keys": one("""SELECT COUNT(*) FROM gold.fact_transaction f
            WHERE player_id NOT IN (SELECT player_id FROM gold.dim_player)
               OR game_id NOT IN (SELECT game_id FROM gold.dim_game)
               OR date_id NOT IN (SELECT date_id FROM gold.dim_date)
               OR (location_id IS NOT NULL AND location_id NOT IN (SELECT location_id FROM gold.dim_location))"""),
    }


def run(input_dir: Path, db_path: str = ":memory:") -> tuple[duckdb.DuckDBPyConnection, dict]:
    con = duckdb.connect(db_path)
    bronze(con, input_dir, datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"))
    silver(con)
    gold(con)
    return con, summary(con)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data-generator/output")
    parser.add_argument("--db", default=":memory:")
    parser.add_argument("--summary", default=None)
    args = parser.parse_args()
    if args.db != ":memory:":
        Path(args.db).unlink(missing_ok=True)
    _, result = run(Path(args.input), args.db)
    text = json.dumps(result, indent=2, default=str)
    if args.summary:
        Path(args.summary).write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
