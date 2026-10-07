# 07 — Full record: motivation, methodology, search equations, raw numbers, conclusions, references

*Compiled 2026-10-07 as a single reference file. Everything here already exists split across
`docs/00_plan.md`, `report/informe_bibliometrico.tex`, `queries/*.txt`, `outputs/tables/*.csv`
and `refs/references.bib`; this document assembles it in one place on request. The source
files remain authoritative — if this file and one of them disagree, the source file is right
and this one is stale.*

---

## 1. Motivation

Global plastic production and its environmental footprint are driving interest in
biopolymers (polysaccharides, microbial polyesters, structural proteins, lignins) as
substitutes. At the same time, computational chemistry, chemoinformatics and artificial
intelligence are reshaping materials discovery broadly. This project asks how far that
computational wave has actually reached biopolymer research — worldwide, and specifically in
Latin America and Colombia, where this group (Grupo IN SILICO, Universidad de Sucre) works on
cellulose/nanocellulose, polyhydroxyalkanoates (PHA/PHB) and lignin.

The Latin American and Colombian narrowing is what makes the thesis publishable rather than a
course exercise: that slice is thin in the existing bibliometric literature, and this group's
own joint lines (with GIFTEX–UIS and Universidad Nacional de Frontera, Perú) sit exactly on
the intersection being measured.

## 2. Introduction — what this report answers

Three questions, in the order the work addressed them:

1. Where and when is research on biopolymers being done, and by whom?
2. How much of that research uses computational chemistry, chemoinformatics or artificial
   intelligence, and which methods on which polymers?
3. What does the Latin American and Colombian position look like inside that map?

Thematic scope is deliberately **broad**: every biopolymer recognised as a subject of
scientific study, with explicit anchoring on the three lines this group works in jointly —
cellulose/nanocellulose, PHA/PHB, and lignin. Biomedical applications are kept in, not
excluded, so the map is the whole field and the narrowing happens later, by intention.

Two results shape everything that follows: keyword bibliometrics **overstates** the
computational share of the field worldwide (the vocabulary of biopolymers overlaps that of
structural biology), and it **understates** the share in Latin America (regional work is
invisible to affiliation matching, and partly to English-only vocabulary). Reading abstracts
instead of matching keywords reverses the ranking of contexts the keyword counts produce.

## 3. Methodology

### 3.1 How the corpus was defined

The core corpus is the field that *identifies itself* as biopolymers: works whose title or
abstract carries a biopolymer-framing term. This was reached empirically — blocks for each
polymer family were probed first, and every family block intersected with a biopolymer
framing turned out to be a subset of the generic string, so the generic string is the union,
not a narrowing.

Two acronym tests decided the wording of every query: bare `PHA` returns 56,015 records
against 8,422 bound to its expanded form; bare `DFT` returns 471 against 295 inside the core
corpus. **Bare acronyms are used nowhere.**

Every search string is a versioned file (`queries/*.txt`) that is never edited once run, so a
count can always be traced to the exact text that produced it.

### 3.2 Sources

Scopus and Web of Science are **not used**: no institutional subscription at UNISUCRE
(confirmed 2026-09-23). Triangulation runs on OpenAlex (base corpus) and Lens (independent
index), with Semantic Scholar and Europe PMC recovering abstracts OpenAlex lacks.

| Block | Region | OpenAlex | Lens | Lens as % of OpenAlex |
|---|---|---:|---:|---:|
| Core field | World | 142,254 | 129,729 | 91.2 |
| Core field | Latin America | 8,147 | 5,412 | 66.4 |
| Core field | Colombia | 598 | 342 | 57.2 |
| Method layer | World | 3,912 | 3,323 | 84.9 |
| Method layer | Latin America | 211 | 104 | 49.3 |
| Method layer | Colombia | 17 | 4 | 23.5 |
| Cellulose | Latin America | 14,222 | 9,813 | 69.0 |
| Cellulose | Colombia | 897 | 558 | 62.2 |
| PHA/PHB | World | 22,225 | 20,241 | 91.1 |
| PHA/PHB | Latin America | 1,444 | 1,037 | 71.8 |
| PHA/PHB | Colombia | 88 | 64 | 72.7 |
| Lignin | Latin America | 11,464 | 8,598 | 75.0 |
| Lignin | Colombia | 810 | 635 | 78.4 |

