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
- Commit `10c8c01` 10:51 — Phase 1: bibliometric mapping of the biopolymers field on OpenAlex
- Open for AC: an OpenAlex API key; Scopus and WoS access; whether to add Spanish and
  Portuguese query variants; the identities of GIFTEX, UNF and Wilson Castro.

---

## 2026-09-23 — Session 3: API key, networks, and the screened method layer

- AC supplied an OpenAlex API key for insilico@unisucre.edu.co. Stored at
  `~/.openalex_key`, mode 600, exported from `.bashrc`, never in the repository.
  `corpora.api_key()` reads the environment first, then that file.
- Harvested 28,556 full records across 14 corpora. Two API corrections: `grants` is not a
  valid select field on this version and was replaced with `awards` and `funders`; added
  `countries_distinct_count` so the international-collaboration share is read from the API
  rather than parsed out of authorships.
- Screened the world method layer, 3,951 works, with DeepSeek on a 12-thread pool. Result:
  70.1% carry an abstract, and of those only 55.6% are biopolymer materials research. The
  keyword method share of 2.63% falls to 1.46%.
- **Correction, found by inspecting the output rather than trusting it.** The Colombian
  screening put the computational share at 12.47%, which looked wrong against the keyword
  2.8%. Reading the titles showed the `other_computational` category was catching factorial
  designs, response-surface methodology and curve fitting. Rather than re-screen 12,000
  abstracts under a new prompt, only that bucket was re-asked with a question naming the
  distinction: 504 works, of which 221 turned out to be statistical design of experiments
  and 127 no modelling at all. `statistical_doe` is now excluded from every computational
  count, the strict world figure is 1.26%, and the Colombian figure is 5.09%. First-pass
  files kept as `*.firstpass.csv`.
- AC: "sigue con las redes de coautoría y el cribado latinoamericano". Both done.
- Networks built with networkx: country, institution and author co-authorship with degree,
  weighted degree and betweenness, plus Louvain clusters. VOSviewer map+network pairs
  written to `outputs/maps/` for all five graphs, since VOSviewer is the right tool for the
  node-link rendering and matplotlib is not.
- **Decision on figures.** No node-link figure was drawn. A 115-node co-authorship graph is
  a hairball; the collaboration structure went into a matrix instead (`F5`), which is
  legible, and the graphs went to VOSviewer.
- Findings. Colombia is the most internationally (44.1%) and most regionally (23.9% with a
  second Latin American country) connected corpus measured, four times the regional average,
  while Brazil's strongest ties run outward to the United States, Portugal and Spain.
  Lotka exponents are 2.6 to 3.5 against a classic 2, and the method layers are steepest:
  86% of the 14,861 authors in the world method layer appear exactly once, so there is no
  standing community of computational biopolymer researchers. Bradford's core zone is 2%
  of journals worldwide but 13% for the Latin American method layer, meaning that work has
  no home venue. Universidad de Sucre appears in the Colombian institution ranking with 25
  works.
- **Reversal worth flagging.** Screening the whole regional fields rather than the
  keyword-selected layer raises Latin America to 3.68% and Colombia to 5.09%, so Colombia is
  *above* the regional average, not below as the keyword counts in
  `01_bibliometric_mapping.md` section 4 said. That section is now marked superseded.
  Keyword bibliometrics undercounts the region by about 1.7 times.
- The regional method mix differs from the world's: molecular dynamics leads worldwide,
  machine learning leads in Latin America, quantum chemistry leads in Colombia. Offered as
  a hypothesis about computing infrastructure, not as a result, because the Colombian
  denominator is nine works.
- Written to `docs/02_networks_and_screening.md`, status in progress.
- Open for AC: whether to recover the missing 30% of abstracts from Crossref; whether
  Camila should hand-code a validation sample against the screening; Scopus and WoS access;
  Spanish and Portuguese query variants; the identities of GIFTEX, UNF and Wilson Castro.

---

## 2026-09-23 — Session 4: Lens, the partial year, attribution loss, and the report

- AC supplied a Lens API token after being shown the exact page, which sits under the
  account at lens.org/lens/user/subscriptions rather than in the search interface. The 401
  he first hit meant no credentials, not a rejected token; a checker now tells the two apart.
