# Review codebook for the 262-paper agentic validation corpus

This file records the coding rules referenced in Section 2 of the manuscript. Both reviewers applied the primary-dimension rules independently to all 262 included papers; the primary reviewer also applied them in the three-pass intra-rater audit. The dimension definitions, all four borderline rules, and the tie-break order were frozen before the revision coding; both reviewers and the intra-rater audit used this version (Sec. 2.2). The labels of the first submission were assigned under an earlier, broader formulation and are not reused. The approach-family and secondary-dimension rules were applied by the primary reviewer only, so no inter-rater agreement exists for that layer.

## Primary-dimension decision rule

Assign each paper one primary validation dimension based on the validation object most central to the paper's contribution.

- `behavioral`: primary claim is capability measurement, benchmark performance, task completion quality, trajectory success, or evaluation design for measuring what the agent can do.
- `safety`: primary claim is hazard prevention, runtime constraint enforcement, containment, fallback, fail-safe operation, or assurance that unsafe behavior is blocked or bounded during execution.
- `temporal`: primary claim is evidence freshness, drift, post-deployment change, revalidation triggers, lifecycle degradation, or when previously valid evidence expires.
- `regulatory`: primary claim is governance, compliance, assurance cases, certification, auditability obligations, or how evidence is structured for external accountability.
- `multiagent`: primary claim is coordination, compositional assurance, interaction-level failures, or system properties that arise only from multiple interacting agents.

## Borderline rules

- `behavioral` vs `safety`: choose `behavioral` when the paper mainly measures capability or benchmark outcomes; choose `safety` when the main novelty is a runtime guard, intervention mechanism, or bounded-autonomy control.
- `temporal` vs `regulatory`: choose `temporal` when the paper centers on evidence decay or revalidation over time; choose `regulatory` when the main object is an external obligation, assurance artifact, or governance workflow.
- `safety` vs `multiagent`: choose `safety` when the main object is local containment or safe execution of one agent in context; choose `multiagent` when the core claim concerns emergent interaction properties, coordination failures, or compositional guarantees.
- `safety` vs `regulatory`: choose `regulatory` when the paper's central output is an assurance artifact or structured argument (e.g., a GSN/CAE safety case, an audit trail built for external review) even when its content concerns safety mechanisms; choose `safety` when the central, tested contribution is the enforcement mechanism itself (e.g., a runtime guard, an access-control gate, a verification gate that blocks an action) rather than the argument or documentation structure around it.

## Tie-break order

This ordering formalizes the borderline rules above and was part of the frozen codebook used by both reviewers.

1. Identify the property the paper validates or evidences, not the setting in which it is studied.
2. If that property exists only when several agents interact (coordination, delegation, joint conflict, compositional guarantees): `multiagent`.
3. If it is the containment or safe execution of one agent, even inside a multi-agent deployment: `safety`.
4. If the main output is an evidence structure for an external party: `regulatory`; if it is the persistence of evidence over change: `temporal`.
5. If two labels still fit: record `medium` confidence and the secondary dimension.

Examples: a guard that filters messages one agent at a time is `safety`; a study of how several individually safe agents jointly deadlock is `multiagent`.

## Approach families

Each family is defined by the kind of validation evidence a paper contributes, not by its topic or domain.

- `Benchmarks`: scored evaluation of agent behavior on a fixed or refreshable suite of tasks or environments, including LLM-as-judge and process-scoring protocols (illustrative examples, not necessarily in the corpus: SWE-bench, AgentBoard, MultiAgentBench).
- `Runtime Monitors`: mechanisms that observe an executing trajectory and detect, block, or contain violations within the session (guards, shields, policy enforcement, OOD or anomaly detectors).
- `CPS Validation`: validation of agents in closed loop with a physical or cyber-physical process, through simulation, digital twins, hardware-in-the-loop, or field deployment, where timing, delay, and physical state determine correctness.
- `Assurance Cases`: structured arguments (e.g., GSN, CAE, reusable patterns) that link claims to evidence to justify acceptable safety, security, or compliance, including automated or continuous assurance-case management.
- `MLOps/Drift`: post-deployment lifecycle practices that detect distribution, performance, or behavioral change across versions or operating periods and trigger revalidation, retraining, or rollback.
- `Reg Guidance`: papers that analyze, interpret, or operationalize regulatory, standards, or governance obligations (e.g., FDA, MDCG, IEC 62304, liability and accountability frameworks); a paper that also proposes a technical validation method additionally receives that family's tag.

Multi-family rule: a paper receives one tag for each family whose criterion is met by a substantive contribution, meaning the method it proposes or the evidence it produces, not a family mentioned only in related work. An evaluation receives the `Benchmarks` tag only when the paper builds and reports its own evaluation suite or protocol; testing a proposed method on an existing benchmark does not add that tag. Each tag yields one appearance, placed in the column of the paper's primary dimension; secondary dimensions are recorded in `approach_families.csv` but are not used in the coverage matrix. No intensity levels are coded. Papers matching no family (`unmatched`) contribute no appearances. Duplicate records were removed by title before screening; when a preprint and a published version of the same study were both retrieved, only one record was retained: the version of record if it was available by 31 March 2026, and otherwise the preprint.

## Confidence labels

- `high`: the paper's title, abstract, and introduction/conclusion align clearly with one primary dimension.
- `medium`: the paper contributes to multiple dimensions or uses vocabulary that leaves the primary validation object partially ambiguous. A secondary dimension is recorded only in the first case, i.e. when the paper contributes substantively to a second dimension (14 of the 21 medium-confidence papers); in the second case no secondary dimension is recorded (7 papers). For records 16, 218, and 343 the secondary dimension (multiagent, safety, and temporal, respectively) was added during the revision after the full texts were re-read; secondary dimensions are not used in any count, so no reported figure changes.
- `low`: the primary dimension is inferred rather than stated, because the paper treats validation only tangentially or provides too little information to discriminate between dimensions.

No study received a low label.

## Audit procedure

- Pass 1: assign primary dimension and confidence label.
- Pass 2: time-separated re-coding audit on all medium-confidence papers plus a stratified high-confidence sample.
- Pass 3: reconcile each Pass 1/Pass 2 discordance against this frozen codebook and flag it as a borderline case.
- Disagreements between the two reviewers (36 of 262) were not adjudicated into the analysis labels; all analyses use the primary reviewer's label. The reconciliation decisions recorded in `primary_dimension.csv` are reported only as a sensitivity analysis.

## Safety sub-strands

The 61 papers with primary dimension `safety` were additionally coded by hand as `functional_safety`, `adversarial_security`, or `both`, in two passes; the two discordant cases were reconciled in a third pass. All three are in `safety_subtypes.csv`. The distinction follows Section 6.2 of the manuscript, where the two sub-strands are separated by threat model, assurance argument, standards, and methods. The dates of the two passes were not recorded.

## Intended use

The codebook is released for inspectability and external re-coding. It is not a claim of observer-independence.