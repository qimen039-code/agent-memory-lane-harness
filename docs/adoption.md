# Adoption Guide

Use this guide to adapt the public runtime core to your own model-agent environment.

ACCF is an assistance layer inside the host agent loop, not a standalone task
engine. Preserve the host model as the owner of planning, semantic decisions,
tool use, recovery, and the final response.

## Step 1: Choose The Instruction Entry

Every agent has a different way to load workspace rules. Map `AGENTS.md` into the file or settings surface that your agent actually reads.

Do not add product-specific adapter files to the shared core unless you want to maintain that adapter.

## Step 2: Configure Project Lanes

Use two policy editing surfaces:

- edit `skills/embedded-harness/embedded_harness_policy.authoring.toml` for
  high-churn trigger, R5 context, full-lane threshold, and one-event
  authorization-boundary sections;
- keep public `skills/embedded-harness/embedded_harness_policy.json` free of
  private machine-local project roots;
- put private project lanes and memory roots in
  `skills/embedded-harness/embedded_harness_policy.local.json`, or point
  `CBH_PROJECT_LANES_FILE` at a private overlay file.

```bash
python skills/embedded-harness/compile_policy_from_toml.py --check
```

Use `--output skills/embedded-harness/embedded_harness_policy.json` only when
you deliberately want to regenerate the runtime JSON from the TOML-maintained
sections. Runtime adapters should not parse TOML directly.

Then copy `templates/project/memory-library` into the project memory root and keep the layered layout:

```text
_META_INDEX.md
governance/_INDEX.md
memory_hierarchy/_INDEX.md
external_references/_INDEX.md
raw_logs/_INDEX.md
```

Do not collapse the library into one large summary file. The point of the meta index is to select the category first, then open only the relevant category index and capsule.

For existing instruction, memory, config, or policy files, adopt a local-patch default. Ordinary change/update/fix/sync/adapt requests should edit only the necessary anchored section. Full-file rewrites require explicit user intent and a review of what state, comments, non-ASCII paths, private entries, or generated metadata could be lost. Use [edit-operation-contract.md](edit-operation-contract.md) to classify append, patch, section replacement, new artifact, supersession, archive, full rewrite, and deletion boundaries.

Make this lookup order mandatory in the adopting agent instructions:

```text
_META_INDEX.md or equivalent meta summary
-> one category index
-> one matching capsule
```

If the agent cannot confirm that it read the meta layer first, treat the memory result as incomplete rather than authoritative.

Use [memory-meta-index-contract.md](memory-meta-index-contract.md) as the recommended field shape. The important part is not the exact Markdown formatting; it is the ability to select by lane, scope, category, record type, status, retrieval terms, applicability, linked modules, linked records, and review freshness before opening a payload.

For long-running conversations that are not yet project lanes, use [conversation-memory-lane.md](conversation-memory-lane.md), [memory-linking-contract.md](memory-linking-contract.md), and `templates/conversation-memory/`. Conversation memory is isolated by thread/session, follows the same meta-first rule, and should not silently write into project or global memory. New conversations continue old ones through link-only edges by default; explicit merges create a new merged memory.

When the host exposes raw session logs, add
[conversation-ledger-contract.md](conversation-ledger-contract.md) and
`templates/conversation-ledger/` between raw logs and memory lanes. For Codex
Desktop JSONL, `python .\skills\embedded-harness\codex_session_ledger.py`
creates the derived session, turn, segment, time-anchor, link, and evidence-ref
ledgers without modifying the raw logs.

If your project needs a stable manual for agents, copy
`templates/static-knowledge-layer/` into the project and fill only the pages that
are useful. This layer is for module maps, entry points, commands, conventions,
and interface notes. It is read through `_STATIC_KNOWLEDGE_INDEX.md` first and
should remain `source_prior` until the agent checks the referenced files, tests,
or schemas. See [static-knowledge-layer.md](static-knowledge-layer.md).

