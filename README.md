# Beyond Component Testing: Validating Agentic AI Systems — review data

This repository contains the supplementary data for the systematic mapping study *Beyond Component Testing: Validating Agentic AI Systems* by F. O. Mirto, L. D'Agati, G. Tricomi, S. Silvestri, F. Longo, A. Puliafito and G. Merlino (manuscript under review at *Artificial Intelligence Review*).

It contains:

- the search queries, the title lists of the date-filtered search exports and the retrieval log;
- the screening corpus and the eligibility log of the 555 candidates;
- the codebook and the coding sheets of the 262 included papers;
- the derived tables reported in the manuscript;
- a script that recomputes the reported counts and derived tables from the data and checks them.

Table and section numbers below refer to the revised manuscript.

## Repository layout

```
data/
  1_search/          queries, date-filtered title lists, retrieval log, arXiv records
  2_screening/       screening corpus, merged title variants, stage summary,
                     eligibility log, included studies
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
| After the 1 January 2019 – 31 March 2026 date filter (311 removed) and removal of 8 duplicates within the arXiv results | 4,868 | `data/1_search/title_lists/*.csv` |
| Unique after cross-source title deduplication (101 removed) | 4,767 | `data/2_screening/search_corpus_4767.csv` |
| Not retained at title and title/abstract triage | 4,261 | per-record decisions not logged |
| Candidates from the screening corpus | 506 | `eligibility_decisions.csv`, column `screening_corpus_match` |
| Candidates identified through other methods | 49 | `eligibility_decisions.csv`, column `screening_corpus_match` |
| Candidates assessed in full text | 555 | `data/2_screening/eligibility_decisions.csv` |
| Included studies | 262 | `data/2_screening/included_studies.csv` |

Of the 4,767 unique records, 4,669 come from a single source (IEEE Xplore 2,369; arXiv 1,104; ACM Digital Library 708; Scopus 270; Semantic Scholar 218) and 98 from two or more sources.

The 293 candidates that were not retained comprise:

- 275 records with an explicit criterion code: 240 from the screening corpus and 35 identified through other methods;
- 18 borderline records from the screening corpus, coded as `criteria not fully met (lower confidence)`.

The 49 candidates without a match in the screening corpus were found outside the database searches, through forward and backward citation searching and through other sources the authors encountered informally (blogs, news, conversations with other researchers). Fourteen of them were included. The route by which each record was found was not logged. The PRISMA flow diagram (Fig. 1) shows them in the "other methods" branch. Eight of them first appeared between 27 April and 2 July 2026, after the end of the window, and are excluded under I5.

### Dates, recorded version and publication status

The manuscript keeps three dates apart (Sec. 2.3–2.4):

- **Eligibility (criterion I5)** depends only on the date of first public availability, which must fall between 1 January 2019 and 31 March 2026. That date is:
  - the first online (early-access) date for journal papers;
  - the earlier of the conference date and the first online date for conference papers;
  - the announcement date of the first version for arXiv preprints.
- **Recorded version.** Each study is recorded (DOI, venue, year) in the version that was available on 31 March 2026: the version of record if it had been published by then, and otherwise the arXiv version. The `year` column is the year of this recorded version, and the year bands of Fig. 2 use it.
- **Publication status** refers to the same date. A study counts as `published` when its peer-reviewed version was available by 31 March 2026, and as `preprint` otherwise. Four IEEE conference papers (studies 64, 108, 294 and 299) were presented in February–March 2026 but added to IEEE Xplore in April 2026. Their conference date is used, so they are recorded as published.

## Reproducing the numbers

```
python3 scripts/reproduce.py
python3 scripts/reproduce.py --write build/   # also write the regenerated tables
```

The script uses only the Python standard library (Python 3.8 or later). It recomputes from `data/`:

- the search, deduplication and selection counts (Sec. 2.3, 2.5; Fig. 1);
- the corpus composition and publication status (Sec. 2.8; Fig. 2);
- the inter-rater and intra-rater agreement (Sec. 2.6) and the worst-case ranges for the intra-rater discordances (Table 7);
- the system attributes (Table 9);
- the coverage matrix and its safety sub-strand columns (Table 13);
- the coverage matrix under the second reviewer's and the reconciled labels (Table 6);
- the IEEE-only audit and all sensitivity analyses (Tables 4–5), including the counts without the 14 papers identified through other methods (Sec. 2.9);
- the matching of the bibliography against the corpus (Sec. 2.9).

It compares each value with the manuscript and with the files in `results/`, and exits with status 1 if any check fails. With `--write`, it also writes the recomputed numeric columns of the six result tables, so that they can be compared with the files in `results/`.

Titles are matched after Unicode NFKC normalization, lower-casing, and removal of every character that is not a letter or a digit. Every file about included papers is keyed by `study_id`, which equals `record_id` in the eligibility log.

## Files

All tables are UTF-8 CSV files with a header row. Lists inside a cell are separated by `;`. Empty cells mean "not applicable".

### `data/1_search/`

- `queries/<source>.txt`: the query of each source (ACM Digital Library, arXiv, IEEE Xplore, Scopus, Semantic Scholar) and its declared export count. For arXiv, the query is given both as entered and as intended.
- `search_and_retrieval_log.csv`: one row per query, plus one for the cross-source merge.
  - `exported_records` is the export count declared in the query file, before the date filter.
  - `title_list_rows` is the number of rows of the released title list.
  - `post_processing` describes the date filter and the deduplication applied to the export.

  Search dates were logged for IEEE Xplore and Scopus only. All queries were repeated on the same five sources in September 2026 (second refresh pass); records first available after 31 March 2026 are excluded by the date filter.
- `title_lists/papers_<source>.csv`: titles of the date-filtered records of each source: ACM 739, arXiv 1,177, IEEE Xplore 2,408, Scopus 297 and Semantic Scholar 247 rows. The arXiv list merges the primary and the supplementary query.
- `arxiv_records.csv`: the 1,249 arXiv identifiers returned by the two arXiv queries, with:
  - the query that returned each identifier;
  - its subject categories;
  - its submission and announcement dates;
  - the date-window decision, based on the announcement of the first version.

  No subject-category filter was applied. The 71 preprints first announced in April 2026 are outside the window.

### `data/2_screening/`

- `search_corpus_4767.csv`: the screening corpus (`title`, `sources`).
- `title_variant_dedup_audit.csv`: five title pairs that differ only in punctuation or spacing and were merged into one record.
- `screening_stage_summary.csv`: record counts of each step from retrieval to inclusion (Fig. 1).
- `eligibility_decisions.csv`: one row per candidate, with:
  - decision, year and DOI;
  - criterion code (I1–I5, E1–E5; Sec. 2.4);
  - a short rationale;
  - whether the candidate matches a record of the screening corpus.

  All 555 candidates were read in full text.
- `included_studies.csv`: the 262 included studies, with:
  - DOI, year and venue of the recorded version;
  - publication status at 31 March 2026 (151 published, 111 preprints);
  - primary dimension (rater 1, used in all analyses);
  - identification route.

### `data/3_coding/`

One file per coding step. Rater 1 alone coded the approach families, the safety sub-strands and the secondary dimensions.

- `codebook.md`: the coding rules (primary dimension, borderline rules, tie-break order, approach families, confidence labels, audit procedure, safety sub-strands). The manuscript summarizes the assignment principle and refers to this file.
- `primary_dimension.csv`: the primary dimension and confidence assigned independently by rater 1 and rater 2 to all 262 papers (Sec. 2.6). For the 36 disagreements, `reconciled_dimension`, `reconciled_toward` and `reconciliation_reason` give the reconciliation decision. It is used only as a sensitivity analysis (Tables 4 and 6).
- `intra_rater_audit.csv`: rater 1's time-separated re-coding (Pass 2) of 85 papers (all 21 medium-confidence papers and 64 high-confidence papers), with a short rationale. For the 12 discordances between Pass 1 and Pass 2, the reconciliation columns give the Pass 3 decision.
- `approach_families.csv`, with for each paper:
  - its approach families (Table 3);
  - `family_status` (`matched`, `multi_family` or `unmatched`);
  - its secondary dimensions;
  - an evidence excerpt from the paper with its page;
  - a short rationale for the tags.
- `safety_subtypes.csv`: the sub-strand (`functional_safety`, `adversarial_security` or `both`) of each of the 61 safety papers in Pass 1 and Pass 2, with:
  - the final label (`reconciled` = yes for the two discordant cases);
  - an evidence excerpt with its page;
  - a short rationale.
- `system_attributes.csv`: study type and eight system attributes (Table 9; also the empirical-only row of Table 4), with a confidence label and an evidence note. These were coded by a coauthor and have no inter-rater agreement estimate.

### `data/4_case_studies/`

`case_study_evidence_table.csv` lists each claim used in the constructed case studies of Sec. 8 (Table 15), with:

- its claim type and evidence class (observed, literature-supported, constructed, illustrative);
- its source and the location in the source;
- the supporting evidence.

### `data/5_bibliography/`

- `bib_corpus_vs_context.csv`: the 214 works cited in the manuscript, matched to the corpus by DOI, arXiv identifier or title. 62 of them are corpus papers and 152 are contextual references.
- `bib_audit_report.md`: the matching rules, and the cited works dated after the search window.

### `results/`

| File | Manuscript |
| --- | --- |
| `gap_matrix.csv` | coverage matrix of approach families by primary dimension (Table 13) |
| `gap_matrix_alternative_labelings.csv` | coverage matrix under the first reviewer's, the second reviewer's and the reconciled primary labels (Table 6) |
| `safety_subtype_family_matrix.csv` | safety appearances by sub-strand (safety columns of Table 13) |
| `sensitivity_analyses.csv` | dimension shares under alternative corpus definitions (Table 4); `difference_pp` is the difference from the full corpus in percentage points |
| `gap_matrix_ieee_only_sensitivity.csv` | coverage-matrix cells with and without IEEE-only papers (Table 5) |
| `ieee_source_audit.csv` | source tags of each included study and the IEEE-only flag |

A study is IEEE-only when the union of the source tags of all its title matches in the screening corpus is exactly IEEE Xplore (110 papers).

In `ieee_source_audit.csv`, `provenance_status` is `single_source`, `multi_source_kept` or `unmatched_kept`. The 14 studies without a title match are kept in every subset. Study 18 (RefuteBench 2.0) matches both arXiv and IEEE Xplore after punctuation normalization, so it is not IEEE-only.


## Licence

The data and documentation are released under the Creative Commons Attribution 4.0 International licence ([`LICENSE`](LICENSE)). The scripts in `scripts/` are released under the MIT licence ([`LICENSE-CODE`](LICENSE-CODE)).

Paper titles in the title lists and coding sheets are bibliographic metadata of the cited works and remain subject to their publishers' terms.

## Citation

Please cite the article once it is published. Until then, cite this repository using [`CITATION.cff`](CITATION.cff).
