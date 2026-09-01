# Research Triage Three Questions

This contract is a method-selection gate. It does not answer a research
question by itself. It decides whether a question should be treated as a search
for an objective verifier, a mechanical-evaluator design problem, or a
governance problem for irreducible uncertainty.

Use it before proposing target functions, reinforcement-learning loops,
automated evaluators, semantic gates, causal evaluators, benchmark claims, or
claims that a system can self-correct toward an objective optimum.

## The Three Questions

1. Does this task type have an external verification signal?

   Ask whether the claim or task has a verifier that is independent of human
   preference and does not loop back into the model's own output. Mathematical
   proof checking, code execution, exact anchor comparison, and reproducible
   measurement can have such signals. Open-ended factual synthesis, causal
   attribution, semantic judgment, memory recall for an unknown point, and value
   judgment often do not.

2. If a signal exists, is it a mechanical judge or human judgment wrapped in a
   technical surface?

   A mechanical judge is executable, inspectable, and repeatable without
   smuggling in a new semantic decision. Red flags include rubrics that require
   human interpretation, model agreement used as truth, preference labels, or a
   "score" that depends on another unverified language judgment.

3. If no independent verifier exists, what governance structure should manage
   the uncertainty?

   Do not keep searching for a single objective function when the task class
   lacks one. Route the work through explicit uncertainty labels, evidence
   windows, source boundaries, causal-attribution limits, external-source
   checks, memory provenance, and review gates.

## Route Outcomes

| Outcome | Use when | ACCF behavior |
| --- | --- | --- |
| `mechanical_verifier_path` | An independent verifier exists and is inspectable. | Use tests, proof checks, exact comparison, reproducible measurement, or a small evaluator. |
| `verifier_audit_path` | A proposed verifier exists but may hide semantic or preference judgment. | Audit the evaluator source, labels, rubric, scorer, and failure cases before using it as a target. |
| `governance_path` | No independent verifier exists for the task class. | Use claim boundaries, uncertainty labels, causal levels, source-preserving memory, and external evidence checks. |
| `mixed_path` | The task has mechanical subparts and non-mechanical judgment subparts. | Split the task: automate verifiable parts and govern semantic or causal parts. |

## Trigger Boundary

Trigger this gate when a task asks about:

- target functions, objective optima, or self-correction loops;
- reinforcement learning or evaluator design for language, memory, causality, or
  semantic claims;
- whether a benchmark, score, judge, or reward is truly objective;
- whether a mechanism should be trained into model weights or governed outside
  the model;
- whether a research line should continue as "find a function" or shift to
  evidence governance.

Do not trigger it for ordinary implementation tasks, direct factual lookup,
simple tests, or local debugging unless the user is choosing the evaluator or
research route itself.

## Boundaries

- This gate does not prove that a verifier is valid. It only routes the next
  evidence demand.
- A mechanical-looking score is not automatically mechanical evidence.
- Human or model preference labels can be useful training data, but they are not
  objective verification by themselves.
- Governance is not failure. For non-mechanical claim classes, explicit
  uncertainty management is the correct engineering path.

## Related Contracts

- [router-decision-contract.md](router-decision-contract.md)
- [content-reading-contract.md](content-reading-contract.md)
- [memory-feedback-loop-trial.md](memory-feedback-loop-trial.md)
- [source-monitoring-memory-schema.md](source-monitoring-memory-schema.md)
