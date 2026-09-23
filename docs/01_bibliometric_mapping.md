# 01 — Phase 1: Spatiotemporal mapping of the biopolymers field

*Started 2026-09-23. Phase 1 of `00_plan.md`.*

**Objective.** Position the biopolymers field in time and space before any judgement is
made about it, and measure how much of that field uses computational, chemoinformatic or
AI methods.

**Status.** in progress — 2026-09-23. Keyword-based pass complete on OpenAlex aggregates.
The record-level work that was blocked here is done in `02_networks_and_screening.md`, and
**section 4 of this document is superseded by section 3.3 there**: reading the abstracts
shows the keyword counts both overstate the world share and understate the regional one.
Web of Science, Scopus and Lens still not added.

---

## 1. What was counted

The corpus is the field that **identifies itself** as biopolymers: works whose title or
abstract carries a biopolymer framing term. Frozen as
`queries/p1_core_biopolymer_field_v1.txt`, run on OpenAlex 2026-09-23.

This definition was reached empirically, not assumed. Family blocks were probed first, and
each one intersected with a biopolymer framing turned out to be a subset of the generic
string, so the generic string is the union rather than a narrowing. Works on cellulose or
collagen that never frame the material as a polymer sit outside the corpus by design.

Two acronym tests decided the wording of every query:

| Acronym | Bare | Bound to expanded form | Decision |
|---|---|---|---|
| PHA | 56,015 | 8,422 | bare form rejected |
| DFT (within core) | 471 | 295 | bare form rejected |

The methods layer is the same corpus intersected with
`queries/p2_computational_ai_v1.txt`, covering molecular dynamics, quantum chemistry,
chemoinformatics and QSAR/QSPR, machine learning, generative models, and solubility
modelling.

## 2. Size and growth

| Context | Works, all years | 2015–2025 | Share of world | CAGR 2015–2025 | Open access | Articles |
|---|---|---|---|---|---|---|
| World | 145,743 | 90,931 | 100% | 11.4% | 43.2% | 72.3% |
| Ibero-America | 13,095 | 9,445 | 10.4% | 13.7% | 58.5% | 82.0% |
| Latin America | 8,162 | 6,035 | 6.6% | 14.7% | 55.5% | 82.2% |
| Colombia | 598 | 465 | 0.51% | 27.0% | 66.7% | 78.9% |

Source: `outputs/tables/T3_context_comparison.csv`. Figure
`outputs/figures/F1_annual_production.png`.

Three things follow. The field is growing fast everywhere, and the regional contexts are
growing **faster than the world**, so the region is closing the relative gap rather than
falling behind. Colombia grows fastest of all, at 27% a year, but from a base so small that
the rate says more about the base than about the capacity. And regional output is markedly
more open: two thirds of Colombian work is open access against 43% worldwide.

## 3. Where the work is done

The top three countries hold 50,777 works, just over a third of the whole field. Only one
Latin American country reaches the top twenty.

| Rank | Country | Works | Computational or AI share |
|---|---|---|---|
| 1 | United States | 19,356 | 4.33% |
| 2 | China | 16,487 | 3.73% |
| 3 | India | 14,934 | 2.95% |
| 9 | Brazil | 4,450 | 1.96% |

Full ranking in `outputs/tables/T4_country_ranking.csv`, regional ranking in
`T5_latam_country_ranking.csv`, figure `F3_country_ranking.png`.

Inside Latin America the order is Brazil, Mexico, Argentina, Colombia, Chile. Colombia is
fourth by volume, which is a stronger position than its 0.51% world share suggests.

## 4. The computational and AI layer

This is the central result of Phase 1.

| Context | Works using computational or AI methods, 2015–2025 | Share of the field |
|---|---|---|
| World | 2,390 | 2.63% |
| Ibero-America | 205 | 2.17% |
| Latin America | 133 | 2.20% |
| Colombia | 9 | 1.94% |

Two findings, and the second is the one worth defending.

**The layer is thin.** Under three percent of the biopolymers field uses any computational,
chemoinformatic or AI method at all. It is, however, growing: on three-year rolling sums the
world share moved from 1.55% in 2013 to 1.86% in 2019 and 3.56% in 2025, so it has roughly
doubled in a decade after a decline through the 2000s. Figure `F2_methods_share.png`.

