# RELIAB-J Annotation Guidelines

## Goal
Annotators verify the gold label for each base item before perturbations are generated. The gold label should reflect the response that best satisfies the user prompt, task context, and explicit rubric.

## Procedure

1. Read the prompt, context, both candidate responses, and rubric.
2. Select `A`, `B`, or `tie` for pairwise items.
3. Provide confidence from 0.0 to 1.0.
4. Add a short rationale that cites the verification evidence.
5. Mark `flag_ambiguous = yes` when the item lacks enough evidence, contains two similarly valid responses, or requires specialized expertise not available to the annotator.

## Domain-specific evidence

- **Factual QA:** Use retrieved source passages and contradiction checks.
- **Mathematics:** Use symbolic or arithmetic verification.
- **Code:** Use unit tests and edge cases.
- **Summarization:** Check atomic claims against source text.
- **Safety:** Apply the safety policy rubric.
- **RAG:** Check whether answer claims are supported by context spans.
- **Medical/Legal:** Use expert panel annotation; do not treat non-expert labels as final.
- **Instruction following:** Verify all constraints exactly.
- **Creative writing:** Apply the five-criterion rubric and report inter-annotator agreement.
- **Agent:** Verify subgoal completion from execution traces.

## Exclusion rule
Items below the required agreement threshold should be excluded from accuracy computation and reported separately as ambiguous/disputed items.
