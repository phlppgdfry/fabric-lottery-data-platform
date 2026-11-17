"""
Generates synthetic lottery-style data for the Fabric Lottery Data Platform:
players, games, retail locations, and transactions.

Usage:
    python generate_data.py --players 5000 --transactions 100000
"""

import argparse
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"

CHANNELS = ["online", "retail", "mobile_app"]
GAME_TYPES = ["scratch_card", "draw_game", "instant_win"]


def generate_games(n=20):
    games = []
    for i in range(1, n + 1):
        games.append(
            {
                "game_id": i,
                "game_name": f"Game {i}",
                "game_type": random.choice(GAME_TYPES),
                "ticket_price": round(random.choice([1, 2, 5, 10, 20]), 2),
                "active": random.choice([True, True, True, False]),
            }
        )
    return games


def generate_retail_locations(n=200):
    locations = []
    for i in range(1, n + 1):
        locations.append(
            {
                "location_id": i,
                "location_name": f"Retailer {i}",
                "city": random.choice(
                    ["Brussels", "Antwerp", "Ghent", "Liege", "Bruges", "Namur"]
                ),
            }
        )
    return locations


def generate_players(n=5000):
    players = []
    start = datetime(2015, 1, 1)
    for i in range(1, n + 1):
        signup_date = start + timedelta(days=random.randint(0, 4000))
        players.append(
            {
                "player_id": i,
                "signup_date": signup_date.date().isoformat(),
                "birth_year": random.randint(1955, 2005),
                "preferred_channel": random.choice(CHANNELS),
            }
        )
    return players


def generate_transactions(n, players, games, locations):
    transactions = []
    start = datetime(2023, 1, 1)
    end = start + timedelta(days=600)
    # A player can only buy after signing up, so only players who signed up before the
    # end of the sales window are eligible, and each purchase falls after their signup.
    eligible = [p for p in players if datetime.fromisoformat(p["signup_date"]) < end]
    for _ in range(n):
        player = random.choice(eligible)
        game = random.choice(games)
        channel = random.choices(
            CHANNELS, weights=[0.4, 0.4, 0.2]
        )[0]
        location = random.choice(locations) if channel == "retail" else None
        first = max(start, datetime.fromisoformat(player["signup_date"]))
        ts = first + timedelta(
            seconds=random.randint(0, int((end - first).total_seconds()))
        )
        transactions.append(
            {
                # Seeded, so --seed reproduces the same IDs (uuid.uuid4() would not).
                "transaction_id": str(uuid.UUID(int=random.getrandbits(128), version=4)),
                "player_id": player["player_id"],
                "game_id": game["game_id"],
                "location_id": location["location_id"] if location else "",
                "channel": channel,
                "amount": game["ticket_price"],
                "transaction_ts": ts.isoformat(),
            }
        )
    return transactions


def inject_faults(transactions, rate, players, games):
    """Opt-in realistic source faults so the Silver layer has something to catch.

    Per selected row one fault: an exact duplicate (re-delivery), a non-positive or
    missing amount, an unknown player or game key, or an unparseable timestamp.
    Uses its own random stream so the clean rows stay identical to a run without faults.
    """
    rng = random.Random(f"faults-{len(transactions)}-{rate}")
    max_player = max(p["player_id"] for p in players)
    max_game = max(g["game_id"] for g in games)
    out = []
    for row in transactions:
        out.append(row)
        if rng.random() >= rate:
            continue
        fault = rng.choice(["duplicate", "amount", "player", "game", "timestamp"])
        if fault == "duplicate":
            out.append(dict(row))
        elif fault == "amount":
            row["amount"] = rng.choice(["", "0", "-5"])
        elif fault == "player":
            row["player_id"] = max_player + rng.randint(1, 1000)
        elif fault == "game":
            row["game_id"] = max_game + rng.randint(1, 50)
        else:
            row["transaction_ts"] = rng.choice(["", "2023-13-45T25:00:00", "yesterday"])
    return out


def write_csv(rows, filename, output_dir=None):
    output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows):,} rows -> {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--players", type=int, default=5000)
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--locations", type=int, default=200)
    parser.add_argument("--transactions", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dirty-rate",
        type=float,
        default=0.0,
        help="share of transactions that get one injected source fault (default 0)",
    )
    parser.add_argument("--output-dir", default=None, help="default: data-generator/output")
    args = parser.parse_args()

    random.seed(args.seed)

    players = generate_players(args.players)
    games = generate_games(args.games)
    locations = generate_retail_locations(args.locations)
    transactions = generate_transactions(args.transactions, players, games, locations)
    if args.dirty_rate > 0:
        transactions = inject_faults(transactions, args.dirty_rate, players, games)

    write_csv(players, "players.csv", args.output_dir)
    write_csv(games, "games.csv", args.output_dir)
    write_csv(locations, "retail_locations.csv", args.output_dir)
    write_csv(transactions, "transactions.csv", args.output_dir)


if __name__ == "__main__":
    main()
