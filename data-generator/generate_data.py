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
    for _ in range(n):
        player = random.choice(players)
        game = random.choice(games)
        channel = random.choices(
            CHANNELS, weights=[0.4, 0.4, 0.2]
        )[0]
        location = random.choice(locations) if channel == "retail" else None
        ts = start + timedelta(
            seconds=random.randint(0, int(timedelta(days=600).total_seconds()))
        )
        transactions.append(
            {
                "transaction_id": str(uuid.uuid4()),
                "player_id": player["player_id"],
                "game_id": game["game_id"],
                "location_id": location["location_id"] if location else "",
                "channel": channel,
                "amount": game["ticket_price"],
                "transaction_ts": ts.isoformat(),
            }
        )
    return transactions


def write_csv(rows, filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
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
    args = parser.parse_args()

    random.seed(args.seed)

    players = generate_players(args.players)
    games = generate_games(args.games)
    locations = generate_retail_locations(args.locations)
    transactions = generate_transactions(args.transactions, players, games, locations)

    write_csv(players, "players.csv")
    write_csv(games, "games.csv")
    write_csv(locations, "retail_locations.csv")
    write_csv(transactions, "transactions.csv")


if __name__ == "__main__":
    main()