Use [format-layering.md](format-layering.md) when deciding whether a record belongs in Markdown, JSON, JSONL, CSV/TSV, or a queryable local store. Public explanations can stay in Markdown; machine-owned routing facts and append-only records should use structured formats.

Use [cost-control-contract.md](cost-control-contract.md) to keep the active context small. Default execution should use compact receipts, action-relevant fields, delta receipts after re-evaluation, and at most one meta index plus one category index plus a small number of payloads.

Use [archive-and-persona-boundaries.md](archive-and-persona-boundaries.md) before adding cold archive or persona behavior. Global archives are optional cold indexes, and persona state is conversation-only by default.

## Step 3: Register The Skill Folders

If your agent supports skills or commands, register these folders:

- `skills/embedded-harness`;
- `skills/troubleshooting-skill-matrix`;
- `skills/agent-error-memory`;
- `skills/bug-solution-memory`;
- `skills/shared-semantic-anchors`.

If your agent does not support skills, keep them as normal workspace files and reference them from the root instruction entry.

## Step 4: Wire Runtime Checks

At minimum, run the intake router before nontrivial work.

When routing selects memory, pass `memory_source_hints` to
`skills/embedded-harness/harness_action_consumer.py` (or a compatible host
consumer) and inject only its bounded `additional_context` into the model's
planning turn. Exact indexed anchors stay selected even when a compound prompt
also produces weaker candidates. Weak-only candidate sets are included as
bounded model-semantic-review context, so the model can select them without a
manual file down-drill. The consumer does not execute the task.

Stronger setups can run:

- memory isolation before reading or writing project memory;
- external research gate before current source claims;
- claim schema verifier before final strong claims;
- high-risk checks before tool calls.

When routing selects external research, the model agent—not a ACCF background
worker—calls the available source tools and records citations or a source
ledger before making current or strong claims.

Also make the model-layer pre-action control plane mandatory:

1. Create a lightweight routing receipt for nontrivial work: task type, target surface, audience, lane, risk, semantic ambiguity, module need, skill lifecycle profile, feedback loop profile, memory need, memory mode, memory lane, record intent, external need, claim risk, projectization decision, conversation memory decision, link intent, receipt profile, and required gates.
2. Re-evaluate only after trigger events: new evidence, missing files, tool errors, scope changes, user corrections, cross-project terminology, currentness/version claims, GitHub/open-source mechanism intake, risk/cost escalation, strong claims, R5 actions, or memory writes.
3. Final-check claim scope, memory scope, version metadata, and unresolved verification debt.

4. When a protected high-risk action is identified, stop before forming or
   calling the executable tool action. Resume only after exact human
   authorization for one concrete event, one declared scope, and one use. A
   later or materially changed risky action requires a new authorization. The
   operator accepts the disclosed risk for the authorized operation; ACCF does
   not certify it as safe or assume responsibility for its consequences.

When a self-check finds memory pollution, target pollution, dirty-tree debt, or
technical debt, route `debt_hygiene_gate`: group issues, clean the must-fix set,
and mark acceptable deferrals as `candidate_technical_debt`. This does not
authorize deletion, reset, or full rewrites.

For local single-user adapters, including Codex-style local harness installs, keep R0-R5 classification internal and silent by default.
Start with no visible receipt for ordinary work, use `compact_runtime` only when a boundary changes the next action, expand to `extended_governance` only when public/private boundaries, framework rules, adapters, project memory, memory writes, conversation-link decisions, semantic ambiguity, or projectization drift appear, and use `debug_receipt` only for router troubleshooting or explicit audit requests.

Do not make this expensive by default. The control plane should choose the cheapest sufficient route and should not wrap every tool call.

Use [router-decision-contract.md](router-decision-contract.md) as the field contract for router and dynamic-decision adapters. The contract can be implicit for obvious low-risk work, but should be explicit for R3 or higher work, public-facing changes, memory writes, high-risk actions, and audited decisions.

When adapting the harness into a concrete runtime, use [declarative-governance-contract.md](declarative-governance-contract.md) and `templates/adapter-contract/governance.contract.json` to declare the minimum adapter promises:

- which stages exist;
- which stage provides active routing before planning;
- which stage can block protected tool execution;
- which optional rewrite protocol and permission semantics the host actually supports;
- which payload-safety guarantees exist;
- which receipt profile is the default.

Keep this contract small. It should not cause ordinary R0/R1 work to load all memory, all skill files, all tool schemas, or all external sources.

Use [memory-routing-contract.md](memory-routing-contract.md) when wiring memory writes. Start with common error corpus records for small reusable mistakes, including the applied solution and validation, and upgrade to paired ERR/SOL records only when the issue is explicit, high-impact, or repeated.

For conversation-memory continuation, merge, archive, or cross-conversation update requests, resolve the link decision through meta-first lookup before acting. This remains a model/host governance boundary, not a behavior-correction denial.

For optional nonblocking correction, use only these entry points:

```text
profile receipt -> skills/embedded-harness/behavior_correction_gate.py
verified current-input rewrite -> skills/embedded-harness/behavior_correction_hook.py
memory/action context -> skills/embedded-harness/harness_action_consumer.py
```

The correction hook returns `allow + updatedInput` only for an accepted deterministic profile and silent no-op otherwise. It does not own R5 confirmation or final-answer authorization.

Claim payloads should use enumerated `source_type` and `evidence_boundary`
values from `embedded_harness_policy.json`. Source-backed claims such as
`local_file`, `local_test`, `tool_output`, `external_retrieval`, and
`memory_capsule_ref` should include `source_ref`. Strong wording such as
validated, verified, stable, or proven requires an evidence boundary at least as
strong as the policy's `strong_claim_evidence_boundaries`.

Do not replace your normal agent launcher. Start with the decision router and
validators; enable optional correction only after the exact host protocol is
verified. The model-layer pre-action stop does not require a deny-capable hook,
but any claim of independent execution-time blocking does. Keep a fallback path
so a bad adapter can be disabled without losing workspace access.

Exit code contract:

- `0`: gate passed, or returned a non-blocking status.
- other: standalone diagnostic/runtime error, missing dependency, malformed input, or adapter failure.

Status contract:

- `pass`: no blocking issue found.
- `correction_candidate`: a current candidate matched and declares its verifier.
- `cross_reference_allowed`: memory path is outside the active lane but was explicitly allowed as a cross-reference.

For Bash environments, use the scripts under `skills/embedded-harness/bash`. They require `jq` and share the same `embedded_harness_policy.json`.

Integration validation is local by default. Run the profile, policy, hook, and
fresh-task checks against the installed Codex version before reporting a
capability as active.

For runtime/client compatibility, maintain a small manifest using [version-compatibility-management.md](version-compatibility-management.md) and `templates/adapter-contract/compatibility.manifest.json`. Refresh it only after adapter install, client update, hook or wrapper edits, failed smoke tests, or explicit user request.

Before calling a deployment active, check the broader deployment failure modes in [deployment-risk-patterns.md](deployment-risk-patterns.md). Repository presence is not host invocation evidence.

## Step 4a: Configure Search And Learning Routes

Tune `search_and_learning_decision_matrix` and `external_research_triggers` in `skills/embedded-harness/embedded_harness_policy.json`.

Use separate routes for:

- official or authority source checks for drift-prone public facts;
- GitHub or open-source repository inspection for repository claims and reuse boundaries;
- general web cross-checks for ecosystem context and uncertain public claims;
- source-grounded learning intake for external mechanisms and external architecture comparison;
- local validation before claiming adoption, success, performance, or compatibility.

Use the external gate and `external_retrieval_strategy.py` before search tool
execution. Preserve the original query and exact identifiers, use the matching
canonical/source-native route for typed objects, discover unknown namespaces
before guessing a provider, and bind facets and evidence to each target. Feed
attempt receipts back into the task-local reducer when available. Do not turn
one provider/index miss into absence, or a plan into evidence that browsing
already occurred.