- Lens harvested: 179,860 records across 11 corpora. Stopped twice on the two largest world
  anchors with HTTP 429 after long scrolls; the API answered normally minutes later, so the
  backoff was made patient rather than failing fast. The trial subscription runs to
  2026-09-29, which is why the harvest was ordered by priority rather than run blind.
- **AC asked why 2026 was missing. The exclusion was wrong and is reversed.** The OpenAlex
  harvest never filtered by year, so its records always held 2026 and the screening already
  covered it; only the analysis dropped it. The Lens, Scopus and WoS query files did carry a
  2025 cap and were corrected before any download. Justification: the world method layer
  holds 722 works in 2026 against 610 for all of 2025, while the field as a whole sits at
  63-84% of its 2025 volume, so the year carrying the strongest signal was the one being
  discarded. Figures now draw 2026 with a hollow marker, and the dashed segment is anchored
  to the single-year 2025 value rather than to the rolling window, which would have
  exaggerated the jump.
- **Bug introduced and caught by AC's follow-up question.** Extending the year range made the
  comparative window sum 2015-2026 while still labelled 2015-2025; the world figure moved
  from 90,931 to 102,560 under an unchanged column header. Now bounded at both ends.
- **AC: "acceso a Scopus y Web of Science... NO HAY! no insista!"** Both closed as sources,
  recorded as a decision with date, and removed from every open-questions list. The query
  files stay for reproducibility by others. Source roster is now OpenAlex, Lens, Semantic
  Scholar and Europe PMC.
- Collaborators identified from the record rather than by asking again. GIFTEX is a research
  group at Universidad Industrial de Santander; UNF is Universidad Nacional de Frontera,
  Sullana, Piura; Wilson Castro is at UNF and also publishes with Universidad Nacional de
  Cañete. Found in the acknowledgements of `../Lignin_Project/`, which was on disk the whole
  time. Lesson recorded: search the sibling projects before listing something as an open
  question for AC.
- **AC challenged Universidad Nacional de Cañete as non-existent. It exists** (public, San
  Vicente de Cañete, SUNEDU licence 116-2018-SUNEDU/CD), but checking exposed a real defect.
  OpenAlex matched only one of that paper's six authorships, to Universidad de Guadalajara,
  leaving both Peruvian affiliations unmatched, so the work counts as Mexican and Peru gets
  nothing. Quantified: 12.7% of authorships in the world method corpus match no institution,
  and per-country loss reaches 27% for Bolivia and 10% for Venezuela. Since every regional
  corpus was selected on institution country, the regional counts are a lower bound. This is
  now a result in the report, not only a caveat.
- Abstract recovery finished. Crossref returned 2.1% because Elsevier deposits no abstracts
  there, verified on three Elsevier DOIs. Replaced by a cascade: Semantic Scholar recovered
  2,403 and Europe PMC 1,667, for 4,113 of 9,433 overall. The screener now falls back to
  them and every corpus was re-screened, which moved the strict world share from 1.26% to
  1.27% and the materials fraction from 55.6% to 56.6%.
- Triangulation measured. Lens holds 91% of the OpenAlex world corpus but 66% of the Latin
  American one and 57% of the Colombian one, so the choice of source matters most exactly
  where this thesis focuses. Overlap is asymmetric: 76-100% of Lens records are in OpenAlex
  against 24-75% the other way, and Lens still contributes works OpenAlex lacks.
- `author_profile.py` added after AC asked about Marianny Combariza and César Sierra.
  Marianny Combariza has 31 works in the corpus, on fique nanocellulose, TEMPO oxidation and
  PHA from cacao waste, with molecular dynamics entering from 2025. César Sierra has 8, led
  by two Cu-BTC-on-cellulose papers from 2012 and 2014 holding 345 citations between them.
  Note: searching by surname alone conflates people; "Sierra" returned 18 works, "Cesar
  Sierra" 8.
- **AC: "donde esta el informe?"** Fair. There were working documents but no report.
  `scripts/python/build_report.py` now generates `report/informe_bibliometrico.tex` with
  every number read from `outputs/tables/`, compiles it in two pdflatex passes, removes the
  auxiliary files and verifies with pdftotext. Nine pages, seven figures, eight tables, no
  hand-typed values, because several numbers changed twice in one day.
- Open for AC: a hand-coded validation sample against the screening; Spanish and Portuguese
  query variants; whether to renew Lens past 2026-09-29.

### 2026-09-23, later: refine completed, report rebuilt