Across matched corpora, 76–100% of Lens records are also in OpenAlex, but only 24–75% of
OpenAlex records are in Lens. Lens still contributes works OpenAlex lacks, so the union of
the two is larger than either; a single-source regional count is a **lower bound**, reported
as a result, not hidden as a caveat.

### 3.3 Reading the abstracts (method-layer screening)

A keyword query cannot tell a molecular-dynamics study of a cellulose nanocrystal composite
from a molecular-dynamics study of haemoglobin allostery — only the first is biopolymer
materials science. Every abstract in the method layer was classified by a language model
(DeepSeek, bulk, schema-constrained, cached on a hash of the prompt so the classification is
reproducible and free to re-run): materials research vs. biological-function research, which
polymer family, which computational method, whether experiments are reported.

**Correction applied after inspecting output, not trusting it:** the first pass had a
catch-all "computational" category that absorbed factorial designs, response-surface
methodology and curve-fitting to the authors' own measurements, inflating the Colombian
computational share to 12.5% against a defensible 3%. The ambiguous bucket was re-asked with
a question naming the distinction; statistical design of experiments is now excluded from
every computational count. First-pass classifications are kept on disk so the correction is
auditable.

### 3.4 Validating the screening

125 abstracts were double-coded by a second, independent reader on a **different model**
(Claude), blind to the first coder's (DeepSeek's) labels — asking a model to check its own
work would just have it repeat its own mistakes and report high agreement with itself.
Agreement reported as Cohen's κ, not percent agreement, because percent agreement flatters a
dominant class.

| Dimension | Agreement | Cohen's κ |
|---|---:|---:|
| materials vs biological | 94.0% | 0.878 |
| computational at all | 92.0% | 0.782 |
| method family | 88.0% | 0.816 |
| polymer family | 80.0% | 0.767 |

The distinction the whole correction depends on — materials research vs. biological function
— reaches the highest agreement of the four (0.878, "almost perfect" on the conventional
0.61–0.80 substantial / >0.80 almost-perfect scale).

**Directional bias, measured and quantified:** on the random sample of 100, the first coder
(DeepSeek) called 79 works computational against the second coder's (Claude's) 73 — a
relative over-detection of **+8.2%**. Five of the seven disputed works were labelled machine
learning merely for mentioning AI as a closing outlook in reviews or purely experimental
papers. **Every screened share in this report is therefore an upper bound**; the strict world
figure of 1.28% is closer to 1.18% once the bias is applied.

### 3.5 Rebuilding the corpus in three languages

The English-only queries miss Spanish- and Portuguese-language literature. A combined
EN+ES+PT vocabulary was frozen (`*_combined_v1.txt`) and run as a **set difference** against
the English corpus (what the English string misses), never merged silently. Result, and the
inversion of the original expectation: the added literature is almost entirely
non-computational, so completing the corpus **lowers** regional computational shares rather
than raising them (Colombia 4.48% → 3.84% screened; Latin America 3.43% → 3.12%). See §6
below for the full numbers.

### 3.6 Tool stack

| Tool | Used for |
|---|---|
| Bibliometrix / biblioshiny (R) | Core metrics, thematic maps, Lotka and Bradford, three-field plots |
| VOSviewer | Publication-quality co-occurrence, co-authorship and co-citation maps |
| Python (pybliometrics, pyalex, NetworkX, pandas) | Retrieval, deduplication, network metrics, screening, report generation |

## 4. Search equations (verbatim)

Every string below is copied unmodified from its versioned file in `queries/`. Source field
for OpenAlex queries is `title_and_abstract.search` unless stated otherwise. Header comments
(run date, raw count, rationale) are preserved.

### 4.1 Core field

**`queries/p1_core_biopolymer_field_v1.txt`** — English only. Run 2026-09-23. **Count: 145,743** (no year filter). Every family block intersected with a biopolymer framing turned out to be a subset of this string, so this is the union, not a narrowing.

```
biopolymer OR biopolymers OR bioplastic OR bioplastics OR "bio-based polymer" OR
"bio-based polymers" OR "biobased polymer" OR "biodegradable polymer" OR
"biodegradable polymers" OR "renewable polymer" OR "natural polymer" OR
"natural polymers" OR biomacromolecule OR biomacromolecules
```

**`queries/p1_core_es_pt_v1.txt`** — Spanish/Portuguese variants. Reported as an addition to the English core, never merged silently.

