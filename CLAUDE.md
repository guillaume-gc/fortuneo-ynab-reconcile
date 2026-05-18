# CLAUDE.md

## Commit convention
Conventional Commits, subject line only, no body.
Examples: `feat: add ynab parser`, `fix: handle empty paste`, `chore: add fixtures`

## Non-obvious implementation details
- Fortuneo transactions come from stdin paste, not a file argument
- Matching is amount-only (not payee) using a Counter multiset to handle duplicate amounts
- Fortuneo amounts use French locale (comma decimal, negative sign): `-200,00`
- YNAB outflow amounts are prefixed with `€` and use period decimal: `€200.00`

## Stack
- Python 3.11+, stdlib only (no third-party dependencies)

## Tooling
Use mise for all commands. Prefer defined tasks (`mise run <task>`); for anything else, use `mise exec -- <cmd>`.
