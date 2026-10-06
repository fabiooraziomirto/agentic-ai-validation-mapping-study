# Beyond Component Testing: Validating Agentic AI Systems — review data

This repository contains the supplementary data of the systematic mapping study *Beyond Component Testing: Validating Agentic AI Systems* (F. O. Mirto, L. D'Agati, G. Tricomi, S. Silvestri, F. Longo, A. Puliafito, G. Merlino; manuscript under review).

It contains:

- the search queries and the title lists of the search exports;
- the screening corpus and the eligibility log of the 555 candidates;
- the codebook and the coding sheets of the 262 included papers;
- the derived tables reported in the manuscript;
- a script that recomputes the reported counts and derived tables from the data.

Table and section numbers below refer to the manuscript.

## Repository layout

```
data/
  1_search/          queries, date-filtered title lists, retrieval log
  2_screening/       screening corpus, merged title variants, eligibility log, included studies
  3_coding/          codebook, primary-dimension labels (two raters), intra-rater audit,
                     approach families, safety sub-strands, system attributes
  4_case_studies/    evidence status of the claims used in the constructed case studies
  5_bibliography/    cited works matched to the corpus, bibliography audit notes
results/             derived tables (coverage matrix, sensitivity analyses, IEEE-only audit)
scripts/
  reproduce.py       recomputes the counts and the derived tables and checks them
```

## From search to corpus

| Step | Records | Files |
| --- | ---: | --- |
| Records declared in the five source exports | 5,187 | `data/1_search/queries/*.txt`, `search_and_retrieval_log.csv` |
| After the 1 January 2019 – 31 March 2026 date filter and removal of duplicates within the arXiv results | 4,868 | `data/1_search/title_lists/*.csv` |
| Unique after cross-source title deduplication (101 removed) | 4,767 | `data/2_screening/search_corpus_4767.csv` |
| Candidates assessed for eligibility | 555 | `data/2_screening/eligibility_decisions.csv` |
| … of which match a screening-corpus record | 506 | column `screening_corpus_match` |
| Included studies | 262 | `data/2_screening/included_studies.csv` |

The 293 non-retained candidates comprise:

- 275 records with an explicit criterion code;
- 18 borderline records (`criteria not fully met (lower confidence)`).

Criterion I5 (time window, 1 January 2019 – 31 March 2026) uses the date of first public availability: the first online (early-access) date for journal papers; for conference papers, the earlier of the conference date and the first online date; and the announcement date of the first version for arXiv preprints (Sec. 2.3–2.4).

Each study is recorded (DOI, venue, year) in the version available on 31 March 2026: the version of record if it had been published by then, otherwise the arXiv version. Publication status refers to the same date (`published` = peer-reviewed version available by 31 March 2026, otherwise `preprint`), and `year` is the year of the recorded version.

The 49 candidates without a match in the screening corpus (14 of them included) were identified outside the database searches, through citation searching and other sources the authors encountered informally (blogs, news, conversations with other researchers); the source of each record was not logged. The PRISMA flow diagram (Fig. 1) shows them in the "other methods" branch. Eight of them, identified after the last logged database search, are excluded under I5.

## Reproducing the numbers

```
python3 scripts/reproduce.py
python3 scripts/reproduce.py --write build/   # also write the regenerated tables
```

The script uses only the Python standard library (Python 3.8 or later). It recomputes from `data/`:

- the search, deduplication, and selection counts (Sec. 2.3, 2.5; Fig. 1);
- the corpus composition (Sec. 2.8);
- the inter-rater and intra-rater agreement (Sec. 2.6; Table 7);
- the system attributes (Table 9);
- the coverage matrix and its safety sub-strand columns (Table 13);
- the coverage matrix under the second reviewer's and the reconciled labels (Table 6);
- the IEEE-only audit and all sensitivity analyses (Tables 4–5), including the counts without the 14 papers identified through other methods (Sec. 2.9);
- the bibliography matching.

It compares each value with the manuscript and with the files in `results/`, and exits with status 1 if any check fails.

`--write` writes the recomputed numeric columns of the six result tables, so they can be compared with the files in `results/`.

Titles are matched after Unicode NFKC normalization, lower-casing, and removal of every character that is not a letter or digit. Every file about included papers is keyed by `study_id`, which equals `record_id` in the eligibility log.

## Files

All tables are UTF-8 CSV files with a header row. Lists inside a cell are separated by `;`. Empty cells mean "not applicable".

### `data/1_search/`

- `queries/<source>.txt`: the query of each source (ACM Digital Library, arXiv, IEEE Xplore, Scopus, Semantic Scholar) and its declared export count. For arXiv, the query is given as entered and as intended.
- `search_and_retrieval_log.csv`: one row per query plus one for the cross-source merge. `exported_records` is the export count declared in the query file (before the date filter); `title_list_rows` is the number of rows of the released title list; `post_processing` describes the date filter and deduplication applied to the export. Search dates were logged for IEEE Xplore and Scopus only. All queries were repeated on the same five sources in September 2026 (second refresh pass); records first available after 31 March 2026 are excluded by the date filter (criterion I5).
- `title_lists/papers_<source>.csv`: titles of the date-filtered records of each source (739, 1,177, 2,408, 297, and 247 rows). The arXiv list merges the primary and supplementary queries.
- `arxiv_records.csv`: the 1,249 arXiv identifiers returned by the two arXiv queries, with query, categories, submission and announcement dates, and the date-window decision (first public announcement of the first version). No subject-category filter was applied.

### `data/2_screening/`

- `search_corpus_4767.csv`: the screening corpus (`title`, `sources`).
- `title_variant_dedup_audit.csv`: five title pairs that differ only in punctuation or spacing and were merged into one record.
- `screening_stage_summary.csv`: record counts of each step from retrieval to inclusion (Fig. 1).
- `eligibility_decisions.csv`: one row per candidate with decision, year, DOI, criterion code (I1–I5, E1–E5; Sec. 2.4), a short rationale, and whether the candidate matches a corpus record. All 555 candidates were read in full text.
- `included_studies.csv`: the 262 included studies with venue, publication status (147 published, 115 preprints; the status recorded when each paper was coded, not re-checked at a common date), primary dimension (rater 1, used in all analyses), and identification route.
- `eligibility_log_history.md`: how the eligibility log changed between the submitted and the revised manuscript.

### `data/3_coding/`

One file per coding step. Only rater 1 coded the approach families, safety sub-strands, and secondary dimensions.

- `codebook.md`: the coding rules (primary dimension, borderline rules, tie-break order, approach families, confidence labels, audit procedure, safety sub-strands).
- `primary_dimension.csv`: primary dimension and confidence assigned independently by rater 1 and rater 2 to all 262 papers (Sec. 2.6). For the 36 disagreements, `reconciled_dimension`, `reconciled_toward`, and `reconciliation_reason` give the reconciliation decision, which is used only as a sensitivity analysis (Table 4).
- `intra_rater_audit.csv`: rater 1's time-separated re-coding (Pass 2) of 85 papers (all 21 medium-confidence papers and 64 high-confidence papers), with a short rationale. For the 12 Pass 1/Pass 2 discordances, the reconciliation columns give the Pass 3 decision.
- `approach_families.csv`: approach families (Table 3), `family_status` (`matched`, `multi_family`, or `unmatched`), secondary dimensions, an evidence excerpt from the paper with its page, and a short rationale for the tags.
- `safety_subtypes.csv`: the sub-strand (`functional_safety`, `adversarial_security`, `both`) of the 61 safety papers in Pass 1 and Pass 2, the final label (`reconciled` = yes for the two discordant cases), an evidence excerpt with page, and a short rationale.
- `system_attributes.csv`: study type and eight system attributes (Table 9; empirical-only row of Table 4), with a confidence label and an evidence note. Provided by a coauthor; no inter-rater agreement estimate.

### `data/4_case_studies/`

`case_study_evidence_table.csv` lists each claim used in the constructed case studies of Sec. 8 (Table 15) with its claim type, evidence class, source, location in the source, and the supporting evidence.

### `data/5_bibliography/`

- `bib_corpus_vs_context.csv`: the 214 works cited in the manuscript, matched to the corpus by DOI, arXiv identifier, or title (62 corpus papers, 152 contextual references).
- `bib_audit_report.md`: matching rules and works dated after the search window.

### `results/`

| File | Manuscript |
| --- | --- |
| `gap_matrix.csv` | coverage matrix of approach families by primary dimension (Table 13) |
| `gap_matrix_alternative_labelings.csv` | coverage matrix under the first reviewer's, the second reviewer's, and the reconciled primary labels (Table 6) |
| `safety_subtype_family_matrix.csv` | safety appearances by sub-strand (safety columns of Table 13) |
| `sensitivity_analyses.csv` | dimension shares under alternative corpus definitions (Table 4); `difference_pp` is the difference from the full corpus in percentage points |
| `gap_matrix_ieee_only_sensitivity.csv` | coverage-matrix cells with and without IEEE-only papers (Table 5) |
| `ieee_source_audit.csv` | source tags of each included study and the IEEE-only flag |

A study is IEEE-only when the union of the source tags of all its title matches in the screening corpus is exactly IEEE Xplore (110 papers). In `ieee_source_audit.csv`, `provenance_status` is `single_source`, `multi_source_kept`, or `unmatched_kept`; the 14 studies without a title match are kept in every subset. Study 18 (RefuteBench 2.0) matches both arXiv and IEEE Xplore after punctuation normalization and is not IEEE-only.

`scripts/reproduce.py` recomputes the numeric content of all six tables and checks it against these files.

## Not included

- The pre-filter search exports (with abstracts, venues, years, and DOIs). Only their record counts are reported.
- Per-record decisions of the title and title/abstract triage of the 4,767 corpus records. These were not logged.
- The identification route of the 49 candidates without a corpus match. This was not logged.
- The full texts of the included papers.

## Licence

The data and documentation are released under the Creative Commons Attribution 4.0 International licence ([`LICENSE`](LICENSE)). The scripts in `scripts/` are released under the MIT licence ([`LICENSE-CODE`](LICENSE-CODE)).

Paper titles in the title lists and coding sheets are bibliographic metadata of the cited works and remain subject to their publishers' terms.

## Citation

Please cite the article once it is published. Until then, cite this repository using [`CITATION.cff`](CITATION.cff).