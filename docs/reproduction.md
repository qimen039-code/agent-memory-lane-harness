# Local Reproduction

Run these commands from the repository root.

These checks are smoke tests for the reference package. Re-run the relevant
commands against the installed Codex version, Windows environment, PowerShell
runtime, and configured hook surface.

## GitHub Actions Smoke Workflow

`.github/workflows/smoke.yml` runs a lightweight subset of these checks on push, pull request, and manual dispatch:

- PowerShell policy, router, memory isolation, external research, runtime, tool-proxy, conversation-memory, and claim-gate smoke checks;
- Bash policy/router path smoke checks on Ubuntu, including paths with spaces and R5 context disambiguation;
- `cbh-doctor` read-only adoption diagnostics;
- TOML policy-authoring drift checks;
- pytest contract checks for automatically verifiable `TC-xxx` cases and machine-readable credits;

The workflow is intentionally not a full OS/runtime compatibility matrix. It is a low-cost guard that checks the reference package still runs and returns expected gate decisions.

For broader manual acceptance coverage, use [test-cases.md](test-cases.md). It includes route, claim, memory-lane, adapter, and shell-robustness cases.

## 0a. Adoption Doctor

`cbh-doctor` is a one-shot diagnostic. It does not install packages, configure
hooks, write memory, or certify that a host agent honors every path. It checks
the local reference package and reports pass/warn/fail with evidence.

```bash
python tools/cbh_doctor.py --repo-root . --json
```

Expected highlights:

- `status` is `pass` or `warn`;
- no check has `status: fail`;
- missing Bash or `jq` on a Windows-only machine appears as a warning, not as a package failure.

## 0b. Pytest Contract Checks

These tests code only the automatically verifiable subset of
[test-cases.md](test-cases.md). The Markdown file remains the readable contract
for humans and agents; pytest is the CI regression layer.

```bash
python -m pytest tests
```

Expected highlight:

- router contract cases keep their `TC-xxx` ids;
- `CREDITS.toml` parses and includes attribution boundaries.

## 0. Policy Authoring Check

```bash
python skills/embedded-harness/compile_policy_from_toml.py --check
```

Expected highlight:

- `status`: `pass`;
- `changed_tracked_paths`: `[]`.

## 0c. Policy Validator

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\validate_policy.ps1
```

Expected highlight:

- `status`: `pass`.
- `rule`: includes the lightweight `belief_trace_summary.current_status`
  invariant check when the repository root is available.

## 1. Intake Router

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "fix the script and run benchmark" -Cwd "C:\path\to\project"
```

Expected highlights:

- `project_lane`: `EXAMPLE_PROJECT`;
- `risk_level`: `R4`;
- `triggered_risks`: `R4`, `R3`;
- required gates include `change_contract_gate`, `external_research_gate`, `verification_gate`, and `claim_gate`.

## 2. Fallback Boundary

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "handle this project issue" -Cwd "C:\path\to\other"
```

Expected highlights:

- `classification_confidence`: `low`;
- `fallback_model_judgment_recommended`: `true`.

## 3. Memory Isolation

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_memory_isolation_gate.ps1 -ProjectLane EXAMPLE_PROJECT -RequestedPath "C:\path\to\project\.agent-memory\memory-item.md"
```

Expected highlight:

- `status`: `pass`.

## 3a. Memory Prefix Block

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_memory_isolation_gate.ps1 -ProjectLane EXAMPLE_PROJECT -RequestedPath "C:\path\to\project-evil\.agent-memory\memory-item.md"
```

Expected highlights:

- process exits with code `2`;
- `status`: `blocked`.

## 3b. Trigger Boundary And Negation

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "read installation guide" -Cwd "C:\path\to\other"
```

Expected highlight:

- `matched_risk_triggers` does not include `install`.

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "do not delete anything" -Cwd "C:\path\to\other"
```

Expected highlights:

- `risk_level` is not `R5`;
- `negated_risk_triggers` includes `delete`.

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "trigger list contains commit push 删除 提交, docs discussion only, no npm/pip distribution" -Cwd "C:\path with spaces\project"
```

Expected highlights:

- `risk_level` is not `R5`;
- `risk_candidates.R5` includes `commit`;
- `risk_context_decisions.R5.action_surface`: `documentation_or_discussion`.

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "提交报告" -Cwd "C:\path with spaces\project"
```

Expected highlights:

- `risk_level` is not `R5`;
- `risk_context_decisions.R5.action_surface`: `documentation_or_discussion`.

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "删除旧 release" -Cwd "C:\path with spaces\project"
```

Expected highlights:

- `risk_level`: `R5`;
- `risk_context_decisions.R5.promote_to_risk`: `true`;
- `approval_required` includes `high_risk_action`.

