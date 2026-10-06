#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Recompute the corpus statistics and derived tables of the review from the released data.

Usage:
    python scripts/reproduce.py              # run every check, print a report
    python scripts/reproduce.py --write OUT  # also write the regenerated tables to OUT/

Every check compares a value recomputed from data/ with the value reported in the
manuscript or stored in results/. The script exits with status 1 if any check fails.
Only the Python standard library is used (Python 3.8 or later).

Titles are matched after Unicode NFKC normalization, lower-casing, and removal of
every character that is not a letter or a digit (see norm()).
"""

import argparse
import collections
import csv
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RESULTS = os.path.join(ROOT, "results")

DIMS = ["behavioral", "safety", "temporal", "regulatory", "multiagent"]
DIM_HEADER = {"behavioral": "Behavioral", "safety": "Safety", "temporal": "Temporal",
              "regulatory": "Regulatory", "multiagent": "Multi-agent"}
FAMILIES = ["Benchmarks", "Runtime Monitors", "CPS Validation", "Assurance Cases",
            "MLOps/Drift", "Reg Guidance"]
SUBTYPES = ["functional_safety", "adversarial_security", "both", "uncertain"]
SOURCE_LISTS = {"ACM": "papers_acm.csv", "arXiv": "papers_arxiv_merged.csv",
                "IEEE": "papers_ieee.csv", "Scopus": "papers_scopus.csv",
                "SemanticScholar": "papers_semanticscholar.csv"}

C = collections.Counter
_results = {"pass": 0, "fail": 0}


def norm(title):
    """Normalized title used for every title match in the review records."""
    t = unicodedata.normalize("NFKC", title or "").lower()
    return re.sub(r"[^a-z0-9]+", "", t)


def read(*parts):
    with open(os.path.join(*parts), encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def check(label, got, expected, tol=None):
    if tol is None:
        ok = got == expected
    else:
        ok = abs(float(got) - float(expected)) <= tol
    _results["pass" if ok else "fail"] += 1
    mark = "PASS" if ok else "FAIL"
    detail = "" if ok else f"   (expected {expected!r}, got {got!r})"
    print(f"  [{mark}] {label}: {got}{detail}")
    return ok


def section(title):
    print(f"\n== {title}")


def families_of(row):
    return [f.strip() for f in row["approach_families"].split(";") if f.strip()]


def cohen_kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = C(a), C(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe)


def dim_counts(rows, key="primary_dimension"):
    c = C(r[key] for r in rows)
    return [c[d] for d in DIMS]


def write_csv(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", metavar="OUT", help="write regenerated tables to this directory")
    args = ap.parse_args()

    # ------------------------------------------------------------------ search
    section("Search and deduplication (Sec. 2.3)")
    log = read(DATA, "1_search", "search_and_retrieval_log.csv")
    declared = sum(int(r["exported_records"]) for r in log if r["search_id"] != "cross_source_merge")
    check("records declared in the five source exports", declared, 5187)
    raw = {r["search_id"]: int(r["exported_records"]) for r in log}
    check("records from the IEEE Xplore query and the supplementary arXiv query (Sec. 2.3)",
          raw["ieee_01"] + raw["arxiv_supplementary"], 3559)

    lists = {s: read(DATA, "1_search", "title_lists", f) for s, f in SOURCE_LISTS.items()}
    check("rows of the five date-filtered title lists",
          [len(lists[s]) for s in ["ACM", "arXiv", "IEEE", "Scopus", "SemanticScholar"]],
          [739, 1177, 2408, 297, 247])
    listed = sum(len(v) for v in lists.values())
    check("records in the date-filtered title lists", listed, 4868)
    check("records removed by the date filter or as duplicates within the arXiv results (declared - listed)", declared - listed, 319)

    ax = read(DATA, "1_search", "arxiv_records.csv")
    check("arXiv identifiers in arxiv_records.csv (unique)", (len(ax), len({r["arxiv_id"] for r in ax})), (1249, 1249))
    check("arXiv records by query (primary only, supplementary only, both)",
          [C(r["query"] for r in ax)[k] for k in ["primary", "supplementary", "both"]], [104, 1138, 7])
    check("arXiv results per query equal the declared export counts (111, 1145)",
          [sum(r["query"] in (q, "both") for r in ax) for q in ["primary", "supplementary"]],
          [raw["arxiv_primary"], raw["arxiv_supplementary"]])
    check("arXiv preprints first announced after March 2026 (identifier month 2604)",
          (sum(r["first_version_in_window"] == "no" for r in ax),
           all((r["first_version_in_window"] == "no") == r["arxiv_id"].startswith("2604.") for r in ax)), (71, True))
    four = {"cs.SE", "cs.AI", "cs.MA", "cs.RO"}
    check("arXiv records with none of cs.SE, cs.AI, cs.MA, cs.RO among their categories (no category filter)",
          sum(not (set(r["categories"].split(";")) & four) for r in ax), 307)
    in_window = {norm(r["title"]) for r in lists["arXiv"]}
    check("arXiv title list equals the in-window unique titles of arxiv_records.csv",
          in_window == {norm(r["title"]) for r in ax if r["first_version_in_window"] == "yes"}, True)
    check("declared - listed = date-filter removals + duplicates within the arXiv results",
          declared - listed == 311 + (len([r for r in ax if r["query"] == "both"]) + 1), True)

    union = collections.defaultdict(set)
    for s, rows in lists.items():
        for r in rows:
            union[norm(r["title"])].add(s)
    corpus = read(DATA, "2_screening", "search_corpus_4767.csv")
    corpus_tags = collections.defaultdict(set)
    for r in corpus:
        for s in r["sources"].split(";"):
            corpus_tags[norm(r["title"])].add(s.strip())
    check("unique normalized titles across the title lists", len(union), 4767)
    check("rows of search_corpus_4767.csv", len(corpus), 4767)
    check("cross-source duplicates removed", listed - len(union), 101)
    check("corpus titles equal the union of the title lists", set(corpus_tags) == set(union), True)
    check("corpus source tags equal the union of list memberships",
          all(corpus_tags[k] == union[k] for k in union), True)

    audit = read(DATA, "2_screening", "title_variant_dedup_audit.csv")
    exact = {r["title"] for r in corpus}
    listed_titles = {r["title"] for rows in lists.values() for r in rows}
    check("five merged title variants: same normalized title, variant in a title list, canonical kept in the corpus",
          len(audit) == 5 and all(
              norm(a["canonical_title"]) == norm(a["variant_title"]) and a["variant_title"] != a["canonical_title"]
              and a["variant_title"] in listed_titles and a["canonical_title"] in exact and a["variant_title"] not in exact
              for a in audit), True)

    single = C(next(iter(t)) for t in corpus_tags.values() if len(t) == 1)
    n_single = sum(single.values())
    check("single-source records", n_single, 4669)
    check("multi-source records", len(corpus) - n_single, 98)
    check("single-source records by source (IEEE, arXiv, ACM, Scopus, S2)",
          [single[s] for s in ["IEEE", "arXiv", "ACM", "Scopus", "SemanticScholar"]],
          [2369, 1104, 708, 270, 218])
    check("IEEE Xplore share of single-source records (%)", round(100 * single["IEEE"] / n_single, 1), 50.7)
    check("arXiv share of single-source records (%)", round(100 * single["arXiv"] / n_single, 1), 23.6)

    # --------------------------------------------------------------- screening
    section("Selection (Sec. 2.5, Fig. 1)")
    el = read(DATA, "2_screening", "eligibility_decisions.csv")
    inc = read(DATA, "2_screening", "included_studies.csv")
    check("candidates in eligibility_decisions.csv", len(el), 555)
    check("decisions", dict(sorted(C(r["decision"] for r in el).items())), {"excluded": 293, "included": 262})

    def kind(r):
        code = r["exclusion_code"]
        if code.startswith("criteria not fully met"):
            return "borderline"
        return "coded"

    excl = [r for r in el if r["decision"] == "excluded"]
    check("non-retained: coded / borderline",
          [C(kind(r) for r in excl)[k] for k in ["coded", "borderline"]], [275, 18])

    corpus_titles = set(corpus_tags)
    recomputed_match = ["yes" if norm(r["title"]) in corpus_titles else "no" for r in el]
    check("screening_corpus_match column agrees with a fresh title match",
          recomputed_match == [r["screening_corpus_match"] for r in el], True)
    match = C((m, r["decision"]) for m, r in zip(recomputed_match, el))
    n_matched = match[("yes", "excluded")] + match[("yes", "included")]
    check("candidates matching the screening corpus", n_matched, 506)
    check("candidates without a corpus match (included among them)",
          (match[("no", "excluded")] + match[("no", "included")], match[("no", "included")]), (49, 14))
    check("corpus records not retained at triage (corpus - matched candidates)", len(corpus) - n_matched, 4261)
    check("PRISMA left branch: excluded as coded / borderline",
          [sum(1 for m, r in zip(recomputed_match, el) if m == "yes" and r["decision"] == "excluded" and kind(r) == k)
           for k in ["coded", "borderline"]], [240, 18])
    check("no duplicate DOI or normalized title among candidates",
          len({r["doi"].lower() for r in el if r["doi"]}) == sum(1 for r in el if r["doi"])
          and len({norm(r["title"]) for r in el}) == len(el), True)

    crit = C()
    for r in excl:
        if kind(r) == "coded":
            for c in set(re.findall(r"[IE]\d", r["exclusion_code"])):
                crit[c] += 1
    check("criterion frequency among coded exclusions",
          [crit[c] for c in ["I1", "E3", "I2", "I4", "E1", "E5", "I5", "E4", "E2", "I3"]],
          [142, 102, 84, 46, 19, 13, 8, 7, 4, 2])

    inc_ids = {r["study_id"] for r in inc}
    check("included_studies.csv rows", len(inc), 262)
    check("included study_ids equal the included record_ids of the log",
          inc_ids == {r["record_id"] for r in el if r["decision"] == "included"}, True)
    check("identification_route of included studies not in the corpus",
          C(r["identification_route"] for r in inc)["not_in_screening_corpus_route_not_logged"], 14)

    section("Corpus composition (Sec. 2.8, Fig. 2)")
    full = dim_counts(inc)
    check("primary dimension (R1): beh/saf/temp/reg/multi", full, [105, 61, 14, 35, 47])
    check("publication status: published / preprint",
          [C(r["publication_status"] for r in inc)[k] for k in ["published", "preprint"]], [151, 111])
    pub = C(r["primary_dimension"] for r in inc if r["publication_status"] == "published")
    check("published papers per dimension", [pub[d] for d in DIMS], [57, 33, 10, 29, 22])
    years = [int(r["year"]) for r in inc]
    check("papers per year band (2019-23 / 2024 / 2025 / 2026)",
          [sum(2019 <= y <= 2023 for y in years), years.count(2024), years.count(2025), years.count(2026)],
          [27, 26, 151, 58])
    check("earliest publication year", min(years), 2019)

    # ------------------------------------------------------------------ coding
    section("Primary-dimension coding and agreement (Sec. 2.6)")
    pdim = read(DATA, "3_coding", "primary_dimension.csv")
    by_id = {r["study_id"]: r for r in inc}
    check("primary_dimension.csv covers the included studies, R1 label = included_studies.csv",
          len(pdim) == 262 and all(by_id[r["study_id"]]["primary_dimension"] == r["r1_dimension"]
                                   and norm(by_id[r["study_id"]]["title"]) == norm(r["title"]) for r in pdim), True)
    conf = {r["study_id"]: r["r1_confidence"] for r in pdim}
    check("R1 confidence: high / medium", [C(conf.values())[k] for k in ["high", "medium"]], [241, 21])
    a = [r["r1_dimension"] for r in pdim]
    b = [r["r2_dimension"] for r in pdim]
    check("R1/R2 agreement (papers)", sum(x == y for x, y in zip(a, b)), 226)
    check("Cohen's kappa R1 vs R2", round(cohen_kappa(a, b), 3), 0.812)
    check("primary dimension (R2; Table 4)", dim_counts(pdim, "r2_dimension"), [104, 69, 10, 32, 47])

    rec = [r for r in pdim if r["reconciled_dimension"]]
    check("reconciled R1/R2 disagreements = all disagreements",
          (len(rec), all(r["r1_dimension"] != r["r2_dimension"] for r in rec)), (36, True))
    check("reconciliation decisions toward R2 / R1",
          [C(r["reconciled_toward"] for r in rec)[k] for k in ["R2", "R1"]], [17, 19])
    rec_map = {r["study_id"]: r["reconciled_dimension"] for r in rec}
    applied = [dict(r, primary_dimension=rec_map.get(r["study_id"], r["primary_dimension"])) for r in inc]
    check("primary dimension with the R1/R2 reconciliation alone (Sec. 2.6)", dim_counts(applied), [104, 62, 15, 32, 49])

    p2 = read(DATA, "3_coding", "intra_rater_audit.csv")
    check("intra-rater sample: medium / high confidence",
          [C(r["pass1_confidence"] for r in p2)[k] for k in ["medium", "high"]], [21, 64])
    check("intra-rater Pass 1 = R1 labels",
          all(by_id[r["study_id"]]["primary_dimension"] == r["pass1_dimension"] for r in p2), True)
    check("intra-rater stability (Pass 1 = Pass 2)", sum(r["pass1_dimension"] == r["pass2_dimension"] for r in p2), 73)
    irec = [r for r in p2 if r["reconciled_dimension"]]
    check("reconciled intra-rater discordances = all discordances",
          (len(irec), all(r["pass1_dimension"] != r["pass2_dimension"] for r in irec)), (12, True))
    ranges = []
    for i, d in enumerate(DIMS):
        lo = full[i] - sum(1 for r in irec if r["pass1_dimension"] == d and r["pass2_dimension"] != d)
        hi = full[i] + sum(1 for r in irec if r["pass2_dimension"] == d and r["pass1_dimension"] != d)
        ranges.append([lo, hi])
    check("worst-case ranges under reassignment of the 12 discordances (Table 7)", ranges,
          [[99, 106], [58, 68], [13, 14], [33, 37], [47, 49]])
    # Table 4, "Reconciliation applied": both reconciliations; where a study is in both with
    # different decisions (study 120), the intra-rater decision is used.
    irec_map = {r["study_id"]: r["reconciled_dimension"] for r in irec}
    conflicts = sorted((s for s in set(rec_map) & set(irec_map) if rec_map[s] != irec_map[s]), key=int)
    check("studies in both reconciliations with different decisions", conflicts, ["120"])
    both = {**rec_map, **irec_map}
    applied = [dict(r, primary_dimension=both.get(r["study_id"], r["primary_dimension"])) for r in inc]
    check("primary dimension with both reconciliations applied (Table 4)", dim_counts(applied), [103, 61, 15, 34, 49])

    section("Approach families and coverage matrix (Sec. 2.7, Table 13)")
    af = read(DATA, "3_coding", "approach_families.csv")
    check("approach_families.csv covers the included studies",
          {r["study_id"] for r in af} == inc_ids and all(
              by_id[r["study_id"]]["primary_dimension"] == r["primary_dimension"] for r in af), True)
    matrix = C()
    for r in af:
        for f in families_of(r):
            matrix[(f, r["primary_dimension"])] += 1
    check("only the six defined families are used", {f for f, _ in matrix} <= set(FAMILIES), True)
    check("coverage-matrix appearances", sum(matrix.values()), 318)
    unmatched = C(r["primary_dimension"] for r in af if not families_of(r))
    check("unmatched papers per dimension", [unmatched[d] for d in DIMS], [3, 3, 0, 4, 5])

    gm_rows = []
    for f in FAMILIES:
        row = {"row": f, **{DIM_HEADER[d]: str(matrix[(f, d)]) for d in DIMS}}
        row["Total"] = str(sum(matrix[(f, d)] for d in DIMS))
        gm_rows.append(row)
    gm_rows.append({"row": "Total (papers per primary dimension)",
                    **{DIM_HEADER[d]: str(full[i]) for i, d in enumerate(DIMS)}, "Total": str(len(inc))})
    committed = read(RESULTS, "gap_matrix.csv")
    check("results/gap_matrix.csv equals the recomputed matrix", committed == gm_rows, True)

    section("Safety sub-strands (Sec. 7.2, Table 13)")
    ss = read(DATA, "3_coding", "safety_subtypes.csv")
    subtype = {r["study_id"]: r["subtype"] for r in ss}
    safety = [dict(r, safety_subtype=subtype.get(r["study_id"], "")) for r in af if r["primary_dimension"] == "safety"]
    check("safety_subtypes.csv covers the safety papers", set(subtype) == {r["study_id"] for r in safety}, True)
    sub = C(r["safety_subtype"] for r in safety)
    check("safety papers by sub-strand (functional / adversarial / both)",
          [sub[s] for s in SUBTYPES[:3]], [23, 29, 9])
    check("Pass 1 / Pass 2 agreement on sub-strand", sum(r["pass1_subtype"] == r["pass2_subtype"] for r in ss), 59)
    check("reconciled sub-strands = Pass 1/Pass 2 disagreements",
          all((r["reconciled"] == "yes") == (r["pass1_subtype"] != r["pass2_subtype"]) for r in ss), True)
    sm = C()
    for r in safety:
        for f in families_of(r):
            sm[(f, r["safety_subtype"])] += 1
    sm_rows = [{"row": f, **{s: str(sm[(f, s)]) for s in SUBTYPES}} for f in FAMILIES]
    sm_rows.append({"row": "Total (papers per subtype)", **{s: str(sub[s]) for s in SUBTYPES}})
    check("results/safety_subtype_family_matrix.csv equals the recomputed matrix",
          read(RESULTS, "safety_subtype_family_matrix.csv") == sm_rows, True)

    # ------------------------------------------- matrix under other labelings
    section("Coverage matrix under alternative primary labels (Sec. 2.9, Table 6)")
    r2_map = {r["study_id"]: r["r2_dimension"] for r in pdim}
    labelings = {
        "first_reviewer": {r["study_id"]: r["primary_dimension"] for r in inc},
        "second_reviewer": r2_map,
        "reconciled": {r["study_id"]: both.get(r["study_id"], r["primary_dimension"]) for r in inc},
    }
    alt_rows = []
    for name, lab in labelings.items():
        m = C()
        for r in af:
            for f in families_of(r):
                m[(f, lab[r["study_id"]])] += 1
        papers = C(lab.values())
        for f in FAMILIES:
            alt_rows.append({"labeling": name, "row": f, **{DIM_HEADER[d]: str(m[(f, d)]) for d in DIMS}})
        alt_rows.append({"labeling": name, "row": "Appearances",
                         **{DIM_HEADER[d]: str(sum(m[(f, d)] for f in FAMILIES)) for d in DIMS}})
        alt_rows.append({"labeling": name, "row": "Papers", **{DIM_HEADER[d]: str(papers[d]) for d in DIMS}})
    cell = {(r["labeling"], r["row"]): r for r in alt_rows}
    def cells(fam, dim):
        return [int(cell[(n, fam)][DIM_HEADER[dim]]) for n in labelings]
    check("Behavioral x Assurance Cases (R1 / R2 / reconciled)", cells("Assurance Cases", "behavioral"), [0, 0, 0])
    check("Temporal x Benchmarks", cells("Benchmarks", "temporal"), [4, 5, 5])
    check("Temporal x CPS Validation", cells("CPS Validation", "temporal"), [1, 0, 1])
    check("Regulatory x Runtime Monitors", cells("Runtime Monitors", "regulatory"), [6, 6, 7])
    check("Multi-agent x Benchmarks", cells("Benchmarks", "multiagent"), [36, 36, 38])
    check("Multi-agent x Assurance Cases", cells("Assurance Cases", "multiagent"), [0, 0, 0])
    check("Multi-agent x MLOps/Drift", cells("MLOps/Drift", "multiagent"), [0, 0, 0])
    check("appearances per dimension (R1 / R2 / reconciled)",
          [[int(cell[(n, "Appearances")][DIM_HEADER[d]]) for d in DIMS] for n in labelings],
          [[116, 81, 20, 52, 49], [113, 95, 13, 48, 49], [112, 83, 21, 51, 51]])
    check("results/gap_matrix_alternative_labelings.csv equals the recomputation",
          read(RESULTS, "gap_matrix_alternative_labelings.csv") == alt_rows, True)

    other = [r for r in inc if r["identification_route"] == "not_in_screening_corpus_route_not_logged"]
    check("other-method included papers per dimension", dim_counts(other), [3, 3, 1, 2, 5])
    check("primary dimension without the 14 other-method papers (Sec. 2.9)",
          dim_counts([r for r in inc if r not in other]), [102, 58, 13, 33, 42])

    # ------------------------------------------------------------ IEEE-only
    section("IEEE-only sensitivity (Sec. 2.9, Tables 4-5)")
    audit_rows = []
    ieee_only = set()
    for r in inc:
        k = norm(r["title"])
        tags = sorted(t.lower() for t in corpus_tags.get(k, set()))
        status = "unmatched_kept" if not tags else ("single_source" if len(tags) == 1 else "multi_source_kept")
        if tags == ["ieee"]:
            ieee_only.add(r["study_id"])
        audit_rows.append({"study_id": r["study_id"], "title": r["title"], "primary_dimension": r["primary_dimension"],
                           "sources": ";".join(tags), "provenance_status": status, "ieee_only": "yes" if tags == ["ieee"] else "no"})
    check("IEEE-only included studies", len(ieee_only), 110)
    check("results/ieee_source_audit.csv equals the recomputed audit",
          read(RESULTS, "ieee_source_audit.csv") == audit_rows, True)

    base_n = dict(zip(DIMS, full))
    excl_rows = [r for r in af if r["study_id"] not in ieee_only]
    excl_n = C(r["primary_dimension"] for r in excl_rows)
    excl_m = C()
    for r in excl_rows:
        for f in families_of(r):
            excl_m[(f, r["primary_dimension"])] += 1
    gs_rows, ok = [], True
    committed = {(g["family"], g["primary_dimension"]): g for g in read(RESULTS, "gap_matrix_ieee_only_sensitivity.csv")}
    for f in FAMILIES:
        for d in DIMS:
            bs = 100 * matrix[(f, d)] / base_n[d]
            es = 100 * excl_m[(f, d)] / excl_n[d] if excl_n[d] else 0.0
            row = {"family": f, "primary_dimension": d,
                   "baseline_cell_count": matrix[(f, d)], "baseline_dimension_n": base_n[d],
                   "baseline_cell_share": round(bs, 2), "excluding_ieee_only_cell_count": excl_m[(f, d)],
                   "excluding_ieee_only_dimension_n": excl_n[d], "excluding_ieee_only_cell_share": round(es, 2),
                   "difference_pp": round(es - bs, 2)}
            gs_rows.append(row)
            g = committed.get((f, d))
            ok = ok and g is not None and all(
                abs(float(g[c]) - float(row[c])) < 0.006 for c in row if c not in ("family", "primary_dimension"))
    check("results/gap_matrix_ieee_only_sensitivity.csv equals the recomputed cells",
          ok and len(committed) == len(gs_rows), True)

    # ------------------------------------------------------- system attributes
    section("System attributes (Table 9)")
    studies = read(DATA, "3_coding", "system_attributes.csv")
    types = {r["study_id"]: r["type"] for r in studies}
    check("system_attributes.csv study_ids equal the included studies", set(types) == inc_ids, True)
    table8 = {
        "agents": {"multi": 125, "single": 124, "n/a": 13},
        "memory": {"session": 150, "persistent": 40, "none": 16, "n/a": 56},
        "planning": {"implicit": 106, "explicit": 88, "none": 28, "n/a": 40},
        "tool_use": {"yes": 171, "no": 48, "n/a": 43},
        "environment": {"simulated": 175, "real": 54, "none": 27, "n/a": 6},
        "human": {"none": 190, "in_the_loop": 33, "on_the_loop": 8, "n/a": 31},
        "adaptation": {"none": 209, "self_evolving": 24, "updates": 20, "n/a": 9},
        "risk": {"low": 105, "medium": 85, "high": 69, "n/a": 3},
        "type": {"empirical": 224, "conceptual": 31, "survey": 4, "guidance": 3},
    }
    for col, expected in table8.items():
        check(f"system attributes (Table 9): {col}", dict(C(r[col] for r in studies)), expected)

    # ------------------------------------------------------------ sensitivity
    section("Sensitivity analyses (Table 4)")
    subsets = {
        "published_only": [r for r in inc if r["publication_status"] == "published"],
        "preprint_only": [r for r in inc if r["publication_status"] == "preprint"],
        "high_conf_only": [r for r in inc if conf[r["study_id"]] == "high"],
        "excl_ieee_only": [r for r in inc if r["study_id"] not in ieee_only],
        "pre2025": [r for r in inc if int(r["year"]) < 2025],
        "year_2025_26": [r for r in inc if int(r["year"]) >= 2025],
        "non_preprint_non_ieee": [r for r in inc if r["publication_status"] == "published"
                                  and r["study_id"] not in ieee_only],
        "empirical_only": [r for r in inc if types[r["study_id"]] == "empirical"],
    }
    sens_rows, bad = [], 0
    committed = read(RESULTS, "sensitivity_analyses.csv")
    for s in committed:
        rows = subsets[s["analysis_id"]]
        i = DIMS.index(s["dimension"])
        num, n = dim_counts(rows)[i], len(rows)
        p_sub, p_full = 100 * num / n, 100 * full[i] / len(inc)
        row = {"analysis_id": s["analysis_id"], "subset": s["subset"], "dimension": s["dimension"], "n_studies": n,
               "papers": num, "percent": round(p_sub, 1), "difference_pp": round(p_sub - p_full, 1)}
        sens_rows.append(row)
        same = (int(s["n_studies"]) == n and int(s["papers"]) == num
                and abs(float(s["percent"]) - row["percent"]) < 0.051
                and abs(float(s["difference_pp"]) - row["difference_pp"]) < 0.051)
        if not same:
            bad += 1
            print(f"     mismatch: {s['analysis_id']} / {s['dimension']}: committed {s}, recomputed {row}")
    check("results/sensitivity_analyses.csv rows that match the recomputation",
          f"{len(committed) - bad}/{len(committed)}", f"{len(committed)}/{len(committed)}")

    # ----------------------------------------------------------- bibliography
    section("Bibliography matching (Sec. 2.9)")
    bib = read(DATA, "5_bibliography", "bib_corpus_vs_context.csv")
    check("cited works", len(bib), 214)
    matched = [r for r in bib if r["study_id"]]
    check("corpus papers / contextual references", (len(matched), len(bib) - len(matched)), (62, 152))
    check("corpus papers matched by DOI / arXiv identifier / title",
          [C(r["match_method"] for r in matched)[k] for k in ["doi", "arxiv_id", "title"]], [54, 4, 4])
    check("matched corpus papers exist in included_studies.csv with the same DOI, arXiv identifier, or title",
          all(r["study_id"] in by_id and (
              (r["match_method"] == "doi" and r["doi"].lower() == by_id[r["study_id"]]["doi"].lower())
              or (r["match_method"] == "arxiv_id"
                  and by_id[r["study_id"]]["doi"].lower() == "10.48550/arxiv." + r["arxiv_id"])
              or (r["match_method"] == "title" and norm(r["title"]) == norm(by_id[r["study_id"]]["title"])))
              for r in matched), True)
    corpus_dois = {r["doi"].lower() for r in inc if r["doi"]}
    check("contextual references sharing a DOI or arXiv identifier with a corpus paper",
          sum(1 for r in bib if not r["study_id"]
              and ((r["doi"] and r["doi"].lower() in corpus_dois)
                   or (r["arxiv_id"] and "10.48550/arxiv." + r["arxiv_id"] in corpus_dois))), 0)

    # ------------------------------------------------------------------ write
    if args.write:
        os.makedirs(args.write, exist_ok=True)
        write_csv(os.path.join(args.write, "gap_matrix.csv"), list(gm_rows[0]), gm_rows)
        write_csv(os.path.join(args.write, "safety_subtype_family_matrix.csv"), list(sm_rows[0]), sm_rows)
        write_csv(os.path.join(args.write, "ieee_source_audit.csv"), list(audit_rows[0]), audit_rows)
        write_csv(os.path.join(args.write, "gap_matrix_ieee_only_sensitivity.csv"), list(gs_rows[0]), gs_rows)
        write_csv(os.path.join(args.write, "sensitivity_analyses.csv"), list(sens_rows[0]), sens_rows)
        write_csv(os.path.join(args.write, "gap_matrix_alternative_labelings.csv"), list(alt_rows[0]), alt_rows)
        print(f"\nRegenerated tables written to {args.write}")

    print(f"\n{_results['pass']} checks passed, {_results['fail']} failed.")
    return 1 if _results["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
