# fortuneo-ynab-reconcile

Compare Fortuneo credit card transactions against a YNAB export to find missing entries.

## Usage

```bash
python main.py <ynab_csv>
```

Paste your Fortuneo credit card transactions when prompted, then press Ctrl+D.

## Input formats

**Fortuneo (stdin paste):** copy the transactions from the Fortuneo portal and paste them. Each transaction is three lines: label, amount, currency symbol.

**YNAB CSV:** export your account from YNAB and pass the file path as the argument.

## Output

```
MISSING: CARTE XXXX LABEL — €200.00
```

Prints one line per transaction found in Fortuneo but not in YNAB. Prints `All transactions matched.` if nothing is missing.
