import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    label: str
    amount: float


def parse_fortuneo(path: Path) -> list[Transaction]:
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    transactions = []
    for i in range(0, len(lines) - 1, 3):
        label = lines[i]
        amount = abs(float(lines[i + 1].replace(",", ".")))
        transactions.append(Transaction(label=label, amount=amount))
    return transactions


def parse_ynab(path: Path) -> list[Transaction]:
    transactions = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            amount = float(row["Outflow"].lstrip("€"))
            if amount == 0:
                continue
            label = f"{row['Account']}_{row['Date']}_{row['Payee']}_{row['Category Group/Category']}"
            transactions.append(Transaction(label=label, amount=amount))
    return transactions


def reconcile(
    fortuneo: list[Transaction], ynab: list[Transaction]
) -> tuple[list[Transaction], list[Transaction]]:
    ynab_counts = Counter(t.amount for t in ynab)
    missing = []
    for t in fortuneo:
        if ynab_counts[t.amount] > 0:
            ynab_counts[t.amount] -= 1
        else:
            missing.append(t)
    remaining = Counter(ynab_counts)
    ynab_orphans = []
    for t in ynab:
        if remaining[t.amount] > 0:
            remaining[t.amount] -= 1
            ynab_orphans.append(t)
    return missing, ynab_orphans


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=Path, default=Path("config.json"))
    parser.add_argument("-f", "--fortuneo", type=Path)
    parser.add_argument("-y", "--ynab", type=Path)
    args = parser.parse_args()

    config: dict = {}
    if args.config.exists():
        config = json.loads(args.config.read_text())

    fortuneo_path: Path | None = args.fortuneo or (Path(config["fortuneo"]) if "fortuneo" in config else None)
    ynab_path: Path | None = args.ynab or (Path(config["ynab"]) if "ynab" in config else None)

    if not fortuneo_path:
        parser.error("--fortuneo is required (or set 'fortuneo' in config)")
    if not ynab_path:
        parser.error("--ynab is required (or set 'ynab' in config)")

    fortuneo = parse_fortuneo(fortuneo_path)
    ynab = parse_ynab(ynab_path)
    missing, ynab_orphans = reconcile(fortuneo, ynab)

    if not missing and not ynab_orphans:
        print("All transactions matched.")
    for t in missing:
        print(f"MISSING: {t.label} — €{t.amount:.2f}")
    for t in ynab_orphans:
        print(f"YNAB ORPHAN: {t.label} — €{t.amount:.2f}")


if __name__ == "__main__":
    main()
