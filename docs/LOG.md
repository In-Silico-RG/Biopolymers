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
- Related material found elsewhere on disk, not yet pulled in: `../PHA/` holds a
  bibliometric protocol for polyhydroxyalkanoate R&D in .docx, which overlaps Phase 1 and
  should be read before writing the queries. `../Material_Proyectos_Amilosa/` holds three
  structured amylose projects and `../Lignin_Project/` the lignin line.
- Open for AC: identity and research lines of GIFTEX, UNF and Wilson Castro; Scopus and WoS
  access at UNISUCRE; Camila's programme, deadline and required document format; whether a
  journal article is a secondary target.
