# 00 — Plan: Literature route for Camila Argel's undergraduate thesis

*Started 2026-09-22. Master plan. Every numbered document in `docs/` hangs from a phase
defined here.*

**Objective.** Define and execute a broad, deep literature route on biopolymers that moves
from a bibliometric mapping of the whole field, through a sweep of computational chemistry,
chemoinformatics and artificial intelligence applied to biomaterials and biopolymers, and
narrows at the end to the Latin American and Colombian setting. The route is the backbone
of Camila Argel's undergraduate thesis (proyecto de grado).

**Status.** in progress — 2026-09-24. All three phases written and the regional corpora
screened on the combined vocabulary. Two items remain, both extensions rather than gaps. Phase 1 complete, Phase 2 done and validated, Phase 3
written as an argument on the corpus rebuilt and re-screened in three languages. The report
is `report/informe_bibliometrico.pdf`, 14 pages.

---

## 1. Framing

The thesis is a literature study, not a bench project. Its contribution is a defensible map
of a field: where the work on biopolymers is being done, by whom, on which polymers, and
how fast computational and AI methods are entering that work. The Latin American and
Colombian narrowing at the end is the part that makes it publishable rather than a course
exercise, because that slice is thin in the existing bibliometric literature.

Research collaborations that anchor the topic:

- **GIFTEX** — Grupo de Investigación GIFTEX, Universidad Industrial de Santander,
  Bucaramanga, Colombia. Identified 2026-09-23 from the acknowledgement in
  `../Lignin_Project/Testing_Lignin_Structure_Generators/manuscript/`, not assumed.
- **UNF** — Universidad Nacional de Frontera, Sullana, Piura, Perú; the joint line runs
  through its Instituto de Investigación and its Facultad de Ingeniería de Industrias
  Alimentarias y Biotecnología.
- **Wilson Castro** — Universidad Nacional de Frontera, Sullana, and also publishing with
  Universidad Nacional de Cañete, Perú. His work sits exactly on the intersection this
  thesis studies: terahertz spectroscopy combined with machine learning to predict starch
  concentration and to estimate bioplastic thickness, both 2025. Those works are already
  inside the harvested corpus.

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
| OpenAlex | Base corpus via API; full reproducibility, widest regional coverage | Key held |
| Lens.org | Second corpus via API; independent index, patent linkage | Token held to 2026-09-29 |
| Semantic Scholar | Abstract recovery where OpenAlex has none | Open, no key needed |
| Europe PMC | Abstract recovery, biomedical-adjacent remainder | Open, no key needed |
| ~~Scopus~~ | ~~Commercial index~~ | **No access at UNISUCRE (AC, 2026-09-23)** |
| ~~Web of Science~~ | ~~Commercial index~~ | **No access at UNISUCRE (AC, 2026-09-23)** |

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
  **Amended 2026-09-23 (AC): Scopus and Web of Science are unavailable at UNISUCRE.** The
  four sources are OpenAlex, Lens, Semantic Scholar and Europe PMC. The principle stands,
  the roster changed.
- All three tool stacks are used: bibliometrix/biblioshiny, VOSviewer and Python
  (AC, 2026-09-22).
- Thematic scope is broad, covering every biopolymer recognised as a subject of scientific
  study, with explicit anchoring on cellulose, PHA/PHB, lignins and nanocellulose
  (AC, 2026-09-22). Biomedical work is not excluded at the query stage.
- The project is a literature study; no bench work is planned (AC, 2026-09-22).

## Open questions

- ~~GIFTEX, UNF and Wilson Castro: names and affiliations.~~ **Resolved 2026-09-23** from
  the lignin manuscript acknowledgements and the harvested records. See section 1.
- ~~Scopus and Web of Science access.~~ **Closed 2026-09-23 (AC): there is none.**
  Triangulation runs on OpenAlex, Lens, Semantic Scholar and Europe PMC. Do not reopen.
- Camila's academic programme, thesis deadline, and the document format her programme
  requires. — AC.
- Whether the thesis targets a journal article as a secondary output, which would change how
  Phase 3 is written. — AC.

## Where this stands, 2026-09-24

**Done.** The field mapped in time and space, with co-authorship networks, Lotka and
Bradford. The computational layer measured by reading abstracts rather than matching
keywords, and that reading validated against an independent second coder at Cohen's kappa
0.878 on the distinction that matters, with a directional bias of +8.2% measured and
stated. The generative frontier read work by work. Triangulation against Lens. The
Spanish and Portuguese undercount and the affiliation-matching loss both quantified.

**Not done, in the order it is worth doing.**

1. ~~Write Phase 3 as an argument.~~ **Done 2026-09-24**, `06_latam_colombia.md`.
2. ~~Rebuild the headline corpus on the combined vocabulary.~~ **Done 2026-09-24.** It
   inverted the expectation: the recovered literature is almost entirely non-computational,
   so the regional method share falls rather than rises.
3. ~~Re-run the abstract screening on the combined corpus.~~ **Done 2026-09-24.** 14,709
   abstracts screened; regional screened shares fall, Colombia 4.48% to 3.84%.
4. **Extend the combined-vocabulary rebuild to the anchored lines and the world method
   layer**, which still rest on English-only counts. The world layer gains only 12 works
   from the combined string, so this moves the world figures by less than a tenth of a
   point; it matters for the anchors, not for the headline.
5. **Apply the venue-provenance check to the whole corpus.** It found three impostor venues
   in a shortlist of ten and nothing in the field does it routinely.

**Decisions that are closed and should not be reopened.** Scopus and Web of Science are
unavailable (AC, 2026-09-23). 2026 stays in the corpus, flagged as partial (AC, 2026-09-23).
Statistical design of experiments is not computational chemistry (2026-09-23). **No third
human coding of the screening sample: AC will not do it (AC, 2026-09-24).** The Camposano
lignin preprint is in AC's hands and is not a project task (AC, 2026-09-24).

## Revision log

- **r0, 2026-09-22.** First version. Phases, sources, tools and scope set from the session
  of 2026-09-22.
- **r1, 2026-09-23.** Status moved to in progress. No change to the phases. Phase 1 ran on
  OpenAlex alone because the other three sources need credentials or a key; the
  triangulation decision stands and is simply not yet executed.
- **r4, 2026-09-24.** Phase 3 written and the corpus rebuilt in three languages. The
  rebuild inverted the expected direction and conclusion 2 of the report was rewritten.
- **r3, 2026-09-24.** Status section *Where this stands* added, listing what is done and
  the four things that remain. No change to the phases or to any decision.
- **r2, 2026-09-23.** Source roster amended: Scopus and Web of Science are unavailable and
  are replaced by Lens, Semantic Scholar and Europe PMC. Collaborators identified from the
  record rather than guessed: GIFTEX at Universidad Industrial de Santander, UNF as
  Universidad Nacional de Frontera in Sullana, and Wilson Castro at UNF. 2026 restored to
  the corpus after AC questioned its exclusion.

## References

To be collected in `refs/references.bib`.
