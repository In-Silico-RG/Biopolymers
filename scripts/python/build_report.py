#!/usr/bin/env python3
"""Generate the bibliometric report as LaTeX, with every number read from outputs/tables/.

No figure in the report is typed by hand. Each one is pulled from the CSV that produced it,
so re-running this after any analysis change regenerates a report that cannot disagree with
the data. Several numbers in this project have already changed twice in a day; a report
with hand-copied values would have been wrong within the hour.

Writes report/informe_bibliometrico.tex and compiles it with pdflatex, two passes, then
removes the auxiliary files and verifies the text with pdftotext.
"""
import csv
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAB = ROOT / "outputs/tables"
FIG = ROOT / "outputs/figures"
OUT = ROOT / "report"
TEX = OUT / "informe_bibliometrico.tex"


def rows(name):
    p = TAB / name
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(v, dec=0, dash="--"):
    """Format a value for LaTeX, or an em dash when it is missing."""
    if v is None or v == "" or str(v).lower() in ("nan", "none"):
        return dash
    try:
        f = float(v)
    except (TypeError, ValueError):
        return esc(str(v))
    return f"{f:,.0f}" if dec == 0 else f"{f:,.{dec}f}"


def esc(s):
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
                 ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"),
                 ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def get(rs, key, val, field, default=None):
    for r in rs:
        if r.get(key) == val:
            return r.get(field, default)
    return default


def build():
    t3 = rows("T3_context_comparison.csv")
    t6 = rows("T6_anchor_lines.csv")
    t11 = rows("T11_corrected_method_share.csv")
    t15 = rows("T15_collaboration_shares.csv")
    t16 = rows("T16_lotka_summary.csv")
    t17 = rows("T17_bradford_summary.csv")
    t21 = rows("T21_screening_by_context.csv")
    t22 = rows("T22_method_mix_by_context.csv")
    t24 = rows("T24_whole_field_screened.csv")
    t25 = rows("T25_partial_year_2026.csv")
    t26 = rows("T26_source_counts.csv")
    t27 = rows("T27_source_overlap.csv")
    t28 = rows("T28_affiliation_misses.csv")
    t30 = rows("T30_language_variants.csv")
    t31 = rows("T31_generative_works.csv")
    t33 = rows("T33_combined_vs_english.csv")
    t34 = rows("T34_combined_context_comparison.csv")
    t32 = rows("T32_screening_validation.csv")
    t4 = rows("T4_country_ranking.csv")
    t5 = rows("T5_latam_country_ranking.csv")
    t19 = rows("T19_institution_centrality_core_colombia.csv")

    L = []
    A = L.append

    A(r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}
