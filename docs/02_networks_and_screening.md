# 02 — Co-authorship structure and the screened method layer

*Started 2026-09-23. Completes Phase 1 and opens Phase 2 of `00_plan.md`.*

**Objective.** Two things. Describe the collaboration structure of the field from the
harvested records, and replace the keyword-based method counts of
`01_bibliometric_mapping.md` with counts obtained by reading abstracts.

**Status.** in progress — 2026-09-23. Networks, productivity and concentration done on
OpenAlex records. Screening done for the world method layer and the regional corpora.
Still OpenAlex-only; Scopus, Web of Science and Lens not added.

---

## 1. What was harvested

With the API key, 28,556 full records across 14 corpora, in
`data/raw/openalex/records/`. The field selection carries authorships, institutions,
distinct-country counts, topics, funders and the inverted abstract index.

Abstract coverage is the binding constraint on everything in section 3. Roughly 70% of the
method-layer records carry an abstract, against about 90% of the regional core corpora.

## 2. Collaboration, productivity and concentration

| Corpus | Works | International | Single country | Two or more Latin American countries |
|---|---|---|---|---|
| World, method layer | 3,328 | 30.4% | 69.6% | 0.6% |
| Latin America, whole field | 8,175 | 34.4% | 65.6% | 6.0% |
| Latin America, method layer | 211 | 45.5% | 54.5% | 9.0% |
| Colombia, whole field | 598 | 44.1% | 55.9% | 23.9% |

Source `outputs/tables/T15_collaboration_shares.csv`.

**Colombia is the most internationally and most regionally connected of these corpora.**
Almost a quarter of Colombian biopolymer works involve a second Latin American country,
four times the regional average. Figure `F5_collaboration_matrix.png` shows why this stands
out: Brazil's strongest ties run outward, to the United States (228 works), Portugal (210)
and Spain (141), and dwarf its ties to Argentina (51) or Colombia (46). Colombia's
strongest partners are Mexico (49), Brazil (46) and Spain (46), which is a far more
balanced profile. Figure `F7_colombia_partners.png`.

### Author productivity

| Corpus | Authors | Publishing once | Fitted Lotka exponent |
|---|---|---|---|
| World, method layer | 14,861 | 86.3% | 3.46 |
| Latin America, whole field | 27,932 | 75.4% | 2.57 |
| Colombia, whole field | 2,014 | 79.9% | 2.95 |
| Latin America, method layer | 973 | 85.0% | 3.26 |

Classic Lotka behaviour gives an exponent near 2. Every corpus here is steeper, and the
**method layers are the steepest of all**. Of the 14,861 authors in the world method layer,
86% appear exactly once. Figure `F6_lotka.png`.

This is the structural finding behind the thin method share. There is no established
community of people who do computational work on biopolymers repeatedly. The layer is
mostly made of one-off contributions, which is what a field looks like before a speciality
forms rather than after.

### Journal concentration

| Corpus | Journals | Core-zone journals | As share of journals |
|---|---|---|---|
| World, method layer | 1,302 | 31 | 2.4% |
| Latin America, whole field | 1,870 | 42 | 2.2% |
| Colombia, whole field | 295 | 20 | 6.8% |
| Latin America, method layer | 136 | 18 | 13.2% |

Bradford's core zone is the set of journals carrying the first third of the output. The
world and regional fields behave normally at about 2%. The Latin American method layer does
not: it takes 13% of its journals to reach the first third, meaning **there is no journal
core for regional computational work on biopolymers**. It is scattered, with no venue that
functions as a home.

### Institutions

Latin America is led by Universidade de São Paulo (636 works), UNICAMP (545) and CONICET
(449). Inside Colombia the order is Universidad Nacional de Colombia (96), Universidad del
Valle (66), Universidad de Cartagena (47) and Universidad de Antioquia (47).
**Universidad de Sucre appears with 25 works and 6 collaborating institutions.** Full
rankings in `T19_institution_centrality_*.csv`.

Node-link renderings are not drawn here. A 115-node co-authorship graph is a hairball that
looks like analysis and reads like nothing, so the structure is shown as a matrix and the
network drawings are left to VOSviewer, which is built for them. Map and network pairs for
country, institution and author graphs are in `outputs/maps/`, ready to open directly.

## 3. Reading the abstracts

`scripts/python/screen_abstracts.py` classifies each abstract with DeepSeek: whether the
work is biopolymer **materials** research or biological-function research, which polymer
family, which computational method, and whether experiments are reported. Every call is
cached on a hash of the prompt, so the screening is reproducible and a re-run is free.

### 3.1 A correction that changed the numbers

The first pass offered a category called `other_computational`. Inspecting the Colombian
results showed it was catching factorial designs, response-surface methodology, ANOVA and
curve fitting to the authors' own measurements. Those are quantitative but they are not
computational chemistry, and including them put the Colombian computational share at 12.5%
when the defensible figure was about 3%.

Rather than re-screen every abstract under a new prompt, only that bucket was asked again,
with a question that names the distinction. 504 works were re-asked across all corpora:

| Verdict | Works |
|---|---|
| statistical design of experiments | 221 |
| no modelling at all | 127 |
| molecular modelling | 135 |
| informatics | 21 |

Statistical design of experiments is excluded from every computational count that follows.
First-pass files are kept as `*.firstpass.csv` so the correction is auditable.

### 3.2 The contamination, measured

Of the 3,951 works in the world method layer, 70.1% carry an abstract. Of those:

| Class | Works | Share of classified |
|---|---|---|
| Biopolymer materials research | 1,542 | 55.6% |
| Biological-function research | 1,229 | 44.4% |

Nearly half of what the keyword query called computational biopolymer research is protein
folding, enzyme mechanism and nucleic-acid biology. The method share of the field therefore
falls:

| Measure | Value |
|---|---|
| Keyword estimate | 2.63% |
| Restricted to materials research | 1.46% |
| Restricted to materials **and** a genuine computational method | 1.26% |

### 3.3 Keyword queries undercount the regional field

The opposite correction appears in the regional corpora, and it is just as important.
Screening the **whole** Colombian and Latin American fields, rather than the keyword-selected
method layer, finds computational work the query missed:

| Corpus | Materials works screened | With a computational method | Share | Keyword estimate |
|---|---|---|---|---|
| Latin America | 4,425 | 163 | 3.68% | 2.20% |
| Colombia | 393 | 20 | 5.09% | 1.94% |

Reading abstracts raises the regional estimate by roughly 1.7 times. **Colombia sits above
the Latin American average, not below it**, which reverses the ordering reported in
`01_bibliometric_mapping.md` section 4 from the keyword counts. The keyword-based ordering
should not be quoted.

The regional core corpora are also far cleaner than the method layer: 90.4% of Latin
American and 92.3% of Colombian works are materials research. The structural-biology
contamination is concentrated in the method layer, where the framing terms overlap with
computational biophysics vocabulary.

### 3.4 Which methods, and on what

Method mix of the materials-only subset, as a percentage of each context:

| Method | World | Ibero-America | Latin America | Colombia |
|---|---|---|---|---|
| Molecular dynamics | 33.9 | 28.9 | 23.1 | 22.2 |
| Machine learning | 25.2 | 30.6 | 33.3 | 22.2 |
| Quantum chemistry | 15.8 | 20.7 | 23.1 | 33.3 |
| Docking | 4.8 | 3.3 | 2.6 | 0.0 |
| Solubility modelling | 3.5 | 1.7 | 0.0 | 0.0 |
| QSAR / QSPR | 1.4 | 0.0 | 0.0 | 0.0 |
| Generative | 0.6 | 0.0 | 0.0 | 0.0 |

**The region uses a different method mix from the world.** Worldwide the layer is led by
molecular dynamics; in Latin America machine learning leads and quantum chemistry is level
with dynamics; in Colombia quantum chemistry leads outright. One plausible reading is
infrastructural, since sustained molecular dynamics needs computing time that machine
learning and single-molecule quantum chemistry calculations do not, but the corpora behind
the Colombian column are small and this should be treated as a hypothesis to test, not a
result.

Generative methods and QSAR are absent from the region entirely. Worldwide, generative work
amounts to ten works in the materials subset.

Polymer mix of the same subset shows Colombia concentrated on chitosan (22.2%), against a
world share of 9.3%, and on lignin (11.1%) against 4.7%.

Just over half of the world's computational biopolymer work is coupled to experiments
(52.7%), falling to 44.9% in Latin America. This is not an isolated modelling community.

## 4. The partial year, and why it is not dropped

2026 was originally excluded from the curves as incomplete. AC questioned that on
2026-09-23 and the exclusion was wrong. The OpenAlex harvest never filtered by year, so the
records were always present; only the analysis discarded them.

| Context | Method works, all of 2025 | Method works, 2026 to date | 2026 as a share of 2025 |
|---|---|---|---|
| World | 610 | 722 | 118% |
| Ibero-America | 57 | 67 | 118% |
| Latin America | 39 | 44 | 113% |
| Colombia | 2 | 7 | 350% |

The whole field sits at 63–84% of its 2025 volume at the same date, so the method layer is
not merely keeping pace, it is pulling away. On the screened, materials-only, strictly
computational subset the same shape holds: 156 works in 2024, 221 in 2025, and 248 by late
2026. Dropping the year would have hidden the acceleration the thesis is about.

2026 is therefore in every corpus and every curve, drawn with a hollow marker so it cannot
be mistaken for a complete year. Compound growth rates still use 2015–2025 only, because a
partial year cannot enter a compound rate. `outputs/tables/T25_partial_year_2026.csv` holds
the year on its own.

## Decisions

- Statistical design of experiments, response-surface methodology and curve fitting are not
  counted as computational chemistry (2026-09-23).
- Node-link network figures are not produced; the matrix carries the structure and
  VOSviewer receives the graphs (2026-09-23).
- The keyword-based ordering of contexts by method share in `01_bibliometric_mapping.md`
  section 4 is superseded by section 3.3 here (2026-09-23).
- 2026 is kept in the corpus and in every curve, flagged as partial, and excluded only from
  compound growth rates (AC, 2026-09-23, reversing the earlier exclusion).

## Open questions

- About 30% of the method-layer records carry no abstract. Recovering those from Crossref
  would firm up every share in section 3. — AC to decide whether it is worth the pass.
- Should the screening be validated against a hand-coded sample? A few hundred works
  double-coded by Camila would give an agreement figure and make the method defensible to
  a referee. — AC.
- Scopus and Web of Science access, still pending, which is what triangulation needs. — AC.
- Spanish and Portuguese query variants for the regional slices. — AC.
- GIFTEX, UNF and Wilson Castro: names and lines, to place them on the institution map. — AC.

## References

To be collected in `refs/references.bib`.
