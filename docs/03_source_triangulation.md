# 03 — Source triangulation: Lens, Semantic Scholar and Europe PMC

*Started 2026-09-23. Serves every phase of `00_plan.md`.*

**Objective.** Get the three remaining sources into the project, so the counts reported so
far from OpenAlex alone can be triangulated rather than trusted.

**Status.** in progress — 2026-09-23. **Scopus and Web of Science are out: UNISUCRE has no
access (AC, 2026-09-23), and this is not to be revisited.** Lens is harvested, 179,860
records across 11 corpora. Triangulation therefore runs on OpenAlex against Lens, with
Semantic Scholar and Europe PMC as the third and fourth sources for abstracts. The Scopus
and Web of Science query files are kept for the day someone else runs them, not as a
pending task.

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

**Lens has an API, and it is the better route.** The manual export below is the fallback.
`POST https://api.lens.org/scholarly/search` with `Authorization: Bearer <token>` is live;
an unauthenticated probe returns 401, which is how we know the endpoint is right. It
accepts Lucene-style `query_string` with explicit AND/OR/NOT, so the same strings serve the
web interface and the API unchanged.

**How to get a token, precisely.** The page is not obvious from the front page; it lives
under the account, not under the search interface.

1. Sign in at lens.org.
2. Go to **https://www.lens.org/lens/user/subscriptions** directly, or navigate there through
   the **Our Apps** menu, then **API and Data**. The same page is reachable from the user
   profile as the **API and Data** tab.
3. Click **Select This Plan** on the plan you want. That opens the service request form.
4. Fill it in with real detail: who you are, the institution, what the data is for, how long
   the project runs, and how you will comply with the attribution terms. The review is
   manual and a thin answer is what gets it delayed.
5. On approval, generate the token from the **Your Active Access** tab. An account may hold
   at most five tokens and each expires after a year.

**The trial lasts 14 days from approval, and that changes the plan.** The free
non-commercial trial is a fortnight, not an open-ended academic tier. Continued or
automated access is the paid Member / Custom Access plan. So the harvest must be ready to
run the day the token arrives rather than started then. It is: `harvest_lens.py` is written
and its parsing tested, so the whole Lens corpus can be pulled in one sitting and kept.

Once issued, write the token to `~/.lens_token` or set `LENS_API_TOKEN`, verify it with
`scripts/python/check_lens_token.py`, and never commit it.

**What to run.** `scripts/python/harvest_lens.py`, which reads the blocks straight out of
`queries/platform_lens_v1.txt` and writes one JSONL file per block and region into
`data/raw/lens/`, plus a manifest recording the query, the run date and the record count.
Run the patent search separately, never mixed into the scholarly counts.

**Two API constraints the script already handles.** Offset paging refuses to go past 10,000
records, so every corpus is scrolled with a cursor instead; and a `scroll_id` expires after
one minute, so the paging loop never pauses between pages. Maximum page size is 1,000.

**Field names, confirmed against the Scholar API reference:** `title`, `abstract`,
`author.affiliation.address.country_code`, `year_published`.

**Manual fallback.** If the token is refused or delayed, export CSV and BibTeX from the web
interface, same search and same day. The free tier caps the export size and the cap has
changed more than once, so read the number the platform shows rather than trusting any
figure written here. If the cap bites, segment by year, which is cleaner than segmenting by
subtopic because year slices cannot overlap.

## 3. Scopus — not available

**UNISUCRE has no Scopus or Web of Science subscription (AC, 2026-09-23).** Both are closed
as sources for this thesis. `queries/platform_scopus_v1.txt` and
`queries/platform_wos_v1.txt` stay in the repository so the study can be reproduced by
someone who does have access, and because a thesis that states its search strings for the
two conventional databases and explains why it could not run them is stronger than one that
does not mention them.

What replaces them is not nothing. OpenAlex and Lens disagree by a third on Latin American
counts, which is itself a triangulation result and a more interesting one than agreement
between two commercial indexes would have been. Semantic Scholar and Europe PMC contributed
4,070 abstracts that OpenAlex lacks, which is a form of coverage check on the same corpus.

### Archived: what Scopus would have needed

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

### Archived: what Web of Science would have needed

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

- ~~Request a Lens API token.~~ **Done 2026-09-23.** Token issued, subscription runs to
  2026-09-29, 179,860 records harvested.
- Whether to renew the Lens subscription past 2026-09-29, which would be needed only to
  re-harvest. The records are already on disk. — AC.
- ~~Scopus and Web of Science access.~~ **Closed 2026-09-23 (AC): there is none.** Not to
  be raised again.
- Should Spanish and Portuguese term variants be added for the regional slices? They matter
  more on Scopus and Lens than on Web of Science. — AC.

## References

To be collected in `refs/references.bib`.
