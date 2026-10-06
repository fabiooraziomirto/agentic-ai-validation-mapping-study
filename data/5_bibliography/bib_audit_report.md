# Bibliography audit

This note records which works cited in the manuscript belong to the 262-paper corpus, and which cited works fall outside the search window. It refers to the manuscript's bibliography file (`sn-bibliography.bib`, not part of this repository).

## Corpus papers and contextual references

`bib_corpus_vs_context.csv` has one row per cited work (214 rows).

| Column | Content |
| --- | --- |
| `bib_key`, `title`, `doi` | BibTeX key, title, and DOI of the cited work |
| `arxiv_id` | arXiv identifier of the cited work (`eprint` field), if any |
| `study_id` | matched study in `../2_screening/included_studies.csv`, if any |
| `match_method` | `doi`, `arxiv_id`, or `title` |

Matching rules, applied in this order:

1. DOI: the cited DOI equals the DOI of an included study.
2. arXiv identifier: the cited arXiv identifier corresponds to an included study whose DOI is the arXiv DOI (`10.48550/arxiv.<id>`).
3. Title: the normalized titles are identical.

Results:

- 62 cited works are corpus papers: 54 matched by DOI, 4 by arXiv identifier (`agentDrift2025`, `agenticSelfevolving2025`, `agentsafeUnified2025`, `unifiedFramework2025`; studies 226, 220, 228, 232, cited under a different title of the same arXiv preprint), and 4 by identical normalized title.
- 152 are contextual references.
- No contextual reference shares a DOI or an arXiv identifier with a corpus paper.

## Works dated after the search window (1 January 2019 to 31 March 2026)

Two cited works were first posted on arXiv after the window. Both are cited as context only and are not corpus papers.

- `autogenesis2026`, *Autogenesis: A Self-Evolving Agent Protocol* (arXiv 2604.15034, v1 16 April 2026)
- `ahe2026`, *Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses* (arXiv 2604.25850, v1 28 April 2026)

Five cited works have a print-issue date after March 2026, but their online version appeared inside the window. Their `year` field may therefore differ from the printed issue.

| Key | DOI | Online | Print issue |
| --- | --- | --- | --- |
| `reliabilitybydesignAgentic2025` | 10.1109/MRL.2026.3660197 | 2026-02-19 | 2026-06 |
| `parallelNursing2025` | 10.1109/TCSS.2025.3605582 | 2025-10-15 | 2026-04 |
| `overviewGenai2025` | 10.1109/MCOMSTD.2025.3644899 | 2025-12-25 | 2026-09 |
| `autoonbenchBenchmark2025` | 10.1364/JOCN.589201 | 2026-03-27 | 2026-09 |
| `meanfieldDeep2025` | 10.1109/LRA.2026.3669783 | 2026-03-03 | 2026-05 |

The dates are taken from Crossref.
