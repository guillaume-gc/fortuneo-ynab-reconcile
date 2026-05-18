import argparse
import csv
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Transaction:
    label: str
    amount: float


def parse_fortuneo(text: str) -> list[Transaction]:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
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
    ynab_errors = []
    for t in ynab:
        if remaining[t.amount] > 0:
            remaining[t.amount] -= 1
            ynab_errors.append(t)
    return missing, ynab_errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ynab", dest="ynab_csv", type=Path, required=True)
    args = parser.parse_args()

    print("Paste Fortuneo transactions and press Ctrl+D when done:")
    pasted = sys.stdin.read()

    fortuneo = parse_fortuneo(pasted)
    ynab = parse_ynab(args.ynab_csv)
    missing, ynab_errors = reconcile(fortuneo, ynab)

    if not missing and not ynab_errors:
        print("All transactions matched.")
    for t in missing:
        print(f"MISSING: {t.label} — €{t.amount:.2f}")
    for t in ynab_errors:
        print(f"YNAB ERROR: {t.label} — €{t.amount:.2f}")


if __name__ == "__main__":
    main()
