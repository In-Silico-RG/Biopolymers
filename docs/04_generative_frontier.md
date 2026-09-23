# 04 — The generative frontier, read work by work

*2026-09-23. Phase 2 of `00_plan.md`, the part the counts pointed at.*

**Objective.** The screening found ten works in the materials subset using generative or
large-language-model methods. Ten is few enough to read every one. A count cannot say what
these works generate, what steers the generation, or whether anything is validated, and
those are the questions that decide whether this is a frontier or a rumour.

**Status.** closed 2026-09-23. All ten read by two independent readers.

---

## 1. Why two readers

DeepSeek did the screening that produced this shortlist, so asking DeepSeek alone to
characterise the shortlist would have it grading its own selection. A second reader on a
different model, Claude, read the same abstracts without seeing the first reader's
extraction. The disagreements below are the useful part: each one is a place where a single
automated pass would have produced a confident wrong answer.

DeepSeek's structured extraction is `outputs/tables/T31_generative_works.csv`. The abstracts
are `data/processed/validation/generative_read.md`.

## 2. Three disagreements, all material

**Ten records are nine works.** Items 3 and 4 are the same arXiv preprint on
retrieval-augmented generation over polyhydroxyalkanoate literature, indexed twice, once
with a DOI and once without. The automated pass counted both. Every "ten generative works"
figure in `02_networks_and_screening.md` should read nine.

**The lignin paper is not a large-language-model paper.** DeepSeek assigned family `llm` to
*Population-aware Generative Modeling of Lignin Ensemble*. It trains autoregressive
*molecular* language models on SMILES strings, which is a generative sequence model over
chemical structure, not a large language model over natural language. The confusion is
understandable and it is wrong, and it matters because it moves the single most
methodologically serious work in this set into the wrong category. Corrected family:
`generative_model`.

**Two of the ten are published in venues impersonating Frontiers.** Items 7 and 8 appear as
*Frontiers in Agriculture* and *Frontiers in Chemistry Materials and Catalysis*. Their DOI
prefix is `10.71465`, registered at Crossref to **International Study Counselor**. Frontiers
Media SA is `10.3389`. A third, item 2, carries prefix `10.37591`, registered to *Consortium
eLearning Network Pvt Ltd*. All three abstracts share a pattern: dramatic headline numbers
with no dataset, no baseline and no reproducible protocol, such as "1000 times faster" and
"reduced permeability by 45\%". No automated screening asked about venue provenance, and it
should have.

## 3. What the nine works actually are

| # | Work | What it generates | Validated | Biopolymer-specific |
|---|---|---|---|---|
| 1 | LLM-assisted design of electrospun bioplastics | polymer formulations, from RAG over 4,022 papers | experiment | yes |
| 2 | GenAI inverse design of biodegradable polymers | polymer structures, diffusion + graph attention | held-out data | yes, venue doubtful |
| 3 | RAG expert system on PHA literature | answers grounded in 1,000+ PHA papers | expert review | yes |
| 4 | Extending generative ML for sustainable polymer design | 60,000 candidates from a VAE on PI1M | held-out data | no, synthetic only |
| 5 | Population-aware generative modeling of lignin | polydisperse lignin ensembles, simulation-ready | simulation | yes |
| 6 | Inverse design of food packaging, GANs | polymer compositions | none stated | yes, venue doubtful |
| 7 | Generative inverse design of intelligent packaging | compositions and microstructures | none stated | no, venue doubtful |
| 8 | polyGen, atomic-level polymer structure generation | 3D conformations from repeat-unit chemistry | held-out data | no, synthetic polymers |
| 9 | Computational generation of functionalised nucleic acid polymers | HFNAP sequences from a conditional VAE | experiment, nanomolar binders | yes |

## 4. What survives

Strip the works that are not about biopolymers and those whose venue cannot be trusted, and
the credible biopolymer-specific generative literature is **four works**: the electrospun
bioplastic study, the PHA retrieval-augmented expert system, the lignin ensemble generator,
and the nucleic-acid polymer thesis. Three of the four appeared in 2026.

That is emptier than the count of ten suggested, and it strengthens rather than weakens the
argument of this thesis. Two of the four validated against the physical world, one by
electrospinning and mechanical testing, one by measuring nanomolar binding affinities. The
electrospun result was honestly negative: the fibre mat was weaker than commercial PET.

## 5. The one that matters for this group

*Population-aware Generative Modeling of Lignin Ensemble* is the most relevant work in the
entire generative slice to the lines this group already runs. It trains an autoregressive
molecular language model on 1.16 million lignin structures produced with **LigninGraphs**,
then uses reinforcement learning that rewards a *population* of generated molecules for
reproducing ensemble statistics, namely monomer fractions, linkage distributions, branching,
number- and weight-average molecular weight and polydispersity, rather than optimising each
molecule alone. It then converts the ensemble into simulation-ready systems with force-field
topology and solvent packing.

This is adjacent to the lignin structure-generator work in `../Lignin_Project/`, on the same
problem of building realistic heterogeneous lignin for molecular dynamics, approached from
the generative side. It is a preprint on ChemRxiv with no citations yet.

## Decisions

- The generative count is nine distinct works, not ten; items 3 and 4 are one preprint
  indexed twice (2026-09-23).
- Venue provenance is checked by DOI prefix against Crossref for any work the thesis quotes
  individually. Three of the ten failed that check (2026-09-23).
- Family `llm` is reserved for large language models over natural language. Generative
  sequence models over SMILES are `generative_model` (2026-09-23).

## Open questions

- Should the venue check be applied to the whole corpus rather than to this shortlist? It
  would be a result in its own right, and nothing in the bibliometric literature routinely
  does it. — AC.

## References

DOI prefix ownership checked against the Crossref prefix API, 2026-09-23.
