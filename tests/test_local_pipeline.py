"""End-to-end checks for the generator and the local DuckDB medallion pipeline."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "local"))
import pipeline  # noqa: E402


def generate(out: Path, dirty_rate: float = 0.0, seed: int = 7) -> Path:
    subprocess.run(
        [sys.executable, str(ROOT / "data-generator/generate_data.py"), "--players", "300", "--games", "8",
         "--locations", "20", "--transactions", "5000", "--seed", str(seed),
         "--dirty-rate", str(dirty_rate), "--output-dir", str(out)],
        check=True, capture_output=True,
    )
    return out


@pytest.fixture(scope="module")
def dirty(tmp_path_factory):
    return pipeline.run(generate(tmp_path_factory.mktemp("dirty"), dirty_rate=0.05))


def test_every_bronze_row_is_either_in_silver_or_rejected(dirty):
    _, s = dirty
    assert s["layers"]["bronze_transactions"] == s["layers"]["silver_transactions"] + s["layers"]["rejected"]
    assert s["layers"]["gold_fact_rows"] == s["layers"]["silver_transactions"]


def test_each_injected_fault_type_is_caught(dirty):
    _, s = dirty
    reasons = {r["reason"] for r in s["rejects_by_reason"]}
    assert reasons == {"duplicate_delivery", "non_positive_or_missing_amount", "unknown_player",
                       "unknown_game", "missing_or_bad_timestamp"}


def test_silver_has_unique_transactions_and_gold_has_no_orphans(dirty):
    con, s = dirty
    assert con.execute("SELECT COUNT(*) - COUNT(DISTINCT transaction_id) FROM silver.transactions").fetchone()[0] == 0
    assert s["orphan_fact_keys"] == 0


def test_non_retail_rows_have_no_location(dirty):
    con, _ = dirty
    assert con.execute("SELECT COUNT(*) FROM gold.fact_transaction WHERE channel <> 'retail' AND location_id IS NOT NULL").fetchone()[0] == 0


def test_generated_purchases_never_precede_signup(dirty):
    _, s = dirty
    assert s["warnings"]["purchase_before_signup"] == 0


def test_clean_data_produces_no_rejects(tmp_path):
    _, s = pipeline.run(generate(tmp_path))
    assert s["layers"]["rejected"] == 0


def test_generator_is_reproducible_with_a_seed(tmp_path):
    a = generate(tmp_path / "a", dirty_rate=0.02)
    b = generate(tmp_path / "b", dirty_rate=0.02)
    for name in ("players.csv", "games.csv", "retail_locations.csv", "transactions.csv"):
        assert (a / name).read_bytes() == (b / name).read_bytes(), name