## 4. External Research Trigger

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_external_research_gate.ps1 -TaskText "check latest package version 1.2.3 on GitHub"
```

Expected highlight:

- `needs_external_research`: `true`.
- `recommended_search_modes` includes `github_open_source_repository_search` and `official_authority_source_search`.
- `external_retrieval_receipt.schema`: `cbh.external_retrieval_receipt.v1`.
- `external_retrieval_receipt.network_access_performed`: `false`.

Run the cross-source regression matrix without network access:

```powershell
pwsh -NoProfile -File .\tests\test_external_retrieval_strategy.ps1
python -B -m pytest .\tests\test_external_retrieval_strategy.py
```

The matrix covers DOI/RFC/CVE/arXiv/standards, PyPI/npm/Hugging Face/GitHub,
unknown namespaces, currentness, multi-target binding, source-native fallback,
and the rule that provider misses do not establish absence.

## 4-1. External Research Negation

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_external_research_gate.ps1 -TaskText "do not search GitHub"
```

Expected highlights:

- `needs_external_research`: `false`;
- `negated_triggers` includes `GitHub`;
- `recommended_search_modes`: empty.

## 4a. Source-Grounded Learning Route

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_external_research_gate.ps1 -TaskText "learn from an open source mechanism and avoid closed-door invention"
```

Expected highlights:

- `needs_external_research`: `true`;
- `recommended_search_modes` includes `github_open_source_repository_search` and `source_grounded_learning_intake`;
- `learning_classification_labels` includes `source_prior`, `hypothesis`, `inspiration`, `unverified_implementation_path`, and `not_applicable`.

## 4b. Governance Rule Update Route

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "refine the dynamic evaluation decision layer and update routing triggers" -Cwd "C:\path\to\project"
```

Expected highlights:

- `risk_level`: `R3`;
- `matched_risk_triggers` includes `dynamic evaluation`, `decision layer`, or `trigger rule`;
- required gates include `project_context_gate`, `change_contract_gate`, and `claim_gate`.

## 4b-1. Composite Scope Reassessment Route

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "read this report and also update public docs and test cases from it" -Cwd "C:\path\to\project"
```

Expected highlights:

- `risk_level`: `R3`;
- `semantic_ambiguity` includes `composite_or_scope_reassessment`;
- required gates include `scope_reassessment_gate` and `change_contract_gate`.

## 4c. Behavior-Correction Profile Inventory

```powershell
python -B .\skills\embedded-harness\behavior_correction_gate.py --list-profiles
```

Expected highlights:

- `status`: `pass`;
- `host_blocking`: `false`;
- `profile_count` is greater than zero.

## 4c-1. Local Architecture Maintenance Should Not Force External Research

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "update the local architecture chain and optimize routing logic" -Cwd (Get-Location).Path
```

Expected highlights:

- `risk_level`: `R3`;
- `needs_external_research`: `false`.

## 4d. Nonblocking Correction Regression

```powershell
python -B -m pytest -q tests/test_nonblocking_runtime_contract.py
```

Expected highlights:

- the known PowerShell `foreach {...} | ...` regression produces a verified rewrite;
- unmatched input is a silent no-op;
- the old wrapper/proxy/runtime scripts remain absent.

## 4e. Conversation Memory Route

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "checkpoint this conversation so we can continue this conversation later" -Cwd "C:\path\to\other"
```

Expected highlights:

- `conversation_memory_decision`: `create_or_update_current_conversation`;
- `memory_lane`: `current_conversation`;
- `memory_mode`: `write`;
- `record_intent`: `explicit_conversation_memory_request`.

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "README VERSION CHANGELOG tests adapter repository release long conversation" -Cwd "C:\path\to\other"
```

Expected highlights:

- `projectization_decision`: `emergent_project_candidate`;
- `conversation_memory_decision`: `none`;
- projectization review takes precedence over conversation checkpointing.

## 4f. Static Knowledge Layer Route

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_intake_router.ps1 -TaskText "read the project manual and module map before editing" -Cwd "C:\path\to\project"
```

Expected highlights:

- `memory_need`: `index_only`;
- `module_need` includes `static_knowledge_index`;
- `required_gates` includes `static_knowledge_index_gate`;
- selected static notes remain `source_prior` until checked against local files,
  tests, or other evidence.

## 5. Claim Schema

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\embedded-harness\harness_claim_schema_verifier.ps1 -ClaimJson '{"claim_type":"architecture_decision","source_type":"local_file","source_ref":"README.md","evidence_boundary":"whiteboard_smoke"}'
```

Expected highlight:

- `status`: `pass`.

## 6. Bash Smoke Checks

Run these only when Bash and `jq` are available.

```bash
bash ./skills/embedded-harness/bash/validate_policy.sh
bash ./skills/embedded-harness/bash/harness_intake_router.sh --task-text "do not delete anything" --cwd "/path/to/other"
bash ./skills/embedded-harness/bash/harness_external_research_gate.sh --task-text "do not search GitHub"
```

Expected highlights:

- policy validator returns `status: pass`;
- intake router records the negated `delete` trigger without direct `R5`;
- external research gate returns `needs_external_research: false`.


## Notes

These checks prove that the public runtime core and reference functions return
expected routing decisions. They do not establish that a particular client
loads or honors every surface; fresh-task lifecycle evidence is required for
that claim.