**The region is not behind in method uptake.** Latin America sits at 2.20% against a world
2.63%, and Colombia at 1.94%. The regional deficit is one of **volume**, not of methodological
modernity. *(Superseded: `02_networks_and_screening.md` section 3.3 shows these keyword
counts understate the region. On screened abstracts Latin America reaches 3.68% and
Colombia 5.09%, so Colombia is above the regional average rather than below it. The
conclusion holds and strengthens; the ordering and the numbers here should not be quoted.)* This cuts against the expectation that the gap would be technological, and it
changes what the thesis can recommend: the constraint to argue about is scale and
continuity of output, not access to computational practice.

Generative methods are effectively absent. A probe of generative models, large language
models, graph neural networks and inverse design inside the core returned **43 works
worldwide**. That is the emptiest part of the map.

## 5. The three anchored lines

| Anchor | World | Latin America | Colombia | Computational share, world | Computational share, region |
|---|---|---|---|---|---|
| Cellulose and nanocellulose | 378,840 | 14,683 | 902 | 1.64% | 1.69% |
| PHA / PHB | 22,378 | 1,444 | 88 | 1.30% | 1.52% |
| Lignin | 181,260 | 11,534 | 811 | 2.08% | 1.86% |

Source `outputs/tables/T6_anchor_lines.csv`, figure `F4_anchor_lines.png`. These counts do
not require a biopolymer framing, so they are larger than the corresponding slices of the
core corpus.

Lignin is the most computationally studied of the three and PHA the least, at 1.30%. Latin
America holds a larger share of world output in PHA (6.45%) and lignin (6.36%) than in
cellulose (3.88%), which fits a region working from agro-industrial residues.

## 6. What the field is about

The largest topics of the core corpus are biodegradable polymer synthesis, nanocomposite
films for food packaging, electrospun nanofibers, cellulose, and bone tissue engineering
(`T9_core_top_topics.csv`).

The methods layer looks different, and the difference is a warning. Its largest topic is
**protein structure and dynamics** (201 works), ahead of biodegradable polymer synthesis
(189). The framing terms *biomacromolecule* and *natural polymer* pull structural biology
and nucleic-acid chemistry into the corpus, where molecular dynamics has been routine for
thirty years. Part of the measured 2.63% is therefore biophysics rather than biopolymer
materials science, which means the materials-side figure is **lower** than 2.63%, not
higher. Quantifying that contamination needs record-level screening of abstracts, which is
the blocked work described below.

## 7. Limitations of this pass

- **One source.** OpenAlex only. Scopus, Web of Science and Lens have not been added, so
  nothing here is triangulated yet and the counts carry OpenAlex's known inclusiveness.
- **Title and abstract only.** No full-text search, which suppresses works that name the
  method only in the methods section.
- **English bias.** The queries are English. Regional output published in Spanish and
  Portuguese is undercounted, which matters most for the Colombian slice.
- **Corpus contamination.** Quantified in section 6, not yet corrected.
- **No record-level analysis.** No co-authorship networks, no Lotka or Bradford, no keyword
  co-occurrence maps, no author or institution disambiguation. All of it needs the full
  records.
- **Country attribution** is by institution country, so a work counts once for each country
  present. Country columns therefore sum to more than the corpus total.

## Decisions

- The core corpus is defined by self-identification as biopolymers, after probing showed
  family-plus-framing blocks to be subsets of it (2026-09-23).
- Bare acronyms are excluded from every query, on measured precision (2026-09-23).
- 2026 is excluded from every curve as incomplete; long curves run 1990–2025 and
  comparative indicators 2015–2025 (2026-09-23).
- Ibero-America is reported as a context distinct from Latin America (2026-09-23).
- Ratios on small denominators are computed on three-year rolling sums and suppressed below
  50 works in the window. Colombia publishes 0–3 method papers a year, and a raw annual
  percentage there swung between 0 and 9 percent on sampling noise alone (2026-09-23).

## Open questions

- **An OpenAlex API key is needed.** The free daily budget is shared across everyone on the
  same IP and was exhausted by the aggregate harvest, so full-record downloads fail with
  HTTP 429. Keys are free at https://help.openalex.org/api/authentication/. Until one
  exists, everything in section 7 that needs records stays blocked. — AC.
- Scopus and Web of Science access at UNISUCRE, and Camila's credentials. — AC.
- Whether to add Spanish and Portuguese query variants for the regional slices. — AC.
- GIFTEX, UNF and Wilson Castro: names and lines, needed to place them on the map. — AC.

## References

To be collected in `refs/references.bib`.