```
biopolímero OR biopolímeros OR biopolimero OR biopolimeros OR bioplástico OR
bioplásticos OR bioplastico OR bioplasticos OR "polímero biodegradable" OR
"polímeros biodegradables" OR "polímero biodegradável" OR "polímeros biodegradáveis" OR
"polímero natural" OR "polímeros naturales" OR "polímeros naturais" OR
"polímero de origen renovable" OR biomacromolécula OR biomacromoléculas
```

**`queries/p1_core_combined_v1.txt`** — EN+ES+PT union, written out in full so the string that produced any count lives in one file. Run 2026-09-24. **Count: 150,122.**

```
biopolymer OR biopolymers OR bioplastic OR bioplastics OR "bio-based polymer" OR
"bio-based polymers" OR "biobased polymer" OR "biodegradable polymer" OR
"biodegradable polymers" OR "renewable polymer" OR "natural polymer" OR
"natural polymers" OR biomacromolecule OR biomacromolecules OR biopolímero OR
biopolímeros OR biopolimero OR biopolimeros OR bioplástico OR bioplásticos OR
bioplastico OR bioplasticos OR "polímero biodegradable" OR "polímeros biodegradables" OR
"polímero biodegradável" OR "polímeros biodegradáveis" OR "polímero natural" OR
"polímeros naturales" OR "polímeros naturais" OR "polímero de origen renovable" OR
biomacromolécula OR biomacromoléculas
```

### 4.2 Method layer (Phase 2) — `queries/p2_computational_ai_v1.txt`

Run 2026-09-23. **Count: 5,480,382 standalone; 3,947 intersected with the Phase-1 core.**
Used as `<CORE> AND <this string>`. Bare `DFT` excluded (471 vs. 295 bound).

```
"molecular dynamics" OR "density functional theory" OR "ab initio" OR
"quantum chemical" OR QSAR OR QSPR OR "molecular descriptor" OR "molecular descriptors" OR
chemoinformatics OR cheminformatics OR "virtual screening" OR "molecular docking" OR
"machine learning" OR "deep learning" OR "neural network" OR "artificial intelligence" OR
"random forest" OR "gradient boosting" OR "generative model" OR "large language model" OR
"graph neural network" OR "inverse design" OR "Hansen solubility" OR
"solubility parameter" OR COSMO-RS OR "coarse-grained simulation" OR
"molecular simulation" OR "computational screening"
```

### 4.3 Anchor lines (joint group lines)

**Cellulose** — `p1_anchor_cellulose_v1.txt`: 378,840 (EN, run 2026-09-23) / `p1_anchor_cellulose_combined_v1.txt`: 392,424 (combined, run 2026-09-24)

```
cellulose OR nanocellulose OR "cellulose nanocrystal" OR "cellulose nanocrystals" OR
"cellulose nanofiber" OR "cellulose nanofibers" OR "cellulose nanofibril" OR
"bacterial cellulose" OR "microfibrillated cellulose"
[combined adds:] OR celulosa OR celulose OR nanocelulosa OR nanocelulose OR
"celulosa bacteriana" OR "celulose bacteriana" OR "nanocristales de celulosa" OR
"nanocristais de celulose" OR "nanofibras de celulosa" OR "nanofibras de celulose" OR
lignocelulósico OR lignocelulósica OR lignocelulósicos
```

**PHA/PHB** — `p1_anchor_pha_v1.txt`: 22,378 (EN) / `p1_anchor_pha_combined_v1.txt`: 23,213 (combined). Bare `PHA`/`PHB` excluded in every language.

```
polyhydroxyalkanoate OR polyhydroxyalkanoates OR polyhydroxybutyrate OR
"poly(3-hydroxybutyrate)" OR "poly-3-hydroxybutyrate" OR polyhydroxyvalerate OR
"poly(hydroxybutyrate-co-hydroxyvalerate)" OR "polyhydroxyalkanoic acid"
[combined adds:] OR polihidroxialcanoato OR polihidroxialcanoatos OR
poli-hidroxialcanoatos OR polihidroxibutirato OR poli-hidroxibutirato OR
poliidroxialcanoatos OR poliidroxibutirato
```

**Lignin** — `p1_anchor_lignin_v1.txt`: 181,260 (EN) / `p1_anchor_lignin_combined_v1.txt`: 186,341 (combined)

