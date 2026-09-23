# 03 — Source triangulation: Lens, Scopus and Web of Science

*Started 2026-09-23. Serves every phase of `00_plan.md`.*

**Objective.** Get the three remaining sources into the project, so the counts reported so
far from OpenAlex alone can be triangulated rather than trusted.

**Status.** in progress — 2026-09-23. Search equations written in native syntax for all
three platforms and frozen in `queries/platform_*_v1.txt`. Nothing downloaded: Lens needs an
account and Scopus and WoS need institutional access. This document is the instruction
sheet for that download.

---

## 1. Why this matters more than another OpenAlex pass

Everything in `01_bibliometric_mapping.md` and `02_networks_and_screening.md` comes from one
source. OpenAlex is inclusive, which is an advantage for regional coverage and a liability
for precision, and it has no editorial boundary at all. A referee will ask whether the
1.26% computational share is a property of the field or a property of OpenAlex. Only a
second source answers that.

The three sources are not interchangeable. Scopus and Web of Science are curated and will
return smaller, cleaner corpora. Lens is the only one of the four that links scholarly
works to patents, which matters because the archived PHA protocol was right that industrial
R&D on biopolymers shows up in patents before it shows up in papers.

## 2. Lens.org

**What is needed.** A free account at lens.org. No institutional subscription. This is the
one you can start today.

**What to run.** The six blocks in `queries/platform_lens_v1.txt`, under Scholarly Works.
Run the patent search separately, never mixed into the scholarly counts.

**Caution on the field names.** The country and date filters in that file follow Lens's
documented schema but were not tested against a live account. If a string is rejected, use
the left-hand facet panel for country and year instead and leave the topical block alone.
The topical block is the part that has to be reproducible; the filters are reproducible
either way as long as the run is recorded.

**Export.** CSV and BibTeX both, same search, same day. The free tier caps the export size
and the cap has changed more than once, so read the number the platform shows rather than
trusting any figure written down here. If the cap bites, segment by year and export one
slice per year, which is cleaner than segmenting by subtopic because the slices cannot
overlap.

## 3. Scopus

**What is needed, and this is the list to check with the library:**

1. An active UNISUCRE subscription to Scopus, and **which** subscription, since the content
   entitlement varies.
2. Credentials for Camila, plus a working off-campus route, either the institutional login
   or the VPN.
3. Whether an API key is available through dev.elsevier.com. A key tied to the institutional
   IP would let the harvest be scripted, which makes it reproducible and removes the export
   caps. Without it every corpus has to be exported by hand through the web interface.

**What to run.** The six blocks in `queries/platform_scopus_v1.txt`.

**Export.** CSV, with abstracts and affiliations included in the field selection. The
per-export cap is much lower when abstracts are included than when they are not, so plan on
segmenting by publication year. Name each file for the block and the year range it holds.

## 4. Web of Science

**What is needed:**

1. An active UNISUCRE subscription to the Core Collection.
2. **Which indexes the subscription covers**: SCIE, SSCI, AHCI, ESCI, CPCI, BKCI. This is
   the single most important thing to find out, and it is often missed. Whether ESCI is
   included changes regional counts substantially, because a large share of Latin American
   journals sit in ESCI rather than SCIE. A Web of Science count without a statement of the
   indexes searched is not interpretable and a referee will say so.
3. Credentials for Camila and off-campus access.

**What to run.** The six blocks in `queries/platform_wos_v1.txt`.

**Export.** Tab-delimited or Excel, with "Full Record" so abstracts and addresses come
through. Web of Science exports in fixed batches, so a corpus of several thousand needs
several files. Keep them, do not concatenate by hand; the merge is scripted.

## 5. The comparability trap

The three platforms do not search the same fields, and this alone can produce a difference
that looks like coverage but is not.

| Source | What the topical search covers |
|---|---|
| OpenAlex | title and abstract |
| Scopus, TITLE-ABS-KEY | title, abstract, author keywords, indexed keywords |
| Scopus, TITLE-ABS | title and abstract |
| Web of Science, TS= | title, abstract, author keywords, KeyWords Plus |
| Web of Science, TI= OR AB= | title and abstract |

Run **both** the wide and the narrow form on Scopus and Web of Science and record both
counts. The narrow form is what compares to OpenAlex; the wide form is what the field
conventionally reports. The gap between them belongs in the methods section of the thesis,
because it quantifies how much of a bibliometric count is an artefact of the search field
rather than of the literature.

## 6. What to hand back

Drop the exports into the folders that already exist, untouched, one folder per source:

```
data/raw/scopus/     data/raw/wos/     data/raw/lens/
```

Name every file `<block>_<yearrange>_<YYYY-MM-DD>.csv`, for example
`S1_core_2015-2025_2026-09-30.csv`. Then fill in the run date and the record count in the
matching `queries/platform_*_v1.txt` file, because a count without its exact string and its
date cannot be checked later.

Deduplication across sources, harmonisation of the field names and the merge into a single
corpus are scripted once the files are there. Nothing needs to be cleaned by hand, and
nothing should be.

## Decisions

- Patents are searched and reported separately from scholarly works, never merged into the
  same counts (2026-09-22, carried from the PHA protocol adjudication).
- Both the wide and narrow field forms are run on Scopus and Web of Science, and both counts
  reported (2026-09-23).
- Exports are segmented by year rather than by subtopic when a cap bites, because year
  slices cannot overlap (2026-09-23).

## Open questions

- Does UNISUCRE have active Scopus and Web of Science subscriptions, and does Camila have
  credentials and off-campus access? — AC.
- Which Web of Science indexes does the subscription cover, ESCI in particular? — AC.
- Is a Scopus API key obtainable through the institution? It would replace the manual
  exports with a scripted harvest. — AC.
- Should Spanish and Portuguese term variants be added for the regional slices? They matter
  more on Scopus and Lens than on Web of Science. — AC.

## References

To be collected in `refs/references.bib`.
