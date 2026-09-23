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

### Why it is not here

Unpaywall and OpenAlex both confirm it is open access and both give the same URL:
`https://chemrxiv.org/doi/pdf/10.26434/chemrxiv.15008225/v1`. That URL sits behind a
Cloudflare browser challenge, which returns an HTML interstitial to curl, to requests and to
the ChemRxiv public API alike (HTTP 403). There is no mirror: the preprint is three weeks
old, so Semantic Scholar has no record of it and no repository has picked it up.

### How to get it

Open the URL in a browser and save the PDF here, or from this session:

```
! xdg-open https://chemrxiv.org/doi/full/10.26434/chemrxiv.15008225/v1
```

Name it `2026_Camposano_Population-aware_Generative_Modeling_of_Lignin_Ensemble.pdf`.
The abstract is already captured in `data/processed/validation/generative_read.md`.
