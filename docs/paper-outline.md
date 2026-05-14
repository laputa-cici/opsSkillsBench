# Paper Outline

Working title:

`SkillBench for Management Operations: Evaluating How Domain Skills Change Agent Performance on Deterministic Business Tasks`

## 1. Abstract skeleton

This paper introduces a management-operations skill benchmark for evaluating how large language models and agent frameworks perform on realistic business tasks derived from public operations datasets, including control-tower exception review, sourcing concentration review, and disruption recovery control. The benchmark uses deterministic, file-based evaluation and compares systems under three skill conditions: no skill, provided skills, and self-created skills. We show how externally sourced or adapted domain skills affect framework taxonomy, operational action mapping, feasibility, and efficiency across multiple agents, and we analyze when agent-generated skills can substitute for benchmark-provided skills.

## 2. Introduction

Motivate three points:

- Operations work is procedural, high-stakes, and constraint-heavy.
- Existing agent benchmarks underrepresent management-operations workflows.
- Skill mechanisms are widely discussed, but there is little controlled evidence for their value on deterministic business tasks.

End the introduction with contributions:

1. A new management-operations benchmark in a deterministic Harbor / SkillsBench-style format grounded in external datasets and skill-market provenance.
2. A controlled evaluation protocol for `no skill`, `provided skills`, and `self-created skills`.
3. An empirical analysis across multiple model + agent stacks.

## 3. Related work

Cover:

- LLM agent benchmarks
- Tool-use and workflow benchmarks
- Skill or memory augmentation for agents
- Operations research and business process automation benchmarks

## 4. Benchmark design

### 4.1 Domain scope

- inventory management
- logistics and delivery-risk operations
- procurement and supplier operations
- capacity planning and recovery
- manufacturing scheduling

### 4.2 Task design principles

- realistic scenario framing
- deterministic outputs
- explicit file targets
- reproducible local execution
- procedural skills instead of answer leakage
- skill-sensitive framework fields rather than pure ETL or formula execution

### 4.3 Skill conditions

- no skill
- provided skills
- self-created skills

## 5. Experimental setup

### 5.1 Systems under test

Table template:

| Model | Agent framework | Tool policy | Skill path convention |
| --- | --- | --- | --- |

### 5.2 Task set

Table template:

| Task | Domain | Required outputs | Main constraints | Difficulty |
| --- | --- | --- | --- | --- |

### 5.3 Metrics

- full success
- normalized score
- constraint-feasibility
- cost and runtime
- skill usage and skill creation

### 5.4 Reproducibility

- fixed benchmark version
- fixed prompts
- repeated runs per condition
- transcript and artifact retention

## 6. Results

### 6.1 Main performance table

Table template:

| Agent | No skill | Provided skills | Self-created skills | Delta provided vs none |
| --- | --- | --- | --- | --- |

### 6.2 Per-task breakdown

Highlight where skills matter most.

Expected pattern to test:

- limited skill gains on pure data-processing smoke tests
- stronger gains on control-tower tasks when skills define service/cost/cash/resilience tradeoffs
- stronger gains on sourcing review tasks when skills define Kraljic segmentation and mitigation strategies
- mixed gains on recovery scheduling: feasibility may be algorithmic, while bottleneck/action classification should be more skill-sensitive

### 6.3 Efficiency tradeoffs

Show whether skills reduce retries, tool calls, cost, or wall-clock time.

### 6.4 Self-created skill analysis

Inspect:

- what kinds of skills agents create
- whether they are procedural or task-specific
- whether they are reused
- where they fail

## 7. Qualitative error analysis

Create a small taxonomy:

- output formatting failure
- incorrect formula or scoring rule
- constraint violation
- wrong skill selection
- good reasoning but incomplete artifact generation
- poor self-created skill quality

## 8. Discussion

Discuss:

- what this means for enterprise agent deployment
- when curated domain skills are worth the maintenance cost
- whether skill creation can be trusted in constrained workflows

## 9. Limitations

- small task coverage
- provenance and licensing constraints may limit which external skills can be vendored
- possible benchmark overfitting
- limited agent set in pilot study

## 10. Conclusion

Close on the main message:

Management-operations work is a strong testbed for skill-aware agents because it combines structured reasoning, explicit business rules, and machine-verifiable outputs.

## Figures and tables to prepare

- `Figure 1`: benchmark overview and three skill conditions
- `Figure 2`: per-task success by condition
- `Figure 3`: cost versus score scatter plot
- `Table 1`: benchmark task summary
- `Table 2`: main results across agents
- `Table 3`: self-created skill quality analysis

## Artifact checklist

- benchmark repository
- frozen benchmark version tag
- run configuration files
- transcripts and output artifacts
- scoring scripts
- paper appendix with task summaries
