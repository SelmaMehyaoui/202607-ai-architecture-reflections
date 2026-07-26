# Norvale Commerce controlled context

Use only the following fictional experiment data. Do not supplement it with
outside facts.

## Orders

| Order | Date | Category | Quantity | Unit price |
|---|---|---|---:|---:|
| N-101 | 2026-01-03 | amber | 2 | 17.50 |
| N-102 | 2026-01-08 | cobalt | 1 | 120.00 |
| N-103 | 2026-01-12 | amber | 3 | 9.00 |
| N-104 | 2026-02-02 | verdant | 4 | 11.25 |
| N-105 | 2026-02-11 | cobalt | 2 | 35.00 |
| N-106 | 2026-02-18 | verdant | 1 | 80.00 |
| N-107 | 2026-03-04 | amber | 2 | 22.00 |
| N-108 | 2026-03-09 | cobalt | 3 | 16.00 |
| N-109 | 2026-03-15 | verdant | 2 | 14.50 |

## Return policies

| Category | Window | Restocking fee | Required condition |
|---|---:|---:|---|
| amber | 21 days | 0% | Unused items in original packaging |
| cobalt | 14 days | 10% | Unopened items with the numbered seal intact |
| verdant | 30 days | 0% | Unused items with the fictional Norvale tag attached |

Revenue is `quantity × unit price`. Dates use ISO 8601 and date filters are
inclusive.
