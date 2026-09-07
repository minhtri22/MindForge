"""
OIR-PPV v0.13.11 replay runner scaffold.

Loads frozen seed registry and executes baseline/treatment comparison.
"""

import json
from pathlib import Path


SEED_FILE = Path("../seeds/v0.13.11_seed_registry.json")


def load_seeds():
    with open(SEED_FILE, encoding="utf-8") as f:
        return json.load(f)


def main():
    seeds = load_seeds()
    print("Frozen replay cases:")
    for name, config in seeds.items():
        print(name, config["seed"])


if __name__ == "__main__":
    main()
