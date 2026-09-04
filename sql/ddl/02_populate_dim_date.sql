-- Generates one row per day for a fixed date range.
-- amount/ticket_price stay in fact/dim_game; this table is purely calendar context.

INSERT INTO dim_date (date_id, full_date, year, quarter, month, day_of_week, is_weekend)
SELECT
    CAST(TO_CHAR(d, 'YYYYMMDD') AS INT)             AS date_id,
    d                                                 AS full_date,
    EXTRACT(YEAR FROM d)::INT                          AS year,
    EXTRACT(QUARTER FROM d)::INT                       AS quarter,
    EXTRACT(MONTH FROM d)::INT                         AS month,
    EXTRACT(ISODOW FROM d)::INT                        AS day_of_week,
    EXTRACT(ISODOW FROM d) IN (6, 7)                   AS is_weekend
FROM GENERATE_SERIES(DATE '2023-01-01', DATE '2025-12-31', INTERVAL '1 day') AS d;