```
lignin OR lignins OR lignosulfonate OR lignosulfonates OR "kraft lignin" OR
"organosolv lignin" OR "lignin nanoparticle" OR lignocellulosic
[combined adds:] OR lignina OR ligninas OR lignosulfonato OR lignosulfonatos OR
"lignina kraft" OR "lignina organosolv"
```

**ES/PT anchor blocks** — `queries/p1_anchors_es_pt_v1.txt` (run date/count left blank in header; used as set-difference test, not merged):

```
## cellulose
celulosa OR celulose OR nanocelulosa OR nanocelulose OR "celulosa bacteriana" OR
"celulose bacteriana" OR "nanocristales de celulosa" OR "nanocristais de celulose" OR
"nanofibras de celulosa" OR "nanofibras de celulose" OR lignocelulósico OR
lignocelulósica OR lignocelulósicos

## pha
polihidroxialcanoato OR polihidroxialcanoatos OR poli-hidroxialcanoatos OR
polihidroxibutirato OR poli-hidroxibutirato OR poliidroxialcanoatos OR poliidroxibutirato

## lignin
lignina OR ligninas OR lignosulfonato OR lignosulfonatos OR "lignina kraft" OR
"lignina organosolv"

## starch and others
almidón OR amido OR "almidón termoplástico" OR "amido termoplástico" OR quitosano OR
quitosana OR quitina OR alginato OR pectina OR "goma xantana"
```

### 4.4 Geography — `queries/p3_latam_countries_v1.txt`

OpenAlex field `institutions.country_code`, ISO-3166-1 alpha-2, seeded from the archived PHA
protocol country list and corrected against OpenAlex codes.

```
LATAM (20) = ar|bo|br|cl|co|cr|cu|do|ec|gt|hn|mx|ni|pa|pe|pr|py|sv|uy|ve
```
Ibero-America = Latin America + Spain (`es`) + Portugal (`pt`). Colombia = `co` alone.

### 4.5 Cross-platform translations (frozen protocol — never executed; no Scopus/WoS access)

**`queries/platform_lens_v1.txt`** (this one *was* run against the Lens API, feeding `data/raw/lens/`):

```
## L1 — CORE
(title:(biopolymer* OR bioplastic* OR "bio-based polymer" OR "biobased polymer" OR
"biodegradable polymer" OR "renewable polymer" OR "natural polymer" OR biomacromolecule*)
OR abstract:(same set))

## L2 — METHODS
(title:("molecular dynamics" OR "density functional theory" OR "ab initio" OR
"quantum chemical" OR QSAR OR QSPR OR "molecular descriptor*" OR chemoinformatic* OR
cheminformatic* OR "virtual screening" OR "molecular docking" OR "machine learning" OR
"deep learning" OR "neural network*" OR "artificial intelligence" OR "random forest" OR
"gradient boosting" OR "generative model*" OR "large language model*" OR
"graph neural network*" OR "inverse design" OR "Hansen solubility" OR
"solubility parameter*" OR "COSMO-RS" OR "coarse-grained simulation" OR
"molecular simulation" OR "computational screening") OR abstract:(same set))

## L3 — method layer = L1 AND L2
## L4 — ANCHOR cellulose/nanocellulose
## L5 — ANCHOR PHA (bare PHA/PHB excluded: 56,015 vs 8,422 bound)
## L6 — ANCHOR lignin
## Geographic filters: author.affiliation.address.country_code:(...)
## Date filter: year_published:[1990 TO 2026] — 2026 kept, flagged partial
```

**`queries/platform_scopus_v1.txt`** (never run — no access):

```
## S1 — CORE
TITLE-ABS-KEY(biopolymer* OR bioplastic* OR "bio-based polymer*" OR "biobased polymer*" OR
"biodegradable polymer*" OR "renewable polymer*" OR "natural polymer*" OR biomacromolecule*)

## S2 — METHODS
TITLE-ABS-KEY("molecular dynamics" OR "density functional theory" OR "ab initio" OR
"quantum chemical" OR QSAR OR QSPR OR "molecular descriptor*" OR chemoinformatic* OR
cheminformatic* OR "virtual screening" OR "molecular docking" OR "machine learning" OR
"deep learning" OR "neural network*" OR "artificial intelligence" OR "random forest" OR
"gradient boosting" OR "generative model*" OR "large language model*" OR
"graph neural network*" OR "inverse design" OR "Hansen solubility" OR
"solubility parameter*" OR "COSMO-RS" OR "coarse-grained simulation" OR
"molecular simulation" OR "computational screening")

## S3 = S1 AND S2
## S4 ANCHOR cellulose, S5 ANCHOR PHA, S6 ANCHOR lignin (same term sets as above, TITLE-ABS-KEY)
## Geographic: AND AFFILCOUNTRY(Argentina OR ... OR Venezuela) / AND AFFILCOUNTRY(Colombia)
## Date/type: AND PUBYEAR > 1989 AND PUBYEAR < 2027 AND (LIMIT-TO(DOCTYPE,"ar") OR "re" OR "cp")
## Comparability warning: TITLE-ABS-KEY also searches author/indexed keywords, broader
## than OpenAlex title+abstract — not directly comparable without a TITLE-ABS(...) re-run.
```

