# 05 — Validating the screening against an independent second coder

*2026-09-23. Validates the classification underlying `02_networks_and_screening.md`.*

**Objective.** Every headline number in this project rests on a language model reading
abstracts. Without an agreement measure against an independent coder, a referee is right to
distrust them. This document supplies that measure.

**Status.** closed 2026-09-23. 125 abstracts double-coded. Agreement is substantial to
almost perfect on every dimension, and a directional bias was found and quantified.

---

## 1. Design

**The second coder cannot be the same model.** Asking DeepSeek to check its own labels
would have it repeat its own mistakes and report high agreement with itself. Claude coded
the same abstracts as a second, independent reader, on a different model.

**The coding was blind.** `make_validation_sample.py` writes two files: a coding sheet with
only the title and abstract of each item, and a key with the DeepSeek labels. The key was
not read until the coding was submitted. Items from the two strata were shuffled together
so the stratum could not be inferred from position.

**Two strata.** A simple random sample of 100 readable works, which gives an honest figure
for the mix the corpus actually has; and 25 works drawn deliberately from thin categories
(generative, QSAR, solubility, statistical design of experiments, docking), which a random
draw would barely touch. The random sample is the headline. The rare stratum is reported
separately and never pooled into it.

**Agreement is Cohen's kappa, not percent agreement.** Percent agreement flatters any
classification with one dominant class: if 80% of a corpus carries one label, a coder who
always guessed that label scores 80% and knows nothing. Kappa subtracts the agreement
expected by chance.

## 2. Results

Random sample, n = 100:

| Dimension | Agreement | Cohen's kappa |
|---|---|---|
| Materials research vs biological function | 94.0% | **0.878** |
| Computational at all, yes or no | 92.0% | **0.782** |
| Method family | 88.0% | **0.816** |
| Polymer family | 80.0% | **0.767** |

Rare-category sample, n = 25:

| Dimension | Agreement | Cohen's kappa |
|---|---|---|
| Materials research vs biological function | 88.0% | 0.762 |
| Computational at all | 100.0% | not defined, both coders agreed on every item |
| Method family | 92.0% | 0.844 |
| Polymer family | 80.0% | 0.765 |

On the conventional reading of kappa, 0.61–0.80 is substantial and above 0.80 almost
perfect. **The separation that matters most for this thesis, materials research against
biological function, reaches 0.878.** That is the distinction the whole correction in
`02_networks_and_screening.md` section 3.2 depends on, and it is the strongest of the four.

Polymer family is the weakest at 0.767, which is expected: it has the most categories and
the most genuine ambiguity, since a work on a chitosan–hydroxyapatite scaffold can
reasonably be filed under chitosan or under "other".

## 3. A directional bias, quantified

Agreement is not the whole story. The two coders also disagree in a consistent direction.

| | Works called computational, of 100 |
|---|---|
| DeepSeek | 79 |
| Claude | 73 |

Seven works were called computational by DeepSeek alone and one by Claude alone, a net
**+8.2% relative over-detection by DeepSeek**. Five of the seven were labelled `ml`, and
reading them shows why: they are reviews and experimental papers that mention artificial
intelligence or machine learning as an outlook or a future perspective without performing
any computation. Examples include a carrageenan composites review whose AI content is a
closing paragraph, and an experimental study of a pumpkin-oil-cake coating on grapes.

The corresponding bias on the materials-versus-biological split is smaller, +3.6%.

**Direction of the correction.** The strict world method share of 1.28% reported in the
report is therefore an upper bound. Scaled by the measured over-detection it is closer to
**1.18%**. This runs the same way as every other correction found in this project: the
computational layer of the biopolymers field is thinner than a naive count suggests, not
thicker.

## 4. What this means for the thesis

The screening is defensible. It can be described in the methods section as a machine
classification validated against an independent second coder at kappa 0.88 on the primary
distinction, with a measured and stated over-detection bias of 8% on the computational
label. That is a stronger methodological position than most bibliometric studies of this
kind occupy, and it is stronger than a hand-coded sample by one person would have been,
because a single human coder produces no agreement figure at all.

Its limits should be stated as plainly, and stated as limits rather than as pending work.
Agreement was measured on the works that carry a readable abstract, so it says nothing about
the 20% that do not. And two language models can share a bias that neither detects, so kappa
between two automatic coders is not the same as kappa against a domain expert. No third
human coding will be done (AC, 2026-09-24), so this belongs in the limitations section of
the thesis as a stated boundary of the method, not as an outstanding task.

## Decisions

- The second coder is a different model, never the same one that produced the labels
  (2026-09-23).
- Agreement is reported as Cohen's kappa, with percent agreement alongside it but never
  alone (2026-09-23).
- The rare-category stratum is reported separately and never pooled into the headline
  figure (2026-09-23).
- The measured +8.2% over-detection is stated wherever the screened shares are quoted, and
  the strict world share is given as 1.28% with a bias-adjusted 1.18% (2026-09-23).

## Open questions

None. A third human coding was considered and declined (AC, 2026-09-24); the resulting
limitation is stated in section 4 rather than carried as pending work.

## References

Sample, codes and disagreements: `data/processed/validation/`. Scores:
`outputs/tables/T32_screening_validation.csv`.
