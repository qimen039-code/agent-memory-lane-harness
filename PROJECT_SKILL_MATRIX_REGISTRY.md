# Project Skill Matrix Registry

A compact index that routes the agent to project-specific skill matrix routers. Keep this file small; put detailed behavior inside each project router skill.

## Default Flow

```text
root AGENTS.md
-> embedded harness intake router
-> mandatory model-layer pre-action control plane
-> this registry
-> project router or project AGENTS
-> memory meta summary, category index, and matching capsule only when needed
-> executable gates only when needed
```

## Mandatory Memory Retrieval Chain

Memory lookup must follow this order:

```text
meta summary / _META_INDEX / router manifest
-> category index / point index / outer_retrieval_surface
-> matching capsule or paired point payload
```

Do not open deep memory files, all project notes, or all incident payloads before the meta/index layer has routed the request. If a project is still flat, treat its top-level index as the temporary meta layer and record that the project memory layout should be upgraded.

## Mandatory Model-Layer Pre-Action Control Plane

Nontrivial tasks must run the control plane before loading project-specific context, during execution when trigger events appear, and before final output. It should not wrap every tool call by default.

Protected high-risk actions are different from ordinary tool calls: once the
route identifies one, the model must stop before forming or calling the
executable action until exact human authorization exists. Authorization is
one-event, one-scope, and one-use; a later or materially changed risky action
requires a fresh stop. This model-layer stop remains mandatory even when the
host has no independent deny-capable tool hook.

Required decisions:

- task type and active lane;
- current risk level and escalation triggers;
- whether project instructions, a project router, memory retrieval, existing skills/tools/plugins, external research, claim gates, or human confirmation are needed.

The control plane should compute routing internally on every nontrivial task. R0-R5 labels stay silent by default; expose a compact runtime receipt only when the decision changes execution path, cost, permission, memory, external search, or claim boundary.
Full fields are task type, target surface, audience, project lane, risk level, semantic ambiguity, module need, memory need, memory mode, memory lane, record intent, external need, claim risk, projectization decision, receipt profile, and required gates.

Receipt profiles: `compact_runtime` for ordinary local execution and single-agent adapters; `extended_governance` for public docs, local harness, adapter, project memory, semantic ambiguity, memory write, or projectization boundary work; `debug_receipt` for router diagnosis and full receipt debugging.

Runtime trigger events include new evidence, missing files, tool errors, scope changes, user corrections, cross-project terminology, currentness/version claims, GitHub/open-source mechanism intake, cost escalation, risk escalation, strong claims, R5 actions, and memory writes.

Use the cheapest sufficient route. Do not load all project memory, all skills, all history, or wrap every tool call just because this governance layer is active.

Memory recording is routed separately from memory reading. Explicit "record this error" requests go to the self-reflection matrix or common error corpus; small reusable mistakes go to common error-and-solution records first; full ERR/SOL pairs are for high-impact, repeated, or explicit incidents.

Reusable memory capsules use source-monitoring fields: `source_tag` `belief_status` `confidence` `derived_from` `source_monitoring` `belief_trace_summary`. Treat optional numeric scores as adapter metadata, not as a replacement for evidence basis and provenance.

Governance-layer updates, dynamic-evaluation rule changes, routing-rule changes, trigger-term updates, decision-matrix edits, and framework behavior changes are `R3` even when they are documentation-only. A missed route should be fixed with the narrowest reusable trigger term rather than a broad catch-all.

Trigger terms should be promoted only when they represent a durable routing class: recurring, cross-task, boundary-changing, and not already covered by an existing generic edit/report/search/memory rule. One-off wording for a single documentation request should stay in the task receipt or changelog, not in the long-lived policy.

## Nonblocking Behavior Correction Layer

Known mechanically recognizable recurrence shapes may be reviewed immediately before a tool action:

```text
profile inventory / advisory receipt -> behavior_correction_gate.py
verified current-input rewrite -> behavior_correction_hook.py
memory-selected task-local receipt -> harness_action_consumer.py
```

Only an accepted deterministic profile may return `allow + updatedInput`; ambiguity, verifier failure, unavailable host protocol, or no match is a silent no-op. This layer does not own authorization or denial.

