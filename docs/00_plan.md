# 00 — Plan: Literature route for Camila Argel's undergraduate thesis

*Started 2026-09-22. Master plan. Every numbered document in `docs/` hangs from a phase
defined here.*

**Objective.** Define and execute a broad, deep literature route on biopolymers that moves
from a bibliometric mapping of the whole field, through a sweep of computational chemistry,
chemoinformatics and artificial intelligence applied to biomaterials and biopolymers, and
narrows at the end to the Latin American and Colombian setting. The route is the backbone
of Camila Argel's undergraduate thesis (proyecto de grado).

**Status.** draft — 2026-09-22. Phases defined, queries not yet written, no data pulled.
Blocking items are listed in *Open questions*.

---

## 1. Framing

The thesis is a literature study, not a bench project. Its contribution is a defensible map
of a field: where the work on biopolymers is being done, by whom, on which polymers, and
how fast computational and AI methods are entering that work. The Latin American and
Colombian narrowing at the end is the part that makes it publishable rather than a course
exercise, because that slice is thin in the existing bibliometric literature.

Research collaborations that anchor the topic:

- **GIFTEX** — joint research line with UNISUCRE. [PENDIENTE: full name of the group, host
  institution, and the specific biopolymers worked on jointly.]
- **UNF** — joint research line. [PENDIENTE: confirm full name and country, and the shared
  line.]
- **Wilson Castro** — collaborating researcher. [PENDIENTE: affiliation and the topic of
  the joint work.]

These anchors matter for two reasons. They justify the thematic emphasis on cellulose,
PHA/PHB, lignins and nanocellulose, and they give Phase 3 a concrete set of authors and
institutions whose regional position the analysis can report.

## 2. The three phases

### Phase 1 — Spatiotemporal mapping of the biopolymers field

Position the field in time and space before judging anything about it. Deliverables:
publication and citation growth curves, country and institution production, journal and
source landscape, author and co-authorship structure, keyword co-occurrence and thematic
evolution, most-cited works and reference bursts.

Thematic scope is **broad**: polysaccharides, microbial polyesters, structural proteins,
lignins and nucleic-acid-based materials, with explicit anchoring on cellulose, PHA/PHB,
lignins and nanocellulose. Biomedical applications are kept in, not excluded, so that the
map is the whole field and the narrowing happens later by intention rather than by a
filter decided at the start.

Output document: `docs/01_bibliometric_mapping.md`.

### Phase 2 — Computational chemistry, chemoinformatics and AI in biomaterials and biopolymers

A sweep of the methodological layer sitting on top of the field mapped in Phase 1.
Coverage: molecular dynamics and coarse-grained simulation, DFT and quantum chemistry,
molecular descriptors and QSPR/QSAR, solubility and compatibility modelling (Hansen
parameters, COSMO-RS), docking and enzyme engineering for biopolymer degradation, machine
learning for property prediction, generative models for materials discovery, and large
language models and agents entering materials research.

The question this phase answers: which methods have actually taken hold on which
biopolymers, and where the method literature and the material literature fail to meet.
That gap is the natural opening for a thesis contribution.

Output document: `docs/02_computational_ai_sweep.md`.

### Phase 3 — Latin American and Colombian narrowing

Reduce both previous layers to the region. Deliverables: regional production and its growth
relative to the world, collaboration networks inside Latin America and with outside
partners, which countries lead on which biopolymers, funding and institutional
concentration, the position of Colombian groups, and how much of the regional output uses
computational or AI methods at all.

This is where GIFTEX, UNF and the Wilson Castro collaboration get located on the map, and
where the thesis states what the region is missing.

Output document: `docs/03_latam_colombia.md`.

## 3. Data sources

All four sources are used, and triangulated rather than merged blindly. This was decided
because no single source is adequate for a question that ends in Latin America.

| Source | Role | Access |
|---|---|---|
| Scopus | Core corpus; best commercial coverage of regional journals | [PENDIENTE: confirm UNISUCRE subscription] |
| Web of Science | Second commercial corpus; the bibliometric standard for comparison | [PENDIENTE: confirm access] |
| OpenAlex | Open corpus via API; full reproducibility, wide regional coverage | Open, no subscription |
| Lens.org | Cross-check and patent linkage | Free tier |

Records are deduplicated by DOI first, then by normalised title and year. Every source keeps
its raw export untouched under `data/raw/<source>/`; nothing is edited in place. Overlap and
divergence between sources is itself a reported result, not a nuisance to be hidden.

## 4. Tool stack

| Tool | Used for |
|---|---|
| Bibliometrix / biblioshiny (R) | Core metrics, thematic maps, Lotka and Bradford, three-field plots |
| VOSviewer | Publication-quality co-occurrence, co-authorship and co-citation maps |
| Python (pybliometrics, pyalex, NetworkX, pandas) | Retrieval, deduplication, custom network metrics, and the bridge to Phase 2 |

The Python layer is the one that carries into Phase 2, since the chemoinformatics sweep will
want the same tooling. R and VOSviewer produce the figures that reviewers of bibliometric
work expect to see.

## 5. Query design

Queries are versioned files under `queries/`, one per source and phase, each with its run
date and the record count it returned. A query is never edited in place: a change creates a
new numbered version, because the count is only interpretable against the exact string that
produced it. Search strings, inclusion and exclusion criteria, and the PRISMA-style flow of
records are reported in the thesis.

## 6. Repository layout

```
docs/          numbered working documents, LOG.md, reviews/
queries/       versioned search strings, one file per source and phase
data/raw/      untouched exports, one folder per source
data/processed/ deduplicated and harmonised corpora
scripts/r/     bibliometrix and VOSviewer preparation
scripts/python/ retrieval, deduplication, network analysis
outputs/       figures, tables, maps
refs/          references.bib
Versiones/     dated copies of important PDFs before overwriting
```

## Decisions

- Route is three phases: broad bibliometrics → computational/chemoinformatics/AI sweep →
  Latin American and Colombian narrowing (AC, 2026-09-22).
- All four data sources are used and triangulated, not one chosen (AC, 2026-09-22).
- All three tool stacks are used: bibliometrix/biblioshiny, VOSviewer and Python
  (AC, 2026-09-22).
- Thematic scope is broad, covering every biopolymer recognised as a subject of scientific
  study, with explicit anchoring on cellulose, PHA/PHB, lignins and nanocellulose
  (AC, 2026-09-22). Biomedical work is not excluded at the query stage.
- The project is a literature study; no bench work is planned (AC, 2026-09-22).

## Open questions

- GIFTEX: full name, host institution, and the biopolymers of the joint line. — AC.
- UNF: full name and country; the shared research line. — AC.
- Wilson Castro: affiliation and topic of the joint work. — AC.
- Scopus and Web of Science: does UNISUCRE have active access, and does Camila have
  credentials? Determines whether Phase 1 starts on OpenAlex alone. — AC.
- Camila's academic programme, thesis deadline, and the document format her programme
  requires. — AC.
- Whether the thesis targets a journal article as a secondary output, which would change how
  Phase 3 is written. — AC.

## Revision log

- **r0, 2026-09-22.** First version. Phases, sources, tools and scope set from the session
  of 2026-09-22.

## References

To be collected in `refs/references.bib`.