**`queries/platform_wos_v1.txt`** (never run — no access):

```
## W1 — CORE
TS=(biopolymer* OR bioplastic* OR "bio-based polymer*" OR "biobased polymer*" OR
"biodegradable polymer*" OR "renewable polymer*" OR "natural polymer*" OR biomacromolecule*)

## W2 — METHODS
TS=(same term set as S2/L2 above)

## W3 = #1 AND #2 (saved query numbers)
## W4 ANCHOR cellulose, W5 ANCHOR PHA, W6 ANCHOR lignin — TS=(...) same term sets
## Geographic: AND CU=(Argentina OR ... OR Venezuela) / AND CU=(Colombia)
## Date/type: AND PY=(1990-2026) AND DT=(Article OR Review OR "Proceedings Paper")
## Comparability warning: TS= is broader than OpenAlex and Scopus (adds KeyWords Plus) —
## re-run as (TI=(...) OR AB=(...)) for a like-for-like comparison.
```

## 5. Raw numbers

### 5.1 Field size, growth, geography (English-only; `T3_context_comparison.csv`)

| Context | Total, all years | 2015–2025 | Share of world | CAGR | Methods 2015–2025 | Method share (keyword) | Open access | Article share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| World | 145,743 | 90,931 | 100.0% | 11.37% | 2,390 | 2.63% | 43.2% | 72.3% |
| Ibero-America | 13,095 | 9,445 | 10.39% | 13.65% | 205 | 2.17% | 58.5% | 82.0% |
| Latin America | 8,162 | 6,035 | 6.64% | 14.70% | 133 | 2.20% | 55.5% | 82.2% |
| Colombia | 598 | 465 | 0.51% | 26.98% | 9 | 1.94% | 66.7% | 78.9% |

### 5.2 Same, combined EN+ES+PT corpus (`T34_combined_context_comparison.csv`)

| Context | Total, all years | 2015–2025 core | Share of world | CAGR | Methods 2015–2025 | Method share | Open access | Core 2026 YTD | Methods 2026 YTD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| World | 150,122 | 93,825 | 100.0% | 11.11% | 2,394 | 2.55% | 43.9% | 11,908 | 726 |
| Ibero-America | 14,411 | 10,394 | 11.08% | 12.30% | 208 | 2.00% | 61.3% | 1,150 | 67 |
| Latin America | 9,416 | 6,944 | 7.40% | 12.45% | 136 | 1.96% | 60.0% | 814 | 44 |
| Colombia | 755 | 566 | 0.60% | 18.94% | 9 | 1.59% | 72.7% | 77 | 7 |

### 5.3 Country ranking, top (`T35_combined_country_ranking.csv`)

| Country | Core count | Methods count | Method share |
|---|---:|---:|---:|
| United States | 19,395 | 838 | 4.32% |
| China | 16,491 | 617 | 3.74% |
| India | 14,936 | 440 | 2.95% |
| Germany | 6,388 | 232 | 3.63% |
| United Kingdom | 5,458 | 139 | 2.55% |
| Brazil | 5,130 | 89 | 1.73% |
| Saudi Arabia | 2,184 | 102 | 4.67% |
| Mexico | 1,756 | 59 | 3.36% |
| Argentina | 833 | 11 | 1.32% |

(Full 39-country table in `outputs/tables/T35_combined_country_ranking.csv`.)

### 5.4 Screening by context, abstract-read (English-only; `T21_screening_by_context.csv`)

