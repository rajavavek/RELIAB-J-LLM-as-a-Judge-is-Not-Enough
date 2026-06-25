# Annotation guidelines

Gold labels should be assigned using blind annotation. Objective tasks should be labeled using verifiable evidence, unit tests, symbolic answer keys, or source-span checks. Subjective tasks should use at least three qualified annotators, disagreement adjudication, and inter-rater reliability reporting.

## Annotator qualification criteria

- Factual QA / RAG: graduate degree or equivalent experience in information science; source verification test with at least 95% accuracy.
- Mathematical reasoning: graduate-level quantitative background; must solve benchmark calibration problems independently.
- Code correctness: professional software engineering experience of at least two years; must identify bugs in hidden-test calibration cases.
- Medical/Legal: domain-specific professional credential or equivalent; advisory items flagged and reviewed by a second expert.
- Creative writing: professional editing or creative-writing background; rubric calibration before annotation.

## Adjudication protocol

When three annotators disagree and no majority exists, a fourth domain expert adjudicates. The adjudicator sees previous labels and rationales but not model identity. If disagreement cannot be resolved, the item is marked as disputed and excluded from accuracy calculations while retained for agreement analysis.
