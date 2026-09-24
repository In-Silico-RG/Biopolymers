# Full texts

PDFs are not committed. This file records what is wanted and how to get it.

## Wanted

**Camposano et al. 2026, Population-aware Generative Modeling of Lignin Ensemble.**
ChemRxiv, posted 2026-09-02, `10.26434/chemrxiv.15008225/v1`.

The most relevant work in the entire generative slice to this group's lignin line. It
trains autoregressive molecular language models on 1.16 million lignin structures generated
with LigninGraphs, represented as canonical SMILES, then applies reinforcement learning that
rewards a *population* of generated molecules for reproducing ensemble statistics (monomer
fractions, linkage distributions, branching, number- and weight-average molecular weight,
polydispersity) rather than optimising each molecule alone. It then automates conversion to
simulation-ready systems with force-field topology and solvent packing.

Authors are at Linköping, in Zozoulenko's group. Same problem as
`../../Lignin_Project/Testing_Lignin_Structure_Generators/`, approached from the generative
side.

**AC holds this PDF (2026-09-24). Not a project task; do not raise it again.** What follows
is kept only to explain why an automated fetch will not work if anyone tries.

### Why an automated fetch fails

Unpaywall and OpenAlex both confirm it is open access and both give the same URL:
`https://chemrxiv.org/doi/pdf/10.26434/chemrxiv.15008225/v1`. That URL sits behind a
Cloudflare browser challenge, which returns an HTML interstitial to curl, to requests and to
the ChemRxiv public API alike (HTTP 403). There is no mirror: the preprint is three weeks
old, so Semantic Scholar has no record of it and no repository has picked it up.

The abstract is captured in `data/processed/validation/generative_read.md` and the full
reference in `refs/references.bib`, so the project record does not depend on the file.