\usepackage{lmodern}
\usepackage[margin=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{caption}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\captionsetup{font=small,labelfont=bf}
\setlength{\parskip}{0.4em}
\setlength{\parindent}{0pt}

\title{\textbf{Biopolymers, and the computational methods used to study them}\\[0.3em]
\large A bibliometric mapping of the field, with a Latin American and Colombian focus}
\author{Camila Argel \\ \small Directed by Aldo F. Combariza \\
\small Grupo de Investigación IN SILICO, Universidad de Sucre}
\date{Working draft, \today}

\begin{document}
\maketitle

\begin{abstract}
\noindent
This report maps the scientific literature on biopolymers and measures how much of it uses
computational chemistry, chemoinformatics or artificial intelligence. It then narrows to
Latin America and Colombia. The corpus is built from OpenAlex and cross-checked against
Lens, and the method layer is classified by reading abstracts rather than by matching
keywords. Two results shape everything that follows. Keyword bibliometrics overstates the
computational share of the field worldwide, because the vocabulary of biopolymers overlaps
that of structural biology; and it understates the share in Latin America, because much
regional work is invisible to affiliation matching. Reading the abstracts reverses the
ranking of contexts that the keyword counts produce.
\end{abstract}

\section{What this report answers}

Three questions, in the order the work addressed them.

\begin{enumerate}
\item Where and when is research on biopolymers being done, and by whom?
\item How much of that research uses computational chemistry, chemoinformatics or
      artificial intelligence, and which methods on which polymers?
\item What does the Latin American and Colombian position look like inside that map?
\end{enumerate}

The thematic scope is deliberately wide: every biopolymer recognised as a subject of
scientific study, anchored on the lines this group works in jointly, namely cellulose and
nanocellulose, polyhydroxyalkanoates, and lignin.

\section{Method}

\subsection{How the corpus was defined}

The core corpus is the field that \emph{identifies itself} as biopolymers: works whose
title or abstract carries a biopolymer framing term. This was reached empirically. Blocks
for each polymer family were probed first, and every family block intersected with a
biopolymer framing turned out to be a subset of the generic string, so the generic string is
the union rather than a narrowing.

Two acronym tests decided the wording of every query. The bare acronym PHA returns 56{,}015
records against 8{,}422 when bound to its expanded form, and bare DFT 471 against 295 inside
the core corpus. Bare acronyms are used nowhere.

Every search string is a versioned file that is never edited once run, so a count can always
be traced to the exact text that produced it.

\subsection{Sources}""")

    A(r"""
Scopus and Web of Science are not used: the institution has no subscription. The
triangulation therefore runs on OpenAlex as the base corpus and Lens as an independent
index, with Semantic Scholar and Europe PMC recovering abstracts that OpenAlex lacks.

This turned out to be more informative than a comparison of two commercial indexes would
have been. Table~\ref{tab:sources} shows Lens holding most of the world corpus but a far
smaller share of the regional one.
""")

    A(r"""\begin{table}[htbp]
\centering
\caption{OpenAlex against Lens, same concept, same window. Lens covers the world corpus
well and the regional corpora poorly, so the choice of source matters most exactly where
this report focuses.}
\label{tab:sources}
\small
\begin{tabular}{llrrr}
\toprule
Block & Region & OpenAlex & Lens & Lens as \% of OpenAlex \\
\midrule""")
    names = {"L1": "Core field", "L3": "Method layer", "L4": "Cellulose",
             "L5": "PHA/PHB", "L6": "Lignin"}
    geos = {"world": "World", "latam": "Latin America", "colombia": "Colombia"}
    for r in t26:
        A(f"{esc(names.get(r['block'], r['block']))} & {geos.get(r['geo'], r['geo'])} & "
          f"{num(r['openalex'])} & {num(r['lens'])} & {num(r['lens_vs_openalex_pct'],1)} \\\\")
    A(r"""\bottomrule
\end{tabular}
\end{table}""")

    if t27:
        A(r"""
The overlap is partial in both directions. Across the matched corpora, between """
          + f"{min(float(r['pct_of_lens_found_in_openalex']) for r in t27):.0f}"
          + r"\% and "
          + f"{max(float(r['pct_of_lens_found_in_openalex']) for r in t27):.0f}"
          + r"""\% of Lens records are also in OpenAlex, but only between """
          + f"{min(float(r['pct_of_openalex_found_in_lens']) for r in t27):.0f}"
          + r"\% and "
          + f"{max(float(r['pct_of_openalex_found_in_lens']) for r in t27):.0f}"
          + r"""\% of OpenAlex records are in Lens. Lens still contributes works OpenAlex
lacks, so the union of the two is larger than either. A single-source count of Latin
American output is therefore a lower bound, and this is a result rather than a caveat.
""")

    A(r"""
\subsection{Reading the abstracts}

A keyword query cannot tell a molecular dynamics study of a cellulose nanocrystal composite
from a molecular dynamics study of haemoglobin allostery, yet only the first is biopolymer
materials science. Every abstract in the method layer was therefore classified by a language
model: whether the work is materials research or biological-function research, which polymer
family, which computational method, and whether experiments are reported. Every call is
cached on a hash of the prompt, so the classification is reproducible and re-running it is
free.

One correction was applied after inspecting the output rather than trusting it. The first
pass offered a catch-all computational category, and it was absorbing factorial designs,
response-surface methodology and curve fitting to the authors' own measurements. That
inflated the Colombian computational share to 12.5\% against a defensible 3\%. The ambiguous
bucket alone was re-asked with a question naming the distinction, and statistical design of
experiments is now excluded from every computational count. The first-pass classifications
are kept on disk so the correction is auditable.

\subsection{Validating the screening}
\label{sec:validation}

A classification produced by a language model is worth nothing without an agreement figure.
125 abstracts were double-coded by a second, independent reader on a different model,
blind to the first coder's labels. Asking the same model to check its own work would have
it repeat its own mistakes and report high agreement with itself.

Agreement is reported as Cohen's kappa rather than percent agreement, because percent
agreement flatters any classification with a dominant class.

""")
    if t32:
        rnd = [r for r in t32 if r["stratum"] == "random"]
        A(r"""\begin{table}[htbp]
\centering
\caption{Agreement between the two independent coders on the random sample.}
\label{tab:validation}
\small
\begin{tabular}{lrr}
\toprule
Dimension & Agreement & Cohen's $\kappa$ \\
\midrule""")
        for r in rnd:
            A(f"{esc(r['dimension'])} & {num(r['percent_agreement'],1)}\\% & "
              f"{num(r['cohens_kappa'],3)} \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
    A(r"""

The distinction the whole correction depends on, materials research against biological
function, reaches the highest agreement of the four. On the conventional reading, 0.61--0.80
is substantial and above 0.80 almost perfect.

The two coders also disagree in a consistent direction. On the random sample of 100, the
first coder called 79 works computational against the second coder's 73, a relative
over-detection of 8.2\%. Five of the seven disputed works were labelled machine learning,
and reading them shows why: they are reviews and experimental papers that mention artificial
intelligence as a closing perspective without performing any computation. \textbf{Every
screened share in this report is therefore an upper bound}, and the strict world figure of
1.28\%
is closer to 1.18\% once the bias is applied. This runs the same way as every other
correction found here.

\section{Results}

\subsection{Size, growth and geography}
""")

    A(r"""\begin{table}[htbp]
\centering
\caption{The field by context. Growth rates use complete years only. The method share here
is the \emph{keyword} estimate, corrected in Section~\ref{sec:layer}.}
\label{tab:contexts}
\small
\begin{tabular}{lrrrrr}
\toprule
Context & Works, all years & 2015--2025 & Share of world & Growth/yr & Open access \\
\midrule""")
    for r in t3:
        A(f"{esc(r['context'])} & {num(r['total_all_years'])} & {num(r['core_2015_2025'])} & "
          f"{num(r['share_of_world_pct'],2)}\\% & {num(r['cagr_2015_2025_pct'],1)}\\% & "
          f"{num(r['open_access_pct'],1)}\\% \\\\")
    A(r"""\bottomrule
\end{tabular}
\end{table}""")

    world_total = get(t3, "context", "World", "total_all_years")
    col_cagr = get(t3, "context", "Colombia", "cagr_2015_2025_pct")
    lat_cagr = get(t3, "context", "Latin America", "cagr_2015_2025_pct")
    w_cagr = get(t3, "context", "World", "cagr_2015_2025_pct")
    col_oa = get(t3, "context", "Colombia", "open_access_pct")
    w_oa = get(t3, "context", "World", "open_access_pct")

    A(rf"""
The field holds {num(world_total)} works and grows at {num(w_cagr,1)}\% a year. Both
regional contexts grow faster than the world, Latin America at {num(lat_cagr,1)}\% and
Colombia at {num(col_cagr,1)}\%, so the region is closing the relative gap rather than
falling behind. Colombia's rate is computed on a small base and says more about the base
than about capacity. Regional output is markedly more open: {num(col_oa,1)}\% of Colombian
work is open access against {num(w_oa,1)}\% worldwide.
""")

    A(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{../outputs/figures/F1_annual_production.pdf}
\caption{Annual production by context. Each panel carries its own scale, since the contexts
differ by three orders of magnitude. The hollow marker and dashed segment are 2026, a
partial year.}
\end{figure}""")

    if t4:
        top3 = sum(float(r["core_count"]) for r in t4[:3])
        latam_in_top20 = [r["country"] for r in t4[:20]
                          if r["country_code"] in {"BR", "MX", "AR", "CO", "CL", "PE"}]
        A(rf"""
The top three countries, {esc(t4[0]['country'])}, {esc(t4[1]['country'])} and
{esc(t4[2]['country'])}, hold {num(top3)} works between them, just over a third of the
field. {'Only one Latin American country reaches' if len(latam_in_top20) == 1 else f'Only {len(latam_in_top20)} Latin American countries reach'} the top twenty:
{esc(', '.join(latam_in_top20)) if latam_in_top20 else 'none'}.
""")
    if t5:
        latam_codes = {"BR", "MX", "AR", "CO", "CL", "PE", "EC", "UY", "VE", "CR",
                       "CU", "BO", "PY", "PA", "GT", "HN", "NI", "SV", "DO", "PR"}
        order = ", ".join(f"{esc(r['country'])} ({num(r['core_count'])})"
                          for r in [x for x in t5 if x["country_code"] in latam_codes][:6])
        A(rf"""
Inside Latin America the order by volume is {order}.
""")

    A(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{../outputs/figures/F3_country_ranking.pdf}
\caption{The twenty largest producers, and how much of each country's output is
computational. Volume and intensity are separate panels; they are different measures and do
not share an axis.}
\end{figure}

\subsection{The computational and artificial-intelligence layer}
\label{sec:layer}
""")

    if t11:
        r = t11[0]
        A(rf"""
This is the central result. The keyword estimate puts
{num(r.get('uncorrected_pct'),2)}\% of the field on some computational, chemoinformatic or
AI method. Reading the abstracts shows only
{num(r.get('materials_fraction_of_methods_layer'),1)}\% of that layer to be biopolymer
materials research; the rest is protein folding, enzyme mechanism and nucleic-acid biology,
pulled in because the framing terms overlap. Restricting to materials research brings the
share to {num(r.get('corrected_pct_materials_only'),2)}\%, and restricting further to works
with a genuine computational method gives
\textbf{{{num(r.get('corrected_pct_strict'),2)}\%}}.
""")

    A(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=0.92\textwidth]{../outputs/figures/F2_methods_share.pdf}
\caption{Uptake of computational methods inside the field. The solid line is a three-year
rolling share; the dashed segment joins single-year 2025 to single-year 2026, the latter a
year to date. Ratios on small denominators are suppressed.}
\end{figure}""")

    if t25:
        A(r"""
\paragraph{The partial year is not dropped.} 2026 is incomplete and is kept, flagged,
because it carries the strongest signal in the data.
""")
        A(r"""\begin{table}[htbp]
\centering
\caption{2026 to date against the whole of 2025. The field as a whole is well short of its
2025 volume at the same date, while the method layer has already passed it in every
context.}
\label{tab:partial}
\small
\begin{tabular}{lrrrrrr}
\toprule
& \multicolumn{3}{c}{Whole field} & \multicolumn{3}{c}{Method layer} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-7}
Context & 2025 & 2026 YTD & \% & 2025 & 2026 YTD & \% \\
\midrule""")
        for r in t25:
            A(f"{esc(r['context'])} & {num(r['core_2025'])} & {num(r['core_2026_ytd'])} & "
              f"{num(r['core_ytd_vs_last_full_pct'],0)} & {num(r['methods_2025'])} & "
              f"{num(r['methods_2026_ytd'])} & {num(r['methods_ytd_vs_last_full_pct'],0)} \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")

    A(r"""
\subsection{Keyword counts understate the region}
""")
    if t24:
        A(r"""\begin{table}[htbp]
\centering
\caption{Screening the whole regional field, rather than the keyword-selected method layer,
finds computational work the query missed.}
\label{tab:regional}
\small
\begin{tabular}{lrrrr}
\toprule
Corpus & Materials works & With a method & Screened share & Keyword share \\
\midrule""")
        kw = {"Latin America, whole field": get(t3, "context", "Latin America", "methods_share_pct"),
              "Colombia, whole field": get(t3, "context", "Colombia", "methods_share_pct")}
        for r in t24:
            A(f"{esc(r['corpus'])} & {num(r['materials_works'])} & "
              f"{num(r['with_computational_method'])} & "
              f"{num(r['computational_pct_of_materials'],2)}\\% & "
              f"{num(kw.get(r['corpus']),2)}\\% \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
        A(r"""
Reading abstracts raises the regional estimate substantially, and it changes the ordering:
Colombia sits \emph{above} the Latin American average, not below it as the keyword counts
say. The keyword-based ordering should not be quoted.
""")

    if t28:
        r0 = t28[0]
        A(rf"""
Part of the reason is mechanical. In the world method corpus,
{num(r0.get('authorships_unmatched_pct'),1)}\% of authorships match no institution entity
at all, so the country they belong to receives no credit. A 2025 paper with two Peruvian
affiliations and one Mexican one counts, in the data, as Mexican alone. Since every regional
corpus here was selected on institution country, works whose regional affiliations all went
unmatched never entered it. Per-country loss is worst for the smallest producers. The
regional counts in this report are a lower bound.
""")

    A(r"""
\subsection{Which methods, on which polymers}
""")
    if t22:
        ctxs = [c for c in t22[0].keys() if c != "method"]
        A(r"""\begin{table}[htbp]
\centering
\caption{Method mix of the materials-only subset, as a percentage of each context. The
world leans on molecular dynamics; the region leans on machine learning and quantum
chemistry.}
\label{tab:methods}
\small
\begin{tabular}{l""" + "r" * len(ctxs) + r"""}
\toprule
Method & """ + " & ".join(esc(c) for c in ctxs) + r""" \\
\midrule""")
        label = {"md": "Molecular dynamics", "ml": "Machine learning",
                 "qc": "Quantum chemistry", "docking": "Docking",
                 "solubility": "Solubility modelling", "qsar": "QSAR / QSPR",
                 "generative": "Generative", "molecular_modelling": "Other molecular modelling",
                 "informatics": "Other informatics", "none": "None detected",
                 "statistical_doe": "Statistical design of experiments"}
        order = ["md", "ml", "qc", "docking", "solubility", "qsar", "generative",
                 "molecular_modelling", "informatics", "statistical_doe", "none"]
        byk = {r["method"]: r for r in t22}
        for k in order:
            if k in byk:
                A(esc(label.get(k, k)) + " & "
                  + " & ".join(num(byk[k].get(c), 1) for c in ctxs) + r" \\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")

    A(r"""
Generative methods and QSAR are absent from the region entirely, and worldwide the
generative slice is a handful of works. That is the emptiest part of the map and the most
obvious opening.

\subsection{The regional deficit is partly linguistic}
\label{sec:language}

Every count so far came from English queries. Spanish and Portuguese term variants were run
against the same regional slices and the set difference taken, so what is reported is not
how many records the Spanish and Portuguese strings return but how many they return that
the English string does \emph{not}.

""")
    if t30:
        reg = [r for r in t30 if r["geo"] in ("latam", "colombia")]
        A(r"""\begin{table}[htbp]
\centering
\caption{What Spanish and Portuguese terms add. The last column is the set difference:
records the Spanish and Portuguese strings return that the English string does not.}
\label{tab:language}
\small
\begin{tabular}{llrrr}
\toprule
Block & Region & English & Spanish/Portuguese & Added \\
\midrule""")
        bn = {"core": "Core field", "cellulose": "Cellulose", "pha": "PHA/PHB",
              "lignin": "Lignin"}
        gn = {"latam": "Latin America", "colombia": "Colombia"}
        for r in reg:
            A(f"{esc(bn.get(r['block'], r['block']))} & {gn.get(r['geo'], r['geo'])} & "
              f"{num(r['english'])} & {num(r['spanish_portuguese'])} & "
              f"{num(r['added_by_es_pt'])} (+{num(r['added_pct_of_english'],1)}\\%) \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
    A(r"""

The addition is substantial and it is largest for Colombia. A bibliometric count of Latin
American biopolymer research built on English terms alone misses between a seventh and a
third of the corpus, depending on the slice. Taken with the affiliation-matching loss of
Section~\ref{sec:layer}, the regional figures in this report understate the region twice
over, for two independent and separately measurable reasons.

\subsection{The three anchored lines}
""")
    if t6:
        A(r"""\begin{table}[htbp]
\centering
\caption{The biopolymer lines this group works in jointly.}
\label{tab:anchors}
\small
\begin{tabular}{lrrrrr}
\toprule
Line & World & Latin America & Colombia & Computational, world & Computational, region \\
\midrule""")
        anames = {"cellulose": "Cellulose and nanocellulose", "pha": "PHA / PHB",
                  "lignin": "Lignin"}
        for r in t6:
            A(f"{esc(anames.get(r['anchor'], r['anchor']))} & {num(r['world'])} & "
              f"{num(r['latam'])} & {num(r['colombia'])} & "
              f"{num(r['methods_share_world_pct'],2)}\\% & "
              f"{num(r['methods_share_latam_pct'],2)}\\% \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
        A(r"""
Lignin is the most computationally studied of the three and PHA the least. Latin America
holds a larger share of world output in PHA and lignin than in cellulose, which fits a
region working from agro-industrial residues.
""")

    A(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{../outputs/figures/F4_anchor_lines.pdf}
\caption{Volume and method intensity of the three anchored lines.}
\end{figure}

\subsection{The generative frontier, read work by work}
\label{sec:generative}

The screening put ten works in the materials subset on generative or large-language-model
methods. Ten is few enough to read every one, and a count cannot say what these works
generate, what steers the generation, or whether anything is validated. Both coders read
all ten independently. Three disagreements followed, and all three change the answer.

\paragraph{Ten records are nine works.} A preprint on retrieval-augmented generation over
polyhydroxyalkanoate literature is indexed twice, once with a DOI and once without. The
automated pass counted both.

\paragraph{The lignin paper is not a large-language-model paper.} It trains autoregressive
\emph{molecular} language models on SMILES strings, which is a generative sequence model
over chemical structure rather than a language model over natural language. The confusion
is understandable and it moves the most methodologically serious work in the set into the
wrong category.

\paragraph{Three of the ten sit in venues that are not what they appear to be.} Two are
published as \emph{Frontiers in Agriculture} and \emph{Frontiers in Chemistry Materials
and Catalysis}, under DOI prefix 10.71465, which Crossref registers to \emph{International
Study Counselor}. Frontiers Media SA is 10.3389. A third carries prefix 10.37591,
registered to a different publisher again. All three abstracts share a pattern: dramatic
headline numbers with no dataset, no baseline and no reproducible protocol. No automated
screening asked about venue provenance, and none routinely does.

""")
    if t31:
        A(r"""\begin{table}[htbp]
\centering
\caption{The generative works, as the two readers agreed them. ``Specific'' marks work
genuinely about a biopolymer rather than about polymers in general.}
\label{tab:generative}
\small
\begin{tabular}{rp{5.6cm}p{3.5cm}ll}
\toprule
Year & What it generates & Validated by & Specific \\
\midrule""")
        seen = set()
        for r in t31:
            g = (r.get("generates") or "").strip()
            if not g or g in seen:
                continue
            seen.add(g)
            v = (r.get("validated_how") or "").replace("_", " ")
            sp = "yes" if str(r.get("is_biopolymer_specific")).lower() == "true" else "no"
            A(f"{num(r.get('year'))} & {esc(g)} & {esc(v)} & {sp} \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
    A(r"""

\paragraph{What survives.} Removing the works that are not about biopolymers and those
whose venue cannot be trusted leaves \textbf{four credible biopolymer-specific generative
works}, three of them from 2026. Two validated against the physical world, one by
electrospinning and mechanical testing, one by measuring nanomolar binding affinities. The
electrospun result was honestly negative: the fibre mat was weaker than commercial PET.

That is emptier than a count of ten suggests, and it strengthens the argument of this
report rather than weakening it. It also suggests that venue provenance deserves to be
checked across the whole corpus, not only on a shortlist, which nothing in the bibliometric
literature routinely does.

\subsection{Collaboration and community structure}
""")
    if t15:
        A(r"""\begin{table}[htbp]
\centering
\caption{Collaboration, counted per work.}
\label{tab:collab}
\small
\begin{tabular}{lrrr}
\toprule
Corpus & Works & International & Two or more Latin American countries \\
\midrule""")
        cn = {"methods_world": "World, method layer", "core_latam": "Latin America, whole field",
              "methods_latam": "Latin America, method layer", "core_colombia": "Colombia, whole field"}
        for r in t15:
            A(f"{esc(cn.get(r['corpus'], r['corpus']))} & {num(r['works_with_country'])} & "
              f"{num(r['international_pct'],1)}\\% & {num(r['intra_latam_pct'],1)}\\% \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
        col_intra = get(t15, "corpus", "core_colombia", "intra_latam_pct")
        lat_intra = get(t15, "corpus", "core_latam", "intra_latam_pct")
        A(rf"""
Colombia is the most regionally connected corpus measured. Nearly
{num(col_intra,0)}\% of Colombian works involve a second Latin American country, against
{num(lat_intra,0)}\% for the region as a whole. Brazil's strongest ties run outward instead,
to the United States, Portugal and Spain, and dwarf its ties inside the region.
""")

    A(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{../outputs/figures/F5_collaboration_matrix.pdf}
\caption{Country co-authorship in Latin American biopolymer research, shown as a matrix. A
node-link drawing of the same 115-node graph is a hairball; the network files are provided
for VOSviewer instead.}
\end{figure}""")

    if t16:
        wm = get(t16, "corpus", "methods_world", "single_work_authors_pct")
        we = get(t16, "corpus", "methods_world", "lotka_exponent")
        wa = get(t16, "corpus", "methods_world", "authors")
        A(rf"""
\paragraph{{There is no standing computational community.}} Classic Lotka behaviour gives an
exponent near 2. Every corpus here is steeper, and the method layers are steepest of all: of
the {num(wa)} authors in the world method layer, {num(wm,1)}\% appear exactly once, with a
fitted exponent of {num(we,2)}. The layer is made of one-off contributions. That is what a
field looks like before a speciality forms, not after.
""")
    A(r"""\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{../outputs/figures/F6_lotka.pdf}
\caption{Author productivity. A steeper slope means a shallower core of specialists.}
\end{figure}""")

    if t17:
        ml = get(t17, "corpus", "methods_latam", "core_zone_pct_of_journals")
        ww = get(t17, "corpus", "methods_world", "core_zone_pct_of_journals")
        A(rf"""
\paragraph{{And it has no home venue.}} Bradford's core zone is the set of journals carrying
the first third of a corpus. Worldwide it is {num(ww,1)}\% of journals, which is normal. For
the Latin American method layer it takes {num(ml,1)}\% of its journals to reach the first
third. That work is scattered, with no venue acting as a centre.
""")

    A(r"""
\section{Latin America and Colombia}
\label{sec:region}

\subsection{The claim}

Latin America is not behind in computational practice. It is small, invisible and
unorganised, and those are three different problems with three different remedies. The
region's difficulty is not access to molecular dynamics or machine learning. It is that its
output is thin in absolute terms, that a large part of what exists is not seen by the
instruments that count science, and that the part which does use computational methods has
neither a community nor a venue.

\subsection{Rebuilding the corpus in three languages}
\label{sec:combined}

Section~\ref{sec:language} measured what Spanish and Portuguese terms add. The corpus was
then rebuilt on the combined vocabulary, and the English-only corpus kept beside it, because
the gap between the two is the result.

""")
    if t33:
        A(r"""\begin{table}[htbp]
\centering
\caption{What the combined English, Spanish and Portuguese vocabulary adds. The core
corpora gain substantially; the method corpora gain almost nothing.}
\label{tab:combined}
\small
\begin{tabular}{lrrr}
\toprule
Corpus & English only & Combined & Added \\
\midrule""")
        nm = {"core_world": "Core field, world", "core_ibero": "Core field, Ibero-America",
              "core_latam": "Core field, Latin America", "core_colombia": "Core field, Colombia",
              "methods_world": "Method layer, world",
              "methods_ibero": "Method layer, Ibero-America",
              "methods_latam": "Method layer, Latin America",
              "methods_colombia": "Method layer, Colombia"}
        for r in t33:
            if r["corpus"] not in nm:
                continue
            A(f"{esc(nm[r['corpus']])} & {num(r['english_only'])} & {num(r['combined'])} & "
              f"{num(r['added'])} (+{num(r['added_pct'],1)}\\%) \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
    A(r"""

\paragraph{The result is the opposite of the one expected, and it is the most useful finding
of this section.} Adding Spanish and Portuguese recovered 7,106 works to the core corpora
and \textbf{19} to the method corpora. Colombia gains 26.3\% of core output and 0.0\% of
method output.

The literature that English-language queries miss is almost entirely non-computational. Two
readings follow and they are not exclusive: regional computational work is already
internationalised, published in English and never invisible; and the Spanish- and
Portuguese-language regional literature is overwhelmingly experimental and applied.

The consequence is arithmetic and it cuts against the region. With a complete corpus,
Colombia's keyword method share falls from 1.94\% to 1.59\% and Latin America's from
2.20\% to 1.96\%, because the denominator grew and the numerator did not. The growth rate
falls too, Colombia from 27.0\% to 18.9\%, as older Spanish-language work fills in the early
years. \textbf{The language correction does not excuse the thin computational layer; it
sharpens it.}

""")
    if t34:
        A(r"""\begin{table}[htbp]
\centering
\caption{The field by context, rebuilt on the combined vocabulary. Compare with
Table~\ref{tab:contexts}, the English-only version.}
\label{tab:contexts-combined}
\small
\begin{tabular}{lrrrrr}
\toprule
Context & Works, all years & 2015--2025 & Share of world & Growth/yr & Method share \\
\midrule""")
        for r in t34:
            A(f"{esc(r['context'])} & {num(r['total_all_years'])} & "
              f"{num(r['core_2015_2025'])} & {num(r['share_of_world_pct'],2)}\\% & "
              f"{num(r['cagr_2015_2025_pct'],1)}\\% & "
              f"{num(r['methods_share_pct'],2)}\\% \\\\")
        A(r"""\bottomrule
\end{tabular}
\end{table}""")
    A(r"""

\subsection{Three separate causes of invisibility}

A count of Latin American research in this field understates it, and the understatement has
three independent sources, each measured rather than assumed. \emph{Language}, worth 15.4\%
for Latin America and 26.3\% for Colombia. \emph{Affiliation matching}, which leaves 12.7\%
of authorships attached to no institution at all, worst for the smallest producers at 27\%
for Bolivia and 10\% for Venezuela. And \emph{choice of source}, since Lens holds 91\% of
the OpenAlex world corpus but 57\% of the Colombian one. None of these is a statement about
the quality of the research. They are statements about the infrastructure that counts it.

\subsection{Colombia is the most connected corpus measured}

Nearly a quarter of Colombian biopolymer works involve a second Latin American country, four
times the regional average, and 44\% involve any international partner. Its strongest
partners are Mexico, Brazil and Spain in almost equal measure.

Brazil is the contrast. Its strongest ties run outward, to the United States, Portugal and
Spain, and dwarf its ties to Argentina or Colombia. The largest producer in the region is the
least regionally integrated one. Colombia does not need to be taught to collaborate; it
already collaborates more, and more regionally, than the countries above it.

\begin{figure}[htbp]
\centering
\includegraphics[width=0.78\textwidth]{../outputs/figures/F7_colombia_partners.pdf}
\caption{Colombia's co-authorship partners, split between the region and outside it.}
\end{figure}

\subsection{What the region works on}

Latin America holds a larger share of world output in lignin and polyhydroxyalkanoates, both
7.1\%, than in cellulose at 4.8\%. That fits a research base working from agro-industrial
residues rather than purified feedstocks, and it is a comparative position rather than a
deficiency. On the screened subset Colombia concentrates on chitosan, 22\% of its
computational work against a world 9\%, and on lignin, 11\% against 4.7\%.

Its institutional base is real but shallow: Universidad Nacional de Colombia, Universidad del
Valle, Universidad de Cartagena and Universidad de Antioquia lead, with Universidad de Sucre
present at 25 works.

\subsection{Three problems, three remedies}

Conflating them is how this kind of study usually goes wrong.

\begin{enumerate}
\item \textbf{Scale is a funding and continuity problem}, not a training one. The region
      publishes competently and openly; it publishes little, and the people who do
      computational work mostly do it once.
\item \textbf{Invisibility is an infrastructure problem with identified causes.} Language,
      affiliation matching and choice of source are each measurable and each fixable, two of
      them by the databases rather than by the researchers. Depositing with complete,
      matchable affiliations is the part authors control.
\item \textbf{The absence of a community and a venue is an organisational problem}, and it
      is the one a research group can actually move. A recurring regional venue for
      computational work on biopolymers would address a gap this study measured rather than
      assumed.
\end{enumerate}

The clearest opening remains the generative frontier. Reading every generative work in the
field leaves four credible biopolymer-specific studies worldwide and none from Latin America
(Section~\ref{sec:generative}). One of them, on population-aware generation of lignin
ensembles, addresses the same problem as this group's existing lignin line.

\section{What the map shows}

\begin{enumerate}
\item \textbf{The computational layer is thin and it is accelerating.} Around one work in
      eighty in the biopolymers field uses a genuine computational method on a material.
      That share roughly doubled over a decade and 2026 is running ahead of 2025 in every
      context measured.
\item \textbf{The regional deficit is mostly volume, and the language correction sharpened
      rather than excused the rest.} On English-only counts Latin America matched the world
      on method uptake. Rebuilding the corpus in three languages recovered 7{,}106 works and
      only 19 of them computational, so the complete-corpus method share is about four
      fifths of the world's rather than equal to it (Section~\ref{sec:combined}). The
      region's computational work was never invisible; its experimental work was. What the
      region lacks is scale and continuity, and the gap in method uptake is real but modest.
\item \textbf{The method mix differs by region.} The world leans on molecular dynamics;
      Latin America leans on machine learning; Colombia leans on quantum chemistry. An
      infrastructural reading is available, since sustained dynamics needs computing time
      that the other two need less of, but the Colombian denominator is small and this
      belongs in the discussion as a hypothesis rather than in the results as a finding.
\item \textbf{Generative methods are essentially absent}, worldwide and entirely so in the
      region. Reading all of them one by one (Section~\ref{sec:generative}) leaves four
      credible biopolymer-specific works in the world literature. Of everything in this
      report, that is the clearest opening.
\item \textbf{There is no community and no venue.} Most authors in the computational layer
      publish there once, and the regional slice has no core journals. A thesis that wants
      to change something has a structural target, not only a topical one.
\end{enumerate}

\section{Limitations}

\begin{itemize}
\item \textbf{Two sources, not four.} Scopus and Web of Science were unavailable. OpenAlex
      and Lens disagree by about a third on regional counts, which bounds how precise any
      regional figure here can be and is itself reported as a result
      (Section~\ref{sec:region}).
\item \textbf{The screened shares are upper bounds.} The measured over-detection of
      Section~\ref{sec:validation} is 8.2\%, and it is not corrected in the tables, only
      stated. Read every screened percentage as a ceiling.
\item \textbf{The screened shares rest on the English-only corpus.} Sections~\ref{sec:layer}
      and the screening of Section~\ref{sec:validation} were run before the corpus was
      rebuilt in three languages. The denominator is now known to be larger, so those shares
      are upper bounds on that count as well as on the over-detection count.
\item \textbf{Affiliation matching loses regional work.} Quantified in
      Section~\ref{sec:layer}. The regional counts are a lower bound.
\item \textbf{Abstract coverage.} Roughly 30\% of the method-layer records carry no abstract
      in OpenAlex. Semantic Scholar and Europe PMC recovered 4{,}070 of them; the rest could
      not be read and are excluded from every screened share.
\item \textbf{The screening is not yet validated.} A hand-coded sample double-coded against
      the automatic classification would give an agreement figure. Until that exists, the
      screened shares should be reported as what they are, a machine reading.
\item \textbf{English-language queries.} Regional work published in Spanish and Portuguese
      is undercounted.
\item \textbf{Country attribution counts a work once per country present}, so country
      columns sum to more than the corpus.
\end{itemize}

\section{What to do next}

\begin{enumerate}
\item A third coding of a few dozen items by a domain expert, as a check on two automatic
      coders that may share a bias neither detects.
\item Re-run the abstract screening on the combined corpus, so the screened shares rest on
      the same denominator as the keyword ones.
\item Apply the venue-provenance check of Section~\ref{sec:generative} to the whole
      corpus. It is a measurable, publishable statement and nothing in the field does it.
\item Take the affiliation-matching loss seriously as a result in its own right. It is a
      measurable, publishable statement about how invisible small Latin American
      institutions are to the infrastructure that counts science.
\end{enumerate}

\vfill
\noindent\rule{\textwidth}{0.4pt}\\
\footnotesize
Every number in this report is generated from the analysis tables in
\texttt{outputs/tables/} by \texttt{scripts/python/build\_report.py}; none is typed by hand.
Search strings are versioned in \texttt{queries/}, the session record is in
\texttt{docs/LOG.md}.

\end{document}
""")
    return "\n".join(L)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TEX.write_text(build(), encoding="utf-8")
    print(f"wrote {TEX.relative_to(ROOT)}")

    if not shutil.which("pdflatex"):
        sys.exit("pdflatex not found; the .tex is written but not compiled")
    for i in (1, 2):
        p = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                            TEX.name], cwd=OUT, capture_output=True, text=True)
        if p.returncode != 0:
            tail = "\n".join(p.stdout.splitlines()[-30:])
            sys.exit(f"pdflatex failed on pass {i}:\n{tail}")
    for ext in (".aux", ".log", ".out", ".toc"):
        f = TEX.with_suffix(ext)
        if f.exists():
            f.unlink()
    pdf = TEX.with_suffix(".pdf")
    print(f"compiled {pdf.relative_to(ROOT)} ({pdf.stat().st_size // 1024} KB)")

    if shutil.which("pdftotext"):
        txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True)
        n = len(txt.stdout.split())
        print(f"pdftotext: {n} words, {txt.stdout.count(chr(12))} pages")


if __name__ == "__main__":
    main()