| Context | Screened | With abstract | Abstract coverage | Materials % of classified | Materials works | Coupled to experiments |
|---|---:|---:|---:|---:|---:|---:|
| World | 3,951 | 3,153 | 79.8% | 56.6% | 1,784 | 54.7% |
| Ibero-America | 327 | 267 | 81.7% | 55.8% | 149 | 50.3% |
| Latin America | 211 | 160 | 75.8% | 61.9% | 99 | 48.5% |
| Colombia | 17 | 12 | 70.6% | 75.0% | 9 | 33.3% |

### 5.5 Screening, combined corpus, before/after (`T36_screened_combined.csv`)

| Corpus | EN computational % | Combined computational % | Added screened | Added materials | Added computational |
|---|---:|---:|---:|---:|---:|
| Method layer, world | 86.38% | 86.52% | 12 | 19 | 19 |
| Method layer, Ibero-America | 87.92% | 88.0% | 3 | 1 | 1 |
| Method layer, Latin America | 85.86% | 86.0% | 4 | 1 | 1 |
| Method layer, Colombia | 88.89% | 88.89% | 0 | 0 | 0 |
| Whole field, Colombia | **4.48%** | **3.84%** | 157 | 127 | 2 |
| Whole field, Latin America | **3.43%** | **3.12%** | 1,254 | 1,114 | 17 |

### 5.6 What Spanish/Portuguese adds, by block (`T30_language_variants.csv`)

| Block | Geography | English | ES/PT | Overlap | Added by ES/PT | Added as % of English |
|---|---|---:|---:|---:|---:|---:|
| Core | Latin America | 8,159 | 1,364 | 112 | 1,252 | 15.35% |
| Core | Colombia | 598 | 183 | 26 | 157 | 26.25% |
| Cellulose | Latin America | 14,669 | 4,218 | 266 | 3,952 | 26.94% |
| Cellulose | Colombia | 902 | 303 | 22 | 281 | 31.15% |
| PHA | Latin America | 1,444 | 221 | 22 | 199 | 13.78% |
| PHA | Colombia | 88 | 36 | 6 | 30 | 34.09% |
| Lignin | Latin America | 11,527 | 1,815 | 129 | 1,686 | 14.63% |
| Lignin | Colombia | 811 | 158 | 13 | 145 | 17.88% |

Full table set (36 CSVs: annual production, methods share by year, Lotka/Bradford summaries,
co-authorship centrality, polymer×method mix, source counts and overlap, affiliation misses,
generative works, etc.) is in `outputs/tables/`.

## 6. Conclusions — what the map shows

1. **The computational layer is thin and it is accelerating.** Around one work in eighty in
   the biopolymers field uses a genuine computational method on a material. That share
   roughly doubled over a decade and 2026 is running ahead of 2025 in every context measured.
2. **The regional deficit is mostly volume, and the language correction sharpened rather than
   excused the rest.** On English-only counts Latin America matched the world on method
   uptake. Rebuilding the corpus in three languages recovered 7,106 works and only 19 of them
   computational on a reading of their abstracts, so every measure of regional computational
   intensity falls once the corpus is complete. Colombia's screened share goes from 4.48% to
   3.84%. The region's computational work was largely not invisible; its experimental work
   was. What the region lacks is scale and continuity, and the gap in method uptake is real
   but modest.
3. **The method mix differs by region.** The world leans on molecular dynamics; Latin America
   leans on machine learning; Colombia leans on quantum chemistry. An infrastructural reading
   is available (sustained dynamics needs computing time the other two need less of), but the
   Colombian denominator is small and this belongs in the discussion as a hypothesis, not a
   finding.
4. **Generative methods are essentially absent**, worldwide and entirely so in the region.
   Reading all ten retrieved generative-AI works one by one leaves four credible
   biopolymer-specific works in the world literature, none from Latin America. Of everything
   in this report, that is the clearest opening — one of the four, on population-aware
   generation of lignin ensembles, addresses the same problem as this group's existing lignin
   line.
5. **There is no community and no venue.** Most authors in the computational layer publish
   there once, and the regional slice has no core journals. A thesis that wants to change
   something has a structural target, not only a topical one.

### Limitations

- **Two sources, not four.** Scopus and Web of Science were unavailable. OpenAlex and Lens
  disagree by about a third on regional counts, which bounds how precise any regional figure
  can be, and is itself reported as a result.
- **The screened shares are upper bounds.** The measured over-detection is 8.2%, not
  corrected in the tables, only stated. Read every screened percentage as a ceiling.