For external mechanism intake, write a compact source ledger before adapting anything:

```text
source
date checked
claim or mechanism
classification label
applicable boundary
non-applicable boundary
risk
validation path
adoption decision
```

Recommended labels are `fact`, `source_prior`, `hypothesis`, `inspiration`, `unverified_implementation_path`, `not_applicable`, and `local_validated`. Reserve `local_validated` for evidence produced in the adopting workspace.

The external evidence boundary is semi-automatic: when the router sees current
facts, GitHub/open-source mechanisms, "has anyone built this" questions, or
explicit uncertainty such as "not sure" / "需要外部证据", the host should search
official, GitHub, or cross-check sources before making a strong claim. If the
host cannot search, the final answer must mark the claim unverified or source
limited instead of silently relying on internal discussion.

## Step 5: Keep The Core Clean

The public runtime core should not contain private project content. Add project rules, real memory capsules, and solved incident records inside the adopting project only.

Use the public demo records as shape examples only. They are synthetic and are not claims about your environment.

For local routing, use a private project-lane overlay:

```json
{
  "schema": "cbh.project_lane_overlay.v1",
  "project_lanes": {
    "YOUR_PROJECT": ["C:\\path\\to\\your-project"]
  },
  "memory_roots": {
    "YOUR_PROJECT": [
      "C:\\path\\to\\your-project\\.agent-memory",
      "C:\\path\\to\\your-project\\memory-bank"
    ]
  }
}
```

Store it as `skills/embedded-harness/embedded_harness_policy.local.json` for a
single checkout, or set `CBH_PROJECT_LANES_FILE` to a private path. This lets
the router preserve concrete cwd project evidence without committing local
paths into the public package.

## Step 6: Keep Versions In Sync

When publishing changes to an adopted copy or fork, update the version metadata in the same change:

- `VERSION`;
- `CHANGELOG.md`;
- any README line that displays the current version.

Use `vMAJOR.MINOR.PATCH` labels. For early framework work, keep `MAJOR` at `0` until the layout and adoption contract are stable.

## Project Lane Isolation

For multi-project use, create one lane per project through the local overlay
and one registry entry per project in `PROJECT_SKILL_MATRIX_REGISTRY.md`.

Each lane should have its own:

- project instruction entry;
- memory roots;
- optional project router;
- incident records;
- retrieval log.

Shared rules should stay in the public runtime core. Project-specific rules should stay inside the project lane. This keeps separate projects usable across new conversations without mixing unrelated memory, progress, or failure records.

Conversation memory should stay separate from project lanes. A conversation memory lane may reference a project record, but it should not copy project payloads or write project memory unless the user explicitly asks for a project-lane update.

Global archive should stay separate from active lanes. Archive by moving or copying source files/directories by default. Use compressed summary capsules only after explicit compression, migration, de-identification, public-release, or storage-reduction intent. Do not delete source files unless separately confirmed.

Persona state should stay inside the current conversation. It may affect tone or pacing, but it must not affect facts, verification, risk, project boundaries, memory boundaries, search, claim gates, or tests.

## After Agent Client Updates

Agent clients may change executable locations, bundled runtime paths, skill discovery behavior, or hook launch environments across releases. After a client update, re-run the local smoke checks before trusting the chain.

Recommended update check:

1. Confirm the root instruction entry is still loaded.
2. Confirm the intake router still runs.
3. Confirm skill or command folders are still discoverable.
4. Confirm hook or wrapper paths still point to existing files.
5. Confirm project memory roots still pass the isolation gate.
6. Run one mixed-risk route, one memory check, one source-check trigger, and one claim check.

If an agent supports wrapper scripts, keep a small client-health script near the adapter layer. That script should detect path drift and report issues first. Automatic repair should be opt-in because client config files are part of the user's local environment.

## Non-Goals

Before expanding the framework, review [non-goals.md](non-goals.md). Package-manager distribution, broad dashboards, promotion work, large comparison tables, and full test matrices are intentionally excluded from the public runtime core.
