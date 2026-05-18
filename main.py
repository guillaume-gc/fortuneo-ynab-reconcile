import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


def parse_fortuneo(text: str) -> list[tuple[str, float]]:
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    transactions = []
    for i in range(0, len(lines) - 1, 3):
        label = lines[i]
        amount = abs(float(lines[i + 1].replace(",", ".")))
        transactions.append((label, amount))
    return transactions


def parse_ynab(path: Path) -> list[float]:
    amounts = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            outflow = row["Outflow"].lstrip("€")
            amount = float(outflow)
            if amount > 0:
                amounts.append(amount)
    return amounts


def reconcile(
    fortuneo: list[tuple[str, float]], ynab: list[float]
) -> tuple[list[tuple[str, float]], list[float]]:
    ynab_counts = Counter(ynab)
    missing = []
    for label, amount in fortuneo:
        if ynab_counts[amount] > 0:
            ynab_counts[amount] -= 1
        else:
            missing.append((label, amount))
    ynab_errors = [amount for amount, count in ynab_counts.items() for _ in range(count)]
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
    for label, amount in missing:
        print(f"MISSING: {label} — €{amount:.2f}")
    for amount in ynab_errors:
        print(f"YNAB ERROR: €{amount:.2f} has no matching Fortuneo transaction")


if __name__ == "__main__":
    main()
