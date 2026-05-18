# fortuneo-ynab-reconcile

Compare Fortuneo credit card transactions against a YNAB export to find missing entries.

## Usage

```bash
python main.py -f <fortuneo_txt> -y <ynab_csv>
```

## Input formats

**Fortuneo (`-f`):** a text file with transactions copied from the Fortuneo portal. Each transaction is three lines: label, amount, currency symbol.

```
CARTE XXXX LABEL
-200,00
€
CARTE XXXX LABEL
-20,00
€
```

**YNAB (`-y`):** a CSV exported from YNAB.

## Output

```
MISSING: CARTE XXXX LABEL — €200.00
YNAB ORPHAN: XXX_31.05.2026_XXXX_XXX — €20.00
```

Prints `All transactions matched.` if nothing is missing.
