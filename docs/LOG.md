# LOG — chronological lab notebook

*One dated entry per working session. Records what was decided, what was tried and
dropped, and the commits. Outcomes live in the numbered docs; this file keeps the order of
events and the dead ends. Every status change of a numbered doc gets a line here.*

Working mode: AC directs and decides; Claude executes, reports first, applies after an OK.
Language: English.

---

## 2026-09-22 — Session 1: Project opening and route definition

- Session opened on an empty `Biopolymers/` folder. No git repo, no documents.
- AC stated the project: reviewing the route for **Camila Argel's undergraduate thesis
  (proyecto de grado)**, subject biopolymers.
- First scoping attempt asked which single biopolymer would be the centre. AC rejected the
  framing: the scope is every biopolymer recognised as a subject of scientific study, not
  one system. Questions were reformulated.
- AC then described the route in full: a broad and deep literature review of biopolymers,
  focused on the ones worked in joint research with **GIFTEX**, **UNF** and **Wilson
  Castro**; first a bibliometric analysis to position the field in time and space; then a
  sweep of computational chemistry, chemoinformatics and artificial intelligence in
  biomaterials and biopolymers; narrowing at the end to the Latin American and Colombian
  setting.
- Decisions: "use all four sources, Scopus, Web of Science, OpenAlex/Lens, triangulated"
  (AC, 2026-09-22); "use all three tool stacks, bibliometrix/biblioshiny, VOSviewer and
  Python" (AC, 2026-09-22); "broad thematic scope anchored on cellulose, PHA/PHB, lignins
  and nanocellulose" (AC, 2026-09-22).
- Built: git repo initialised; logging templates copied from `~/.claude/templates/logging/`;
  directory tree created (`docs/`, `queries/`, `data/raw/{scopus,wos,openalex,lens}`,
  `data/processed/`, `scripts/{r,python}/`, `outputs/`, `refs/`, `Versiones/`);
  `docs/00_plan.md` written at revision r0 with the three phases.
- `docs/00_plan.md` status set to **draft**.
- Commit `da81921` 10:26 — Open Biopolymers project: repo scaffolding and route plan r0
- Related material found elsewhere on disk, not yet pulled in: `../PHA/` holds a
  bibliometric protocol for polyhydroxyalkanoate R&D in .docx, which overlaps Phase 1 and
  should be read before writing the queries. `../Material_Proyectos_Amilosa/` holds three
  structured amylose projects and `../Lignin_Project/` the lignin line.
- Open for AC: identity and research lines of GIFTEX, UNF and Wilson Castro; Scopus and WoS
  access at UNISUCRE; Camila's programme, deadline and required document format; whether a
  journal article is a secondary target.

---

## 2026-09-23 — Session 2: Phase 1 executed on OpenAlex

- AC: "adelante con la bibliometría", after the scoping questions were answered with every
  option selected. Taken literally: all sources, all tool stacks, broad scope.
- Read `../PHA/Protocolo bibliométrico polyhidroxialcanoatos R&D.docx`. It is an
  AI-produced (Kimi) protocol for a PHA bibliometric study. Archived verbatim with an
  adjudication at `docs/reviews/2026-09-22_protocolo_bibliometrico_PHA_Kimi.md`. Accepted
  its four-context design, country list, indicator table and affiliation-variant warning;
  rejected its bare acronyms, its 2014–2024 window, its Excel steps, its mandatory
  applications block, and mixing patents into the scholarly counts.
- Environment: no R and no `node` on this machine. Python venv at `.venv` with pandas,
  requests, pyalex, matplotlib. Figures therefore use matplotlib, and the dataviz palette
  validator could not be run, so the skill's pre-validated default palette was used
  unmodified rather than inventing one.
- Query design was empirical. Probed candidate blocks against OpenAlex before freezing
  anything. Two results decided the wording: the bare acronym `PHA` returns 56,015 records
  against 8,422 bound to its expanded form, and bare `DFT` 471 against 295 within the core.
  Bare acronyms were excluded everywhere.
- Second probe result changed the corpus definition: every family block intersected with a
  biopolymer framing is a **subset** of the generic framing string, so the generic string
  is the union, not a narrowing. Corpus defined as the field that self-identifies.
- Built: `queries/` with six frozen query files; `scripts/python/{probe_counts,corpora,
  harvest_aggregates,harvest_records,analyze_aggregates,make_figures,screen_abstracts}.py`.
- Harvested OpenAlex aggregates for 23 corpora across 8 facets, 185 CSV files under
  `data/raw/openalex/aggregates/`.
- **Dead end, with its cause.** A `sed` using `|` as its delimiter hit the `|` inside the
  text of `queries/p1_core_biopolymer_field_v1.txt`, failed, and left line 3 stripped of
  its leading `#`. Because `corpora.load()` only skipped lines starting with `#`, the
  broken header would have been concatenated into the search string and silently changed
  every count. Caught by reading the file, not by any test. The record harvest running at
  the time was killed and its partial output deleted. `corpora.load()` now raises when
  header words appear in a search string. The aggregate harvest had finished *before* the
  corruption and is unaffected; `core_world` = 145,743 matches the clean probe.
- **Blocker found.** OpenAlex now meters the anonymous API against a daily budget shared by
  everyone on the same IP, and the aggregate harvest exhausted it. Full-record downloads
  return HTTP 429 with `retryAfter` about 8 hours. A free API key lifts this. Recorded as
  an open question for AC; all record-level work is blocked until then.
- Results written to `docs/01_bibliometric_mapping.md`, status **in progress**. Nine tables
  in `outputs/tables/`, four figures in `outputs/figures/`.
- Headline findings. The field holds 145,743 works and grows at 11.4% a year. Under 2.63%
  of it uses any computational or AI method, roughly doubling over a decade. Latin America
  sits at 2.20% and Colombia at 1.94%, so the **regional deficit is volume, not method
  uptake** — which cuts against the expected narrative. Generative methods return 43 works
  worldwide. Lignin is the most computational anchor at 2.08%, PHA the least at 1.30%.
- **Caveat found in the data, not assumed.** The methods layer's largest topic is protein
  structure and dynamics, ahead of biodegradable polymer synthesis. The framing terms
  `biomacromolecule` and `natural polymer` drag structural biology into the corpus, so the
  materials-side method share is *lower* than 2.63%. Separating the two needs abstracts.
- AC, mid-session: "usa la API de deepseek si crees que nos ayuda a descargarte de tareas
  mecanicas". Applied to exactly that contamination problem, which is the one genuinely
  mechanical task at hand and which no keyword rule can solve. Built
  `scripts/python/screen_abstracts.py`: DeepSeek classifies each abstract as biopolymer
  materials or biological-function work, plus polymer family, method and whether
  experiments are reported, with every call cached on a prompt hash for reproducibility.
  Tested on two hand-written abstracts and it separated a cellulose-nanocrystal composite
  simulation from a hemoglobin allostery simulation correctly. It cannot run on the corpus
  until the OpenAlex records exist.
- Figure fixed after looking at it. The first version of `F2_methods_share.png` plotted
  Colombia's annual method share, which swung between 0 and 9 percent on 0–3 papers a year.
  Rebuilt on three-year rolling sums with points suppressed below 50 works in the window.
- Open for AC: an OpenAlex API key; Scopus and WoS access; whether to add Spanish and
  Portuguese query variants; the identities of GIFTEX, UNF and Wilson Castro.