## Mandatory Search And Learning Decision Matrix

When a task needs public facts, open-source repository evidence, external mechanism learning, or anti-closed-door-invention review, choose the appropriate search and learning route:

| Route | Use when | Required boundary |
| --- | --- | --- |
| Official / authority source search | product, institution, policy, law, price, version, release date, named role, or other drift-prone public fact | Prefer official or authority sources first, then cross-check when practical. |
| GitHub / open-source repository search | repository, release, issue, license, changelog, source tree, project activity, examples | Separate README claims, source-code facts, release/issue evidence, and license boundaries. |
| General web cross-check | ecosystem trend, mechanism comparison, third-party guide, community experience, or uncertain public claim | Use independent sources when practical; mark source limits when not. |
| Source-grounded learning intake | external mechanism, external architecture comparison, learn-from-open-source work, or anti-closed-door-invention task | Build a source ledger and classify material as fact, source_prior, hypothesis, inspiration, unverified implementation path, or not_applicable. |
| Local validation route | adopting a mechanism, making a strong claim, or reporting success | Do not upgrade to locally validated without local files, scripts, tests, reproduction, or a concrete evidence chain. |

Outside material can supply completion ideas, boundary control, engineering constraints, validation methods, failure lessons, or non-applicable examples. It must not replace the active project objective or be presented as local validation by itself.

## Native Skill / Plugin / Connector Discovery Layer

Codex-native skills and installed plugins are not always callable until the
current turn exposes them through the skill list, `tool_search`, MCP/app tools,
or an explicit user mention. When the task depends on a platform object or a
specialized client capability, run a cheap discovery pass before falling back
to shell, raw web, clone, or manual download.

| Object / capability | Preferred discovery route | Fallback boundary |
| --- | --- | --- |
| GitHub repo, file, issue, PR, release, Actions log/artifact | Discover GitHub MCP/app tools first; use direct file/log/artifact tools when available | Shell `git`/`gh` or web only after plugin surface is missing, blocked, or insufficient for the needed local write |
| Hosted or SaaS platform objects | Discover the named plugin/connector first when one exists | General web or shell only after `checked_missing`, `checked_blocked`, or local filesystem execution is the actual target |
| PDF, documents, spreadsheets, presentations, templates, OpenAI docs, skill/plugin creation or install | Use the Codex native/system or primary-runtime skill listed for the turn | Shell only when the native skill cannot read/write the needed local artifact or the task is a build/test/edit step |
| Browser, Chrome, Computer Use | Prefer Browser/Chrome/node_repl control when available; Computer Use only when the user names it or lighter browser paths are insufficient | Screenshots/OCR/manual UI only after lighter browser surfaces fail |
| Local build/test/edit, filesystem copy, Windows config, large local repo clone | Shell/local tools | Plugin discovery is optional unless a platform API object is also part of the task |

Record the internal decision as `tool_surface_need`,
`tool_discovery_status`, `skill_or_tool_need`, `plugin_need`, and
`preferred_call_surface`. Show it only in extended/debug receipts or when it
changes the action path.

## Registered Routers

| Scope | Path or trigger | Router skill / file | Status | Notes |
| --- | --- | --- | --- | --- |
| Shared troubleshooting | agent errors, tool failures, skill matrix updates, reusable incidents | `skills/troubleshooting-skill-matrix/SKILL.md` | active | Routes to semantic anchors and paired ERR/SOL ledgers. |
| Embedded harness | nontrivial task intake, direct-outcome-first routing, memory isolation, external research trigger, claim schema, policy validation | `skills/embedded-harness/README.md` | active | Low-cost deterministic entry route; PowerShell and the Codex hook surface expose the direct-outcome action contract. |
| Example project | `<PROJECT_ROOT>`, `EXAMPLE_PROJECT` | `<PROJECT_ROOT>/AGENTS.md` or a future project router skill | template | Replace with real project details after adoption. |

## Project Router Manifest Contract

Each project router should declare:

- scope
- capabilities
- permission declaration
- risk level and escalation triggers
- default invocation mode
- human-confirmation requirements
- linked point sets
- memory meta summary and category index roots
- external mechanism intake rules
- provenance and rollback policy for executable content