- The refine pass crashed on its first run: two screening threads reached the same corrupt
  cache entry, the first removed it and the second died on `FileNotFoundError`. Cause was a
  non-atomic cache write producing half-written entries. Fixed with a temp-file-and-rename
  write and a tolerant unlink, then rerun.
- Second run re-asked 599 works: 263 statistical design of experiments, 179 no modelling,
  137 molecular modelling, 20 informatics.
- With the recovered abstracts folded in, the unreadable share of the world method layer
  fell from 29.9% to 20.2%, and 1,784 works are classified as biopolymer materials research
  against 1,542 before.
- Final figures: strict world method share 1.28% against a keyword 2.63%; Latin America
  3.43% and Colombia 4.48% on screened abstracts, both above their keyword estimates, with
  Colombia still above the regional average.
- Lens will not finish its two largest world anchors; it stops with HTTP 429 after long
  scrolls on every attempt. 13 corpora and 179,860 records are on disk and those two have
  their Lens totals recorded, which is what the source comparison needs. Not retried further.
- Report rebuilt from the updated tables and verified with pdftotext: 9 pages, 3,191 words.
- Commit `9717282` — Rebuild the report after the completed refine pass.

---

## 2026-09-23 — Session 5: validation, language variants, and the generative frontier

- AC rejected leaving the screening validation to Camila: "NOPE, VALIDA TU, O DILE A
  DEEPSEEK API QUE VALIDE". Taken, with one correction of design: DeepSeek cannot validate
  its own labels, because the same model repeats the same mistakes and reports high
  agreement with itself. The second coder is Claude, a different model, coding blind.
- 125 abstracts double-coded, 100 random plus 25 drawn from thin categories, shuffled
  together so the stratum could not be inferred. Cohen's kappa rather than percent
  agreement, because percent agreement flatters a dominant class.
- **Result: kappa 0.878** on materials-versus-biological, the distinction the whole
  correction rests on; 0.782 on computational-at-all; 0.816 on method family; 0.767 on
  polymer family. Substantial to almost perfect throughout.
- **Directional bias found and quantified.** DeepSeek calls 79 of 100 works computational
  against the second coder's 73, +8.2% relative. Five of the seven disputed works were
  labelled `ml` for merely mentioning artificial intelligence as a closing outlook, in
  reviews and in purely experimental papers. Every screened share is therefore an upper
  bound and the strict world figure of 1.28% is closer to 1.18%. Same direction as every
  other correction in this project.
- AC: "ok, ADELANTE CON ESO" on Spanish and Portuguese variants. Frozen as
  `queries/p1_core_es_pt_v1.txt` and `p1_anchors_es_pt_v1.txt`, run as a **set difference**
  against the English corpus rather than a count comparison, so what is reported is what
  the English string misses. Additions: core field +15.4% for Latin America and +26.3% for
  Colombia; cellulose +26.9% and +31.2%; PHA +13.8% and +34.1%; lignin +14.6% and +17.9%.
  The regional deficit is partly linguistic, and with the affiliation-matching loss the
  regional figures understate the region twice over for two independent reasons.
- AC: "HAGAMOS LO MISMO, DEEPSEEK AND CLAUDE PARA ESO" on the generative works. Both read
  all ten. Three disagreements, all material, in `docs/04_generative_frontier.md`: ten
  records are nine works, one arXiv preprint indexed twice; the lignin paper trains
  autoregressive *molecular* language models over SMILES and is not an LLM paper; and three
  of the ten sit in venues whose DOI prefixes belong to other registrants, with 10.71465
  registered to International Study Counselor while publishing as "Frontiers in
  Agriculture" against Frontiers Media's own 10.3389. Stripping those and the
  non-biopolymer work leaves four credible works.
- The most relevant work in the whole generative slice to this group is *Population-aware
  Generative Modeling of Lignin Ensemble*, which trains on 1.16M structures from
  LigninGraphs and rewards a population rather than individual molecules. Adjacent to
  `../Lignin_Project/`.
- Cleaned stale open questions that had been resolved but left listed in docs 01 and 02.
- Report rebuilt at 10 pages with the validation and language sections.
- Open for AC: a third coding of a few dozen items by Camila as a domain-expert check on
  two automatic coders that may share a bias; whether to apply the venue-provenance check
  to the whole corpus rather than to the generative shortlist.
