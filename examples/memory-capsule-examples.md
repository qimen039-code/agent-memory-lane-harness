# Memory Capsule Examples

These examples are synthetic. They show record shape only. Replace every lane, path, title, and validation note after adoption.

## Project Memory Capsule

```text
## MEM-EXAMPLE-ROUTING-001

status: template_example
lane: EXAMPLE_PROJECT
point_kind: project_memory_capsule
source_tag: inferred_synthesis
belief_status: bounded_claim
purpose_anchor: Keep project routing and memory boundaries reusable across conversations.
meaning_anchor: The agent should read only the active project memory unless the user explicitly asks for cross-project synthesis.
outer_retrieval_surface:
  - project lane
  - memory isolation
  - root instruction reload
source_boundary: Synthetic example only.
evidence_boundary: Not a validation result.
confidence:
  label: medium
  basis: Status assigned as bounded_claim because this is a synthetic framework example with explicit scope, not a local runtime validation record.
lifecycle:
  stage: capsule
  retention_policy: preserve
  last_accessed_at: YYYY-MM-DDTHH:MM:SSZ
  promotion_reason: Template shows a reusable project-routing memory shape.
  decay_reason: null
derived_from:
  - type: source_note
    ref_id: TEMPLATE-SOURCE-001
    relationship: synthesized_from
    inherited_boundary: template_only
source_monitoring:
  observation_state: resolved
  trigger_reason: manual_review
  last_checked: YYYY-MM-DDTHH:MM:SSZ
belief_trace_summary:
  initial_status: hypothesis
  current_status: bounded_claim
  intermediate_steps_count: 1
  archived_trace_ref: none
content_summary: A project lane owns its instructions, progress notes, and incident records. Other lanes are not read or written unless explicitly requested.
applicable_boundaries:
  - current project tasks
  - new conversation continuation
  - local instruction reload
non_applicable_boundaries:
  - unrelated project strategy
  - private records from another lane
  - global rule changes without user confirmation
review_rule: Keep the capsule short. Move details into project files only when they are user-confirmed.
```

## Paired Agent Error Record

```text
## ERR-EXAMPLE-CLIENT-DRIFT-001

status: template_example
point_kind: agent_error_solid_point
purpose_anchor: Prevent silent harness disablement after an agent client update.
meaning_anchor: Updated clients can move launchers, bundled runtimes, hook folders, or skill loading paths.
outer_retrieval_surface:
  - client update
  - missing launcher path
  - hook not firing
  - skill folder not loaded
event_summary: After a client update, a previously valid adapter path no longer existed.
agent_fault: The agent trusted the old adapter path without checking the current client surface.
why_it_was_wrong: The harness looked installed but was not being reached by the running client.
impact: Route gates and memory gates could be skipped silently.
evidence: Synthetic example only.
applicable_boundaries:
  - agent client updates
  - wrapper path drift
  - hook path drift
non_applicable_boundaries:
  - tasks that do not depend on local adapters
paired_solution_ids:
  - SOL-EXAMPLE-CLIENT-DRIFT-001
prevention_rule: After a client update, run adapter discovery and smoke tests before relying on the harness.
not_to_repeat: Do not assume old launcher, hook, or skill paths still work.
```

## Paired Solution Record

```text
## SOL-EXAMPLE-CLIENT-DRIFT-001

status: template_example
point_kind: bug_solution_solid_point
purpose_anchor: Restore harness reachability after client path drift.
meaning_anchor: Adapter verification should be cheap, repeatable, and separate from project memory.
outer_retrieval_surface:
  - adapter smoke test
  - client update check
  - hook path verification
problem_class: agent_client_update_drift
solution_summary: Re-discover the active client launcher, runtime, command folders, hook folders, and skill folders, then run routing and memory-gate smoke tests.
investigation_order:
  - identify current client version
  - list current launcher and runtime paths
  - verify root instruction loading
  - verify skill or command folder loading
  - run intake router and memory isolation gate
fix_path: Update adapter paths only after the new paths are confirmed.
rollback: Restore the previous adapter config from backup if the new config fails.
validation:
  - intake router returns expected mixed-risk route
  - memory isolation gate allows project path and blocks unrelated path
  - claim verifier accepts a complete claim record
caveats: Synthetic example only. Each runtime needs its own adapter check.
applicable_boundaries:
  - Codex with verified local adapter paths
non_applicable_boundaries:
  - environments without the referenced local paths
paired_error_ids:
  - ERR-EXAMPLE-CLIENT-DRIFT-001
future_reuse_rule: Convert repeated update failures into one project-neutral adapter check, not many overlapping skills.
references: none
```

## Claim Boundary Record

```text
{
  "claim_id": "CLAIM-EXAMPLE-001",
  "claim_text": "The harness continued to route a new conversation through the configured chain.",
  "claim_type": "field_use_note",
  "source_tag": "local_test",
  "belief_status": "bounded_claim",
  "source_type": "local_smoke",
  "evidence_boundary": "Example shape only. Replace with your own smoke output.",
  "confidence": {
    "label": "medium",
    "basis": "Status is bounded_claim because the example requires local smoke output but this public record is synthetic."
  },
  "lifecycle": {
    "stage": "capsule",
    "retention_policy": "until_superseded",
    "last_accessed_at": "YYYY-MM-DDTHH:MM:SSZ",
    "promotion_reason": "Synthetic claim-boundary example promoted from a smoke-test shape.",
    "decay_reason": null
  },
  "derived_from": [
    {
      "type": "test_result",
      "ref_id": "TEST-EXAMPLE-001",
      "relationship": "extends"
    }
  ],
  "source_monitoring": {
    "observation_state": "resolved",
    "trigger_reason": "manual_review",
    "last_checked": "YYYY-MM-DDTHH:MM:SSZ"
  },
  "not_claimed": [
    "universal compatibility",
    "hard security enforcement",
    "tested on every operating system"
  ],
  "required_followup": [
    "re-run after client update",
    "re-run after adapter path changes"
  ]
}
```

## Bounded Skill Addition Decision

```text
Decision: do not create a new active skill.

Reason:
- The knowledge is useful but does not need a new execution capability.
- A new skill would overlap with the existing troubleshooting route.
- The material can live in a knowledge pack and be routed by retrieval surface.

Allowed storage:
- project memory capsule
- paired error and solution records
- reference pack
- examples folder

Escalate to a new skill only when:
- the task repeats often;
- the execution steps are stable;
- the scope is narrow;
- the non-applicable boundary is clear;
- the user or maintainer confirms adoption.
```
