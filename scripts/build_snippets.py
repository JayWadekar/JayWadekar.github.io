#!/usr/bin/env python3
"""Regenerate the auto-updating parts of index.html from NASA ADS.

Produces two HTML fragments, written to scripts/out/:

  collaborators.html  frequent co-authors, ranked by shared-paper count
  topics.html         research topics, weighted by how often they appear

Both are plain <ul> markup meant to be pasted between the marker comments in
index.html.  Nothing here runs in the browser: the site stays static HTML with
no JavaScript, and re-running this script is the only way the lists change.

Usage:
    ADS_DEV_KEY=$(cat ~/.ads/dev_key) python3 scripts/build_snippets.py

The token is read from $ADS_DEV_KEY, falling back to ~/.ads/dev_key.  It is
never written to disk here and never printed.
"""

import html
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

# Public ADS library holding the first/second-author papers.
LIBRARY_ID = "iyG0RvT-RGyNet9YH6AegQ"

API = "https://api.adsabs.harvard.edu/v1"

# Wadekar's own name forms, excluded from the co-author counts.
SELF = {"wadekar, d", "wadekar, digvijay", "wadekar, jay"}

# Collaborators below this many shared papers are dropped from the list.
MIN_SHARED = 3

# People listed by hand elsewhere on the page — current group members and past
# mentees. Skipped here so nobody appears in two sections.
GROUP = {
    "islam, t",             # current group
    "ho-yeuk cheung, m",    # past mentees, from the CV's Mentoring section
    "thiele, l",
    "zhou, z",
}

# Topic terms are counted across titles, abstracts and ADS keywords.  Only
# multi-word phrases are counted: single words like "model" or "data" carry
# almost no information about what the papers are actually about.
TOPIC_PHRASES = [
    "gravitational wave", "black hole", "neutron star", "binary black hole",
    "compact object", "large-scale structure", "power spectrum",
    "covariance matrix", "galaxy cluster", "dark matter", "dwarf galaxy",
    "machine learning", "neural network", "symbolic regression",
    "large language model", "parameter estimation", "population inference",
    "higher harmonics", "effective spin", "primordial black hole",
    "galaxy survey", "redshift space", "halo occupation", "baryonic feedback",
    "sunyaev-zel'dovich", "intracluster medium", "cosmological parameter",
    "matched filter", "search pipeline", "waveform model", "axion",
    "millicharged", "21 cm", "star formation", "gravitational lensing",
    "effective field theory", "bispectrum", "mass function", "tidal disruption",
    "supermassive black hole", "stellar mass", "galaxy formation",
    "interpretable machine learning", "simulation-based inference",
]

# ADS reports the affiliation a co-author had *when the paper was published*,
# which goes stale as people move. Anything listed here wins over ADS.
OVERRIDE_AFF = {
    "islam, t": "UT Austin",
    "mehta, a": "CMI",
}

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "out"


def token():
    tok = os.environ.get("ADS_DEV_KEY", "").strip()
    if tok:
        return tok
    path = pathlib.Path.home() / ".ads" / "dev_key"
    if path.exists():
        return path.read_text().strip()
    sys.exit("No ADS token. Set $ADS_DEV_KEY or create ~/.ads/dev_key.")


def get(url, tok, data=None, content_type=None):
    req = urllib.request.Request(url, data=data)
    req.add_header("Authorization", f"Bearer {tok}")
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ADS {e.code} on {url}: {e.read().decode()[:400]}")


def fetch_records(tok):
    """Every paper in the library, with authors, affiliations and abstract."""
    lib = get(f"{API}/biblib/libraries/{LIBRARY_ID}?rows=500", tok)
    bibcodes = lib["documents"]

    fields = "bibcode,title,author,aff,abstract,keyword,year"
    body = ("bibcode\n" + "\n".join(bibcodes)).encode()
    url = (f"{API}/search/bigquery?q=*:*&fl={fields}"
           f"&rows={len(bibcodes)}&sort=date+desc")
    res = get(url, tok, data=body, content_type="big-query/csv")
    return res["response"]["docs"]


def norm(name):
    """'Zaldarriaga, Matias' -> 'zaldarriaga, m' so initials and full first
    names collapse onto one person."""
    name = name.strip().lower()
    if "," in name:
        last, first = name.split(",", 1)
        first = first.strip().strip(".")
        return f"{last.strip()}, {first[:1]}" if first else last.strip()
    return name


def collaborators(docs):
    counts, display, affs = {}, {}, {}
    for d in docs:
        authors = d.get("author") or []
        affiliations = d.get("aff") or []
        for i, a in enumerate(authors):
            key = norm(a)
            if key in SELF or key in GROUP:
                continue
            counts[key] = counts.get(key, 0) + 1
            # Keep the longest name form seen; it is usually the fullest.
            if len(a) > len(display.get(key, "")):
                display[key] = a.strip()
            if i < len(affiliations):
                aff = affiliations[i]
                if aff and aff != "-":
                    affs.setdefault(key, []).append(aff)
    rows = [(display[k], counts[k], OVERRIDE_AFF.get(k) or short_aff(affs.get(k, [])))
            for k in counts if counts[k] >= MIN_SHARED]
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows


def short_aff(affiliations):
    """ADS affiliation strings are long and inconsistent. Take the most common
    one and reduce it to a recognisable institution name."""
    if not affiliations:
        return ""
    best = max(set(affiliations), key=affiliations.count)
    known = [
        ("Institute for Advanced Study", "IAS"),
        ("Weizmann", "Weizmann Institute"),
        ("Chennai Mathematical", "CMI"),
        ("Texas at Austin", "UT Austin"),
        ("Santa Barbara", "UC Santa Barbara"),
        ("Flatiron", "Flatiron Institute"),
        ("New York University", "NYU"),
        ("Johns Hopkins", "Johns Hopkins"),
        ("Princeton", "Princeton"),
        ("Perimeter", "Perimeter Institute"),
        ("Harvard", "Harvard"),
        ("Caltech", "Caltech"),
        ("California Institute of Technology", "Caltech"),
        ("Walter Burke", "Caltech"),   # the Walter Burke Institute is at Caltech
        ("Cambridge", "Cambridge"),
        ("Max Planck", "Max Planck"),
        ("Tata Institute", "TIFR"),
    ]
    for needle, label in known:
        if needle.lower() in best.lower():
            return label
    # Otherwise use the first comma-separated clause that looks institutional.
    for part in best.split(","):
        part = part.strip()
        if any(w in part for w in ("University", "Institute", "Observatory",
                                   "College", "Laborator", "Center", "Centre")):
            return part
    return ""


def topics(docs):
    counts = {}
    for d in docs:
        blob = " ".join([
            " ".join(d.get("title") or []),
            " ".join(d.get("abstract") and [d["abstract"]] or []),
            " ".join(d.get("keyword") or []),
        ]).lower()
        blob = re.sub(r"\s+", " ", blob)
        for phrase in TOPIC_PHRASES:
            if phrase in blob:
                counts[phrase] = counts.get(phrase, 0) + 1
    rows = [(p, n) for p, n in counts.items() if n >= 2]
    rows.sort(key=lambda r: (-r[1], r[0]))
    return rows


def display_name(name):
    """ADS stores 'Last, First M.'; a web page wants 'First M. Last'."""
    if "," in name:
        last, first = name.split(",", 1)
        return f"{first.strip()} {last.strip()}".strip()
    return name


# Phrases whose capitalisation is not plain title case.
TOPIC_LABELS = {
    "21 cm": "21 cm",
    "sunyaev-zel'dovich": "Sunyaev-Zel'dovich",
    "large-scale structure": "Large-scale structure",
    "simulation-based inference": "Simulation-based inference",
}


def title_case(phrase):
    if phrase in TOPIC_LABELS:
        return TOPIC_LABELS[phrase]
    # Sentence case, not title case: "Binary black hole", not "Binary Black
    # Hole". Reads as prose rather than as a headline.
    return phrase[:1].upper() + phrase[1:]


def write_collaborators(rows):
    # two-col matches how the fragment is pasted into index.html; without it a
    # regeneration would silently drop the list back to one column.
    out = ['<ul class="people two-col">']
    for name, n, aff in rows:
        meta = f"{aff} &middot; " if aff else ""
        out.append(
            f'    <li><span>'
            f'<span class="person-name">{html.escape(display_name(name))}</span>'
            f'<span class="meta">{meta}{n} papers together</span>'
            f'</span></li>'
        )
    out.append("</ul>")
    (OUT / "collaborators.html").write_text("\n".join(out) + "\n")
    return len(rows)


def write_topics(rows):
    if not rows:
        return 0
    hi = rows[0][1]
    lo = rows[-1][1]
    span = max(hi - lo, 1)
    out = ['<ul class="topics">']
    for phrase, n in sorted(rows, key=lambda r: r[0]):
        w = round((n - lo) / span, 3)
        out.append(f'    <li style="--w:{w}">{html.escape(title_case(phrase))}</li>')
    out.append("</ul>")
    (OUT / "topics.html").write_text("\n".join(out) + "\n")
    return len(rows)


def main():
    OUT.mkdir(exist_ok=True)
    docs = fetch_records(token())
    print(f"{len(docs)} papers from ADS library {LIBRARY_ID}")

    rows = collaborators(docs)
    print(f"{write_collaborators(rows)} collaborators with >= {MIN_SHARED} shared papers")
    for name, n, aff in rows[:25]:
        print(f"  {n:3d}  {name}  [{aff}]")

    trows = topics(docs)
    print(f"{write_topics(trows)} topics")
    for phrase, n in trows[:30]:
        print(f"  {n:3d}  {phrase}")


if __name__ == "__main__":
    main()