- **The world screened shares still rest on the English-only corpus.** The regional corpora
  were re-screened on the combined vocabulary; the world method layer gains only 12 works
  from it, so the world figures move by less than a tenth of a percentage point, but they
  were not rebuilt. (Open item #4 in `docs/00_plan.md`.)
- **Affiliation matching loses regional work.** Quantified in the source-triangulation
  section. The regional counts are a lower bound.
- **Abstract coverage.** Roughly 30% of the method-layer records carry no abstract in
  OpenAlex. Semantic Scholar and Europe PMC recovered 4,070 of them; the rest could not be
  read and are excluded from every screened share.
- **The screening *is* validated** — κ = 0.878 on the materials-vs-biological distinction it
  rests on, with a measured +8.2% directional bias (§3.4 above). *(Correcting a stale line
  that still appears in the current `report/informe_bibliometrico.tex` Limitations section,
  left over from before the validation pass was run; the report text should be updated to
  match.)*
- **English-language queries** undercount regional work published in Spanish and Portuguese
  (quantified in §5.6).
- **Country attribution** counts a work once per country present, so country columns sum to
  more than the corpus.

### What to do next

1. A third coding of a few dozen items by a domain expert — **closed, AC will not do this
   (2026-09-24), do not reopen.**
2. Extend the combined-vocabulary rebuild to the anchored lines and the world method layer,
   which still rest on English-only counts. Open.
3. Apply the venue-provenance check (used on the ten-work generative shortlist, which caught
   three impostor venues) to the whole corpus. Open — nothing in the field does this
   routinely.
4. Take the affiliation-matching loss seriously as a result in its own right: a measurable,
   publishable statement about how invisible small Latin American institutions are to the
   infrastructure that counts science.

## 7. References

From `refs/references.bib` — entries are added only for works quoted individually in the
documents or the report (the bibliometric counts themselves are not citations to individual
papers, they are aggregate query results):

> Camposano, Anthony Val; Gummesson Svensson, Hampus; Löwenmark, Karl; Mehandzhiyski,
> Aleksandar Y.; Zozoulenko, Igor. **"Population-aware Generative Modeling of Lignin
> Ensemble."** ChemRxiv preprint, 2026-09-02. DOI: 10.26434/chemrxiv.15008225/v1.
> https://chemrxiv.org/doi/full/10.26434/chemrxiv.15008225/v1
> *Note: open access, but the PDF sits behind a Cloudflare challenge that refuses
> command-line clients; see `refs/pdfs/README.md`. Not obtained — in AC's hands, not a
> project task (2026-09-24).*

Research collaborations/anchors identified from acknowledgements and harvested records
(`docs/00_plan.md` §1), not citations but attribution of institutional context:

- **GIFTEX** — Grupo de Investigación GIFTEX, Universidad Industrial de Santander,
  Bucaramanga, Colombia.
- **UNF** — Universidad Nacional de Frontera, Sullana, Piura, Perú.
- **Wilson Castro** — Universidad Nacional de Frontera / Universidad Nacional de Cañete,
  Perú; terahertz spectroscopy + ML for starch concentration and bioplastic thickness
  (2025 works, already in the harvested corpus).

## 8. Where everything lives

| Content | File |
|---|---|
| Plan / methodology design | `docs/00_plan.md` |
| Phase 1 — spatiotemporal mapping | `docs/01_bibliometric_mapping.md` |
| Phase 2 — networks and screening | `docs/02_networks_and_screening.md` |
| Source triangulation (Lens/S2/Europe PMC) | `docs/03_source_triangulation.md` |
| Generative frontier, read work by work | `docs/04_generative_frontier.md` |
| Screening validation (κ) | `docs/05_screening_validation.md` |
| Phase 3 — LatAm/Colombia argument | `docs/06_latam_colombia.md` |
| This file | `docs/07_full_record.md` |
| Session-by-session lab notebook | `docs/LOG.md` |
| Search equations, versioned, never edited in place | `queries/*.txt` |
| Raw counts / results tables | `outputs/tables/*.csv` |
| Figures | `outputs/figures/*.pdf` / `*.png` |
| Compiled report (PDF, generated, nothing hand-typed) | `report/informe_bibliometrico.pdf` |
| Report source | `report/informe_bibliometrico.tex` |
| Report generator | `scripts/python/build_report.py` |
| Bibliography | `refs/references.bib` |
| External reviews, archived verbatim | `docs/reviews/` |
