# Query versioning

One file per query, named `<phase>_<name>_v<N>.txt`. A file is never edited once it has
been run: a change creates `v<N+1>`. Each file carries its source, the OpenAlex filter
field, the run date and the record count returned, because a count means nothing without
the exact string that produced it.

Precision notes on acronyms are recorded in `docs/01_bibliometric_mapping.md`, measured on
OpenAlex on 2026-09-22:

| Acronym | Bare | Bound to expanded form | Decision |
|---|---|---|---|
| PHA | 56,015 | 8,422 | Bare form rejected |
| DFT | 471 (within core) | 295 (within core) | Bare form rejected |

Bare acronyms are not used in any frozen query.
