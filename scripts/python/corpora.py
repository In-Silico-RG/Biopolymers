"""Corpus definitions, read from the frozen files in queries/.

Nothing here restates a search string. A string lives in exactly one place, its versioned
file, so a result can always be traced back to the text that produced it.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QDIR = ROOT / "queries"


# Words that can only come from a header line. A malformed comment that loses its "#"
# would otherwise be concatenated into the search string and silently change every count,
# which is exactly what happened on 2026-09-23 and is why this guard exists.
FORBIDDEN = ("Count:", "Run:", "Source:", "Rationale:", "Field:", "Phase ")


def load(name: str) -> str:
    """Return the search string of a frozen query file, comments stripped.

    Raises if the result looks like it swallowed a header line.
    """
    lines = (QDIR / name).read_text(encoding="utf-8").splitlines()
    body = [l for l in lines if l.strip() and not l.lstrip().startswith("#")]
    s = " ".join(body).strip()
    if not s:
        raise ValueError(f"{name}: no search string found")
    for bad in FORBIDDEN:
        if bad in s:
            raise ValueError(
                f"{name}: header text {bad!r} leaked into the search string. "
                "A comment line probably lost its leading '#'."
            )
    return s


CORE = load("p1_core_biopolymer_field_v1.txt")
METHODS = load("p2_computational_ai_v1.txt")
ANCHORS = {
    "cellulose": load("p1_anchor_cellulose_v1.txt"),
    "pha": load("p1_anchor_pha_v1.txt"),
    "lignin": load("p1_anchor_lignin_v1.txt"),
}

LATAM = "ar|bo|br|cl|co|cr|cu|do|ec|gt|hn|mx|ni|pa|pe|pr|py|sv|uy|ve"
IBERO = "ar|bo|br|cl|co|cr|cu|do|ec|es|gt|hn|mx|ni|pa|pe|pr|pt|py|sv|uy|ve"
COL = "co"


def paren(s: str) -> str:
    return s if s.startswith("(") else f"({s})"


def corpora():
    """The corpora analysed, as {name: (search_string, extra_filter_or_None)}."""
    core, meth = paren(CORE), paren(METHODS)
    c = {
        "core_world": (core, None),
        "core_latam": (core, f"institutions.country_code:{LATAM}"),
        "core_ibero": (core, f"institutions.country_code:{IBERO}"),
        "core_colombia": (core, f"institutions.country_code:{COL}"),
        "methods_world": (f"{core} AND {meth}", None),
        "methods_latam": (f"{core} AND {meth}", f"institutions.country_code:{LATAM}"),
        "methods_ibero": (f"{core} AND {meth}", f"institutions.country_code:{IBERO}"),
        "methods_colombia": (f"{core} AND {meth}", f"institutions.country_code:{COL}"),
    }
    for name, s in ANCHORS.items():
        a = paren(s)
        c[f"anchor_{name}_world"] = (a, None)
        c[f"anchor_{name}_latam"] = (a, f"institutions.country_code:{LATAM}")
        c[f"anchor_{name}_colombia"] = (a, f"institutions.country_code:{COL}")
        c[f"anchor_{name}_methods_world"] = (f"{a} AND {meth}", None)
        c[f"anchor_{name}_methods_latam"] = (f"{a} AND {meth}", f"institutions.country_code:{LATAM}")
    return c
