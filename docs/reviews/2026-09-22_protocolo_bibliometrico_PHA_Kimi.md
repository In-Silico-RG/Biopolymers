# External protocol — Bibliometric analysis of polyhydroxyalkanoates (Kimi)

**Received.** Found on disk at `../PHA/Protocolo bibliométrico polyhidroxialcanoatos
R&D.docx`, pulled into this project 2026-09-22. Language: Spanish.
**Source.** Produced by Kimi (an AI assistant) in response to a prompt by AC asking for a
bibliometric protocol on PHA R&D using Lens.org and other free tools, covering world,
Latin American, Ibero-American and Colombian contexts.
**Verbatim copy.** `2026-09-22_protocolo_bibliometrico_PHA_Kimi.docx`, unmodified. Extract
the text with `pandoc -t plain <file>`.

This is source material, not a review of our work, but it is archived here under the same
rule: an external document that shapes the project is kept verbatim with an adjudication,
so nobody has to guess later which of its ideas we took.

## Summary of what it proposes

Eight phases: research questions; search-string design with a PHA thematic block and an
applications block, plus per-context geographic strings; a free-tool stack (Lens.org,
OpenAlex, Semantic Scholar, Publish or Perish, VOSviewer, bibliometrix, Dimensions,
Scimago); extraction and cleaning; analysis across production, impact, authors and
institutions, journals, and themes; a four-context comparison table; a figure list; and a
report structure. Window 2014–2024.

## Adjudication

### Accepted

- **The four-context comparison design** (world / Latin America / Ibero-America /
  Colombia). Adopted for Phase 3, with one change: Ibero-America is kept as a separate
  context because Spain and Portugal are the dominant collaboration partners of Colombian
  groups, and folding them into Latin America would hide exactly the dependency the thesis
  should measure.
- **The Latin American country list.** Adopted as the seed for our geographic filter, moved
  out of the prose and into a versioned file so a query is never retyped by hand.
- **The comparative indicator table** (total documents, annual growth, Q1–Q2 share, corpus
  h-index, citations per document, international collaboration share, top countries,
  institutions, journals and themes). Adopted nearly intact; it is a good skeleton for the
  Phase 3 results section.
- **The Colombian affiliation-variant warning.** Adopted and generalised into the
  normalisation step. Institution names in the region appear in Spanish, in English and
  abbreviated, and a count that ignores this understates regional output.
- **The advice to widen to Colombian authors regardless of publication country** when the
  Colombian slice is thin. Adopted as a validation step for Phase 3.
- **The tool list.** Consistent with what AC already decided on 2026-09-22.

### Rejected or changed

- **Bare acronyms in the search string** (`PHA`, `PHB` as standalone terms). Rejected. `PHA`
  collides with unrelated senses across the literature, and the protocol compounds the risk
  by proposing full-text and claims fields as search targets. Acronyms are used only bound
  to an expanded form or restricted to title and abstract, and every acronym's precision is
  measured on a sample before it enters the final string.
- **The 2014–2024 window.** Changed. The thesis runs in 2026 and its Phase 2 is about
  methods whose uptake is very recent, so a window ending in 2024 would cut the years that
  carry the argument. We use 1990–2025 for the long growth curve and report 2015–2025 for
  the comparative indicators, with 2026 excluded as incomplete.
- **Lens.org as the principal engine.** Changed. AC decided on 2026-09-22 to triangulate
  four sources. OpenAlex carries the reproducible core because it is a scriptable API, and
  Lens contributes the patent linkage, which is the thing it does better than the others.
- **Excel and manual steps** for deduplication, counting and classification. Rejected. Every
  count in this project comes from a script under `scripts/`, so a number can be traced to
  the code and the query version that produced it.
- **The applications block as a mandatory AND.** Rejected for the main corpus. Requiring an
  applications term would drop fundamental and computational work, which is precisely what
  Phase 2 is about. It is kept as an optional facet for subsetting, not as a filter on the
  corpus.
- **Patents inside the scholarly corpus.** Changed. Patents are analysed separately, never
  mixed into counts of scholarly works, because their citation behaviour and metadata are
  not comparable.

### Constraints adopted

- Every search string lives in a versioned file under `queries/` with its run date and
  record count; a modified string becomes a new version rather than an edit.
- Acronym precision is measured, not assumed.
- Patent and scholarly corpora stay separate.
- No count is produced by hand.
