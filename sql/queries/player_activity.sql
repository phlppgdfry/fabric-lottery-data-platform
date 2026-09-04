-- Players with more than 5 transactions: total spend and transaction count.
-- Demonstrates GROUP BY + HAVING (HAVING filters groups, WHERE would run too
-- early -- before the aggregates exist).
SELECT
    player_id,
    SUM(amount)  AS total_spent,
    COUNT(*)     AS num_transactions
FROM fact_transaction
GROUP BY player_id
HAVING COUNT(*) > 5;

-- Per-player running spend and purchase sequence, using window functions
-- (keeps every row, unlike GROUP BY which collapses rows).
SELECT
    transaction_id,
    player_id,
    amount,
    transaction_ts,
    ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY transaction_ts) AS txn_seq,
    SUM(amount) OVER (PARTITION BY player_id)                          AS player_total_spent
FROM fact_transaction;

-- Deduplication pattern used in the Silver layer: keep only the latest row
-- per transaction_id.
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY transaction_ts DESC) AS rn
    FROM fact_transaction
)
SELECT * FROM ranked WHERE rn = 1;
