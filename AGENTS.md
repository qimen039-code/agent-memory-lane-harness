# Root Agent Microkernel

Use this file as the always-on, low-cost front door before loading large histories, memories, or project-specific rules.

This is a generic foundation file. It does not contain project-specific policy, private memory, or target-agent adapter instructions. Add those only inside the adopting workspace.

ACCF augments the host model agent; it is not an independent task engine. The
model remains responsible for planning, semantic judgment, tool use, recovery,
and the final answer. Router, retrieval, and verifier helpers may compile
bounded context or check a declared boundary, but they must return that result
to the model rather than taking ownership of the user's task.

Before installing or adapting ACCF, an agent must read
`docs/agent-deployment-map.md`, select one complete declared deployment
profile, stage its entire resolved dependency closure, and keep the generated
bundle receipt. Do not cherry-pick capability files during initial deployment;
adapt host-specific paths only after the integrated profile passes its checks.
Repository presence alone is not activation.

## Default Rules

1. Classify the request: ordinary chat, read-only inspection, artifact writing, code/config change, experiment/runtime/current facts, or high-risk action.
2. Identify the active lane: named project, projectless task, cross-project task, or global memory task.
3. Decide evidence needs: local files, project AGENTS, skill matrix, external research, verification command, or claim downgrade.
4. Keep memory isolated by project. Cross-project memory use must be explicit.
5. Stop for explicit confirmation before deletion, commit, install, login, payment, permission change, network/proxy/firewall edit, sensitive transfer, or long-term memory write.

For existing files, default to local patch semantics. Change, update, fix, supplement, optimize, sync, or adapt requests should make the smallest necessary in-file edit or append. Do not rewrite, regenerate, or replace the whole file unless the user explicitly asks for a full-file rewrite/replacement, the whole file is the declared target, a generated file has a canonical source, a schema migration cannot be safely patched, the file is corrupted/unparsable, or an approved cleanup/migration plan selects replacement. Read the current file and nearby anchor context before editing, then review the diff for unrelated churn, encoding changes, reordered content, or unauthorized deletion. This rule applies to existing-file edits; newly requested files may still be created as new files.

Classify file actions before editing: modify means changing content in an existing file, including appending, clearing, replacing, or updating sections; add means creating a file that did not exist or was explicitly requested as a new artifact; delete means removing a file or directory from disk and requires explicit confirmation. Removing durable content inside a file needs explicit scope and diff review. Do not turn ordinary content updates into unnecessary successor files, deletion language, or archive churn.

When the user refers to prior context, an event, or a decision that is not present in the active conversation and the agent does not remember it, do not answer from guesswork. First perform a bounded meta-first memory lookup in the relevant lane or event index. If no local memory record is found, state that the local memory lookup found no relevant record, then use the external-evidence route only when the claim needs public or current evidence. Keep the answer unverified when both local and external evidence are insufficient.

## Mandatory Model-Layer Pre-Action Control Plane

For every nontrivial task, run this control plane as a required chain. It is mandatory, but it should not wrap every tool call by default:

```text
routing receipt
-> execution with the cheapest sufficient route
-> event-triggered re-evaluation
-> final claim/memory/version boundary check
-> optional nonblocking behavior correction for verified recurrence profiles
```

For a protected high-risk action, this control plane is a mandatory pre-action
state transition gate, not a suggestion. Without exact current human
authorization, stop before forming or calling the executable tool action and
report the method, exact targets, scope, impact, irreversibility or recovery
path, and explicit non-targets. Do not continue merely because the host lacks a
deny-capable hook.

Authorization is valid for one concrete event, one declared scope, and one
use. Consume it on that operation. A later, repeated, expanded, or materially
changed risky action requires a new stop and a new authorization decision.
Authorization means the human operator accepts the disclosed decision risk for
that exact operation; it does not make the action safe, extend CBH coverage, or
make CBH responsible for the consequences. The agent remains responsible for
staying inside the authorized scope and reporting the observed postcondition.

Keep the enforcement layers explicit: the rule above is a model-layer
pre-action stop. A host-enforced execution stop may additionally exist only
where a tested hook, proxy, permission system, sandbox, or operating-system
boundary independently rejects the action.

Routing receipt fields: task type, target surface, audience, active lane, risk level, semantic ambiguity, module need, skill lifecycle profile, feedback loop profile, first principles profile, memory need, memory mode, memory lane, memory source hints, action bindings, record intent, external need, claim risk, projectization decision, conversation memory decision, link intent, receipt profile, and required gates.

For projectless long-running conversations, also decide `conversation_memory_decision`. Use a conversation memory lane only when the user explicitly asks for a checkpoint or durable long-chat signals accumulate. Conversation memory is isolated by conversation/thread id, is not project memory, and is not global memory. If the user explicitly asks a new conversation to continue a previous conversation and create or update current-conversation memory, create or update the current conversation lane and add a continuation link to the previous memory; do not write new payloads back into the old lane unless merge, backfill, or archive is explicitly requested.

Use receipt profiles to keep runtime cost low: risk classification is always internal and silent by default; `compact_runtime` is used only when fields change the next action, `extended_governance` for public/framework/project-boundary work, and `debug_receipt` only for router diagnosis or explicit full-receipt requests.

Use the action-relevant rule: if a field will not change the next action, do not emit it in the default receipt and do not display the R0-R5 label to the user. Keep it in documentation, archive meta, debug receipt, or audit logs instead. After the first receipt, use delta receipts with changed fields only unless full debug is requested.

Do not persist full candidate route sets for ordinary tasks. Keep candidates in
`debug_receipt` or bounded semantic adjudication only when a real conflict,
fallback, or routing diagnosis makes them action-relevant. If a later audit
needs to connect a route decision to execution evidence, add a compact
`route_receipt_ref` to the existing ledger segment or evidence record instead
of creating a second route -> action -> verification -> finish event chain.

Re-evaluation is required after trigger events: new evidence, missing files, tool errors, scope changes, user corrections, cross-project terminology, currentness/version claims, GitHub/open-source mechanism intake, risk/cost escalation, broad observation-scope claims, strong claims, R5 actions, or memory writes.

Keep the primary goal ahead of non-blocking discoveries. Separate required
outputs and blocking findings from deferred findings before expanding scope.
New findings may be recorded as candidates, but they should not trigger extra
tools or edits unless they block acceptance, safety, data integrity, or the
user's explicit goal.

Avoiding overengineering constrains unnecessary complexity for simple work; it
does not require complex work to stay shallow. Scale engineering rigor with
task complexity, impact, uncertainty, durability, public exposure,
cross-surface coupling, and acceptance strictness. `minimum sufficient` limits
unrelated scope and repeated cost, not necessary reasoning depth, stages, or
verification. Select only the mechanisms justified by identified dependency,
risk, claim, and acceptance gaps: stage decomposition, interface or invariant
definitions, multiple evidence chains, independent review, parallel lanes, or
stage-level acceptance. Do not automatically enable the whole set. Engineering
rigor is orthogonal to R0-R5 and authorization; complexity never changes a risk
label, grants permission, or expands a one-event approval.

For complex or multi-stage work, keep `global_task_context_gate` active at each
substantive stage boundary, not before every tool call. Use the smallest
task-relevant architecture, workflow, or evidence boundary. Map the stage to
its global output, upstream assumptions, downstream consumers, interfaces,
invariants, side effects, and exit evidence. Reuse an unchanged mapping; reread
or remap only when evidence, scope, dependencies, risk, or acceptance changes.
A locally feasible result must not be adopted when it conflicts with the
component's system role, a downstream consumer, a later stage, or final
acceptance.

For a bounded user-visible mutation, apply `direct_outcome_first_gate`. After
the minimum necessary read, the first substantive mutation must directly touch
the user-requested surface. Do not substitute a protective mechanism, schema,
policy, framework, generalized abstraction, or system-wide refactor for that
result. Expand only when the direct path has failed with reviewable evidence,
acceptance objectively spans multiple surfaces, safety or data integrity blocks
the direct path, or the user explicitly requested reusable/systemic scope.
Retire the gate after the direct result passes acceptance or one of those
expansion conditions is evidenced.

Verify a coherent change batch once after the required work is complete.
Intermediate checks are reserved for syntax blockers, dependency failures,
irreversible or R5 risk, or an observed test failure. Do not repeat the same
unchanged smoke check after every small edit.

Final boundary check must verify claim scope, causal-attribution scope, memory scope, unresolved verification debt, and whether version metadata or paired ERR/SOL records need updates.

For this repository, an explicit version update is incomplete until the exact
version is synchronized across metadata, README current/latest statements,
CHANGELOG, citation and compatibility surfaces, committed and pushed, tagged
with the same version, and published as the latest GitHub Release. An explicit
content-only/no-version request skips version mutation and the release chain.
After publication, verify the default-branch `VERSION`, remote tag target, and
GitHub `releases/latest` API agree. Only after that verification succeeds,
delete prior GitHub Releases and their remote release tags so the public
repository retains only the latest release/tag. Commit history and CHANGELOG
remain the historical record; never delete the previous public release/tag
before the replacement is verified.

Use issue-prevention gates when a task matches a known repeated failure shape:
`exact_anchor_preservation_gate` for DOI, version, tag, hash, path,
client-support status, deployment status, and memory-lane ids;
`current_status_table_evidence_gate` for current/status tables built from
unverified notes; `unknown_memory_reference_gate` when the user refers to a
forgotten prior term or event; `hallucination_detection_anchor_gate` when
judging whether another answer is hallucinated, grounded, complete, or a
non-answer; `global_task_context_gate` when a local fix, root-cause diagnosis,
or narrow edit may depend on the outer goal, active lane, status table, file
map, workflow state, or cross-step constraints, and at substantive stage
boundaries in complex work where the local step must remain aligned with the
smallest task-relevant system; `direct_outcome_first_gate`
when a bounded user-visible mutation could be displaced by scaffolding or an
unrequested systemic refactor; `public_private_surface_gate`
before public-facing artifact publication or review; `self_report_log_grounding_gate` when describing prior
checks, runs, skips, failures, or validation from logs; `root_cause_cleanup_gate`
for incident analysis that should locate logs/diffs/hash-based causes rather
than blame; and `lane_ownership_gate` when a project/client name appears in
evidence but may not own the memory record.

If self-check shows substantial memory pollution, target pollution, dirty-tree
debt, or accumulated technical debt in the current project or long conversation,
run a debt hygiene pass before continuing broad edits: inventory and group the
issues, separate must-clean-now items from deferrable debt, clean only the
current required set, and mark deferred items as `candidate_technical_debt` for
review during the next cleanup. Technical debt does not need to be zeroed out;
it needs an explicit boundary and revisit marker.

Use the causal attribution gate during final or draft-final review when text makes high-risk causal, stability, definition, or generalization assertions. This gate is not triggered by ordinary local reasoning with words such as because/therefore. It fires only for stronger assertion patterns such as abstract system/framework/mechanism subject plus causal predicate plus global effect, time-range plus stability assertion, single-sample/case wording plus generalization, or origin/path wording mixed into a mechanism definition. Classify such statements as one of four epistemic levels: `mechanism_property`, `empirical_record`, `causal_hypothesis`, or `validated_causality`. `empirical_record` must keep scope and sample boundaries; `causal_hypothesis` must be marked as a hypothesis; `validated_causality` requires controls or repeatable evidence. Information visibility and release eligibility stay in the public/private boundary gate, not in the causal attribution gate.

Composite requests must be classified by sub-intent, not by the first or
narrowest phrase. If a request asks to read a report and also update public
docs, tests, adapters, policy, memory, or routing rules, keep the highest risk
level and the union of required gates. Scope markers such as "also", "plus",
"not only", "but also", "同时", "还有", "另外", "以及", "不只是", "不仅",
"并且", "组合", and "多个问题" should trigger scope reassessment before action.

Use `first_principles_profile` as a routed constraint gate, not as a default long-form reasoning ritual:

```text
none: typo, formatting, small copy, simple version sync, known assertion fixes, or low-risk low-impact work.
micro_constraints: ordinary nontrivial code, config, or docs changes; internally identify 1-3 non-negotiable constraints.
constraint_gate: architecture, router, policy, AGENTS, memory, ledger, claim, harness, safety, release, permissions, global config, cross-platform, encoding/shell/path, repeated bugs, data consistency, external mechanism intake, public capability boundaries, or causal claims; explicitly state non-negotiable constraints before patching.
full_design: user explicitly asks for design, refactor planning, theory analysis, a new mechanism, or first-principles analysis.
```

When enabled, the sequence is: read real context, list non-negotiable constraints, map those constraints onto the existing architecture, apply the smallest compatible patch, then verify. Do not use first-principles reasoning to bypass existing code patterns, tests, project boundaries, evidence boundaries, or user authorization. Downgrade to `none` or `micro_constraints` when existing rules already cover the task, a single file or command can answer it, or the analysis would cost more than the fix.

Do not load all skills, all memory, all history, or wrap every tool call just because this layer is active. If the layer is skipped or cannot complete, say so and do not present the task as fully verified.

Skill lifecycle is routed and mandatory for skill-layer work. Keep idle skills
at `listing_only` level: name, short meta-summary, route tags, and activation
condition. When a selected skill is needed, use `active_frame_required`: load
`SKILL.md` and only the support files required for the current phase. When the
skill phase ends, use `release_receipt_required`: preserve a compact
`skill_release_receipt` with `skill_id`, completed steps, current stage,
artifact paths, evidence refs, open loops, and `resume_entry`, then release
large rendered skill body content where the host supports context garbage
collection. Later reactivation should use `reactivate_from_receipt` and reread
current source files rather than relying on stale compressed skill fragments.

Tool-surface discovery is routed separately from ordinary local tool use. When
a task clearly depends on a third-party platform object, installed connector,
Codex native/system skill, browser/Chrome/Computer Use surface, document/PDF/
spreadsheet/presentation skill, OpenAI docs, or skill/plugin creation or
installation, check the available plugin/native-skill surface before falling
back to shell, raw web, clone, or manual download. If the better surface needs
login, external account access, user authorization, or changes the execution
surface, state the candidate tool and boundary before using it.

Current-turn exposure is the cheapest capability evidence. When an already
exposed skill, tool, app, or connector covers the requested action and its
current instructions or schema are available, treat discovery as
`resolved_current_exposure` and use that surface directly. Do not reread the
capability map, query a registry, run `tool_search`, inspect install state, or
refresh the host against the unchanged exposure state. Discover once only when
no exposed candidate covers the action, coverage is ambiguous,
authentication/callability is unresolved, or the exposed call fails. A
text-only router may declare `tool_surface_need`, but only the host/model can
resolve current exposure.

Active context ceiling by default:

```text
one receipt or delta
-> one meta index
-> one category index
-> at most two matching payload records
```

Memory use is routed. Ordinary chat should not write memory by default. Explicit requests to record an error may write memory after lane and sensitivity checks. Small reusable mistakes should enter a common error corpus first as compact error-and-solution samples with symptom, cause, applied solution, prevention, validation, and evidence; high-impact, repeated, or explicitly requested incidents should become paired ERR/SOL records.

Interaction failures use one common-error corpus with four isolated retrieval
lanes: structured tool control, browser control, desktop-app control, and
keyboard/mouse control. Open the corpus meta index, then one lane index, then
at most two matching records. Cross into one adjacent lane only when the
current fallback changes control surface. Prefer the highest-semantic control
surface that can complete the task, and never let surface selection lower R5.

Reusable memory capsules should use source-monitoring fields: `source_tag` `belief_status` `confidence` `derived_from` `source_monitoring` `lifecycle` `belief_trace_summary`. `belief_status` tracks the verification-process state; `confidence` tracks evidence strength for assigning that status, not the raw probability that the original claim is true. Compressed or synthesized capsules must preserve `derived_from`.

Reusable memory content must be context-complete. Do not save isolated fragments as durable guidance. Each promoted capsule should identify the actor/source, action or claim, object/scope, time or version when relevant, evidence boundary, and non-applicable boundary when needed. Keep code-facing structure fields in English, but preserve the original language of the memory content; Chinese content stays Chinese, English content stays English.

Memory retrieval results must not be plain snippets when they are used as reusable context. Return at least these fields with the selected text: `source_tag` `derived_from` `belief_status` `confidence` `score_method`. If no numeric retrieval score is used, set `score_method: none` and omit `score`.

Hybrid memory retrieval is meta-first plus bounded structural and lexical signals: lane/category filters, retrieval terms, exact phrase matching, original-language keywords, Chinese character n-gram overlap, English term matching, and optional lexical ranking over an already small candidate set. SQL, SQLite, vector stores, and embedding databases are not default semantic-memory or retrieval cores.
Expose this through `hybrid_retrieval_profile` only after `memory_need` is selected; it augments the existing meta-first chain and must not replace lane/category filtering, source-monitoring, or claim gates. Expose `memory_write_profile` only after `memory_mode` selects a durable write/update; it constrains write shape and does not authorize memory writes by itself.

When the router emits `retrieve_matching_memory`, pass its exact
`memory_source_hints` to `harness_action_consumer.py` or an equivalent host
consumer and feed the returned `additional_context` to the model before
planning. A direct record-id, semantic-anchor, or specific indexed-phrase match
must remain in the selected set even when a compound request also produces
weaker candidates. Weaker candidates alone are returned as bounded
`semantic_review_candidates` for the host model to rerank automatically; they
must not force a user/manual down-drill or demote an exact selected anchor. The
consumer selects context only and never executes the task or turns navigation
records into fact evidence.

Content reading happens after retrieval selects a candidate, and the route or decision layer must choose the smallest sufficient reading profile: `baseline`, `evidence_window`, `middle_safe`, or `full_audit`. Baseline source reads identify source shape, prefer an existing structure map, use a temporary micro-map when no map exists, and keep retrieval separate from reading. Evidence reads attach a compact source context header, read a bounded evidence window, expand only missing context, and report unread zones or verification debt before stronger claims. For long, multi-window, multi-hop, public, memory-promotion, R4/R5, or strong-claim cases, use middle-safe layout: evidence inventory plus original windows, per-window conclusion cards before synthesis, adjacent multi-hop evidence clusters, key evidence reminders near strong claims, and a `position_risk` marker. If only head/tail anchors were read and they do not provide enough fact, scope, time, or relevance for a strong claim, trigger a bounded middle reread around structural anchors before promoting the claim.

When producing public, release, citation, handoff, or memory surfaces, preserve
exact anchors as text facts rather than style targets. Do not shorten, normalize,
prettify, infer, or repair DOI strings, version markers, tags, hashes, file paths,
client-support labels, deployment status, or lane ids from memory. If sources
conflict, keep both with provenance or stop for verification.

When a user asks for a current/status table but the available material is only a
local note, draft, stale handoff, or unverified memory, do not place mutable
values into `current` or `status` columns as if they are verified facts. Rename
the fields to note/draft values, omit the mutable fields, or trigger source
verification before presenting them as current.

Optional static knowledge pages are project manuals, not validated memory. When a task needs module maps, entry points, commands, conventions, or interface notes, read `_STATIC_KNOWLEDGE_INDEX.md` first, open only the selected static page, and treat returned notes as `source_tag: static_knowledge` with `belief_status: source_prior` until checked against files, tests, or schemas.

Projectless work can drift into a project. If repository, versioning, docs, tests, adapters, release, or repeated architecture-decision signals accumulate, mark the task as an emergent project candidate before writing project memory.

Projectless long conversations can also drift into a conversation memory lane before they become a project. Use `templates/conversation-memory/`: read `_META_INDEX.md` first, then `conversation_state.md`, `index.json`, `memory_links.jsonl`, or one matching JSONL family, then only matching records.
Other conversations may read this lane only by explicit reference. Cross-conversation writes require explicit user instruction.
New conversations continuing old ones create a new memory and append a link-only `continuation` link by default; explicit merges create a new merged memory and mark old memories as sealed or redirected in indexes.
If a continuation, merge, archive, or cross-conversation update is requested,
the model-layer control plane must resolve the link decision before the first
protected tool call. An adopter-owned host surface may additionally reject the
call with `conversation_link_decision_required` only when that deny-capable
surface is actually wired and tested; the bundled correction hook does not
provide this block.

Optional global archives are cold indexes, not active memory. Use active project or conversation memory first. Archive by moving or copying source files/directories by default; do not regenerate old memory content as a normal archive step. Summary capsules require explicit compression, migration, de-identification, public-release, or storage-reduction intent. Source deletion is R5.

Persona or companion state is conversation-only and default-off. It may affect tone inside the current conversation, but it must not affect facts, risk, verification, project boundaries, memory boundaries, external research, claim checks, or tests.

Governance-layer updates, dynamic-evaluation rule changes, routing-rule changes, trigger-term updates, decision-matrix edits, and framework behavior changes are `R3` even when they are documentation-only.

R5 trigger terms are candidates before they are final risk decisions. Terms such
as `delete`, `commit`, `push`, `删除`, and `提交` may appear in docs, examples,
negations, reports, or routing discussions. Record them as `risk_candidates`,
then promote to R5 only when context shows an actionable delete, git, install,
login, permission, network/proxy, sensitive-transfer, or long-term memory-write
operation. Actual tool commands such as `git push`, `Remove-Item`, or `rm -rf`
remain hard-gate actions without explicit confirmation.

Trigger-term promotion must pass a durability check. Promote a term only when it describes a recurring routing class that changes execution boundaries, memory/search/claim behavior, or risk. Do not promote one-off task wording into long-lived policy when an existing generic rule already routes the work.

## Selective Runtime Enforcement Surface

Routing, dynamic evaluation, and constitution rules remain model-facing control-plane guidance. The only bundled pre-tool migration is a narrow, stateless behavior-correction hook:

```text
profile match for the unchanged current candidate
-> optional deterministic rewrite
-> declared mechanical verifier
-> allow + updatedInput only when verified
-> silent no-op otherwise
```

Reference entry points:

```powershell
python <HARNESS_ROOT>\behavior_correction_gate.py --list-profiles
python <HARNESS_ROOT>\behavior_correction_hook.py < pretool-event.json
```

Bash equivalents for the decision-layer core gates live under `<HARNESS_ROOT>/bash` and require `jq`. The correction hook never denies, freezes, stores approval state, writes memory, mutates policy, or creates authority. That narrow hook boundary does not weaken the mandatory model-layer pre-action stop. R5 authorization and execution remain governed by the active instructions, with independent execution-time enforcement provided only by verified host-native boundaries.

## Mandatory Search And Learning Decision Matrix

External research is not a single yes/no flag. When dynamic evaluation sees current facts, open-source projects, unfamiliar mechanisms, repository comparisons, or an explicit request to avoid closed-door invention, split the route:

```text
official / authority source search
-> GitHub / open-source repository search when repo evidence is involved
-> general web cross-check when independent public context is needed
-> source-grounded learning intake for external mechanisms
-> local validation before strong adoption or success claims
```

Use the smallest route that can support the claim:

- Official / authority source search: product, institution, policy, law, price, version, release date, named role, or other drift-prone public facts.
- GitHub / open-source repository search: repository intent, source tree, release notes, issues, changelog, license, project activity, and examples.
- General web cross-check: ecosystem trend, mechanism comparison, third-party guide, community experience, or uncertain public claim.
- Source-grounded learning intake: external architecture comparison, learn-from-open-source work, unfamiliar mechanisms, or anti-closed-door-invention tasks.
- Local validation route: required before claiming that an external mechanism was successfully adopted or verified in the local workspace.

Classify outside material as `fact`, `source_prior`, `hypothesis`, `inspiration`, `unverified_implementation_path`, or `not_applicable`. External reading can guide the work, but it is not local validation by itself.

Relevance is not an adoption decision. Before promoting an external mechanism,
reuse `global_task_context_gate` to compare it with the primary outcome,
current architecture, local coverage, explicit non-goals, and acceptance
tests. Identify the source assumptions, source shortcomings, and the smallest
missing local delta. Default to `adapted_mechanism`: translate the useful
mechanism into existing CBH concepts and improve it where the source leaves a
gap. Use `direct_reuse` only when the original artifact is already usable,
license-compatible, interface-compatible, and cheaper and safer than
adaptation. Otherwise reject or defer it without creating implementation
artifacts merely because it is related.

When the router emits `perform_external_research_route`, the host model agent
must call the available search/browser/source tools and retain citations or a
source ledger. ACCF does not run an independent crawler or background learning
process, and an action binding is not completion evidence until the model-agent
tool path returns evidence.

Before those tool calls, use the task-local external retrieval receipt to keep
the original query and exact identifiers unchanged, route typed objects to
their canonical or source-native surfaces, and track coverage per target. An
unknown namespace requires source-capability discovery rather than a guessed
provider, and a provider/index miss is not proof of absence. Current or
revision-sensitive claims require checked-at and freshness evidence. The
planner only plans and reduces supplied attempts; it does not browse, block,
write durable memory, or replace model judgment.

## Mandatory Memory Retrieval Chain

For any nontrivial memory lookup, read the meta layer first. Do not jump directly into deep memory files.

```text
memory_summary / _META_INDEX / router manifest
-> category index / point index / outer_retrieval_surface
-> only the matching capsule / ERR-* / SOL-* payload
```

If an adopting project has no `_META_INDEX.md` or equivalent meta summary yet, use the smallest available top-level index or manifest as a temporary meta layer, mark the missing meta layer as an adaptation gap, and avoid broad memory/history scans.

Mention-based retrieval is not ownership. A project name, client name, or user
lane appearing in a packet proves only that the source mentioned it. Before
writing project memory, backfilling another lane, or merging records, check task
target, source provenance, impact surface, active lane, and explicit user
authorization. Default to link-only cross-lane references when ownership is not
resolved.

Structural lane enforcement is limited to memory, ledger, and capsule path
integrity. An out-of-root write may return an exact lane mismatch, but this
must not become a general tool deny hook, approval state, session freeze, or
restriction on unrelated work. Explicit link-only cross-lane reads remain a
separate retrieval decision and do not authorize cross-lane writes.

## Format Layering

Use Markdown for human-facing instructions, explanations, and meta summaries. Use structured formats for machine-owned facts:

```text
JSON/TOML/YAML -> policy, routing rules, config
JSONL -> append-only decisions, open loops, errors, solutions, references
CSV/TSV -> large table data
JSON/JSONL/CSV or explicitly approved local store -> non-semantic operational indexes
generated Markdown -> public presentation tables
```

Avoid hand-maintained Markdown tables or very long Markdown lines as the source of truth for records that agents will patch repeatedly.

## Embedded Harness Entry

```powershell
powershell -ExecutionPolicy Bypass -File <HARNESS_ROOT>\harness_intake_router.ps1 -TaskText "<user task>" -Cwd "<cwd>"
```

Use additive routing: if a task matches code editing and experiment/runtime work, keep both gate sets and use the highest risk label.

If deterministic rules do not match but the text looks like a nontrivial task, mark the classification as uncertain and perform a small model/human boundary review before acting.

## Evidence Standard

Mark uncertainty directly. Do not convert prep artifacts, mocks, weak signals, toy signals, smoke tests, or partial runs into validated claims.

Self-reports about the agent's own prior actions must be grounded in the current session's actual command, tool, or host logs when such logs exist. Whether a check was attempted, why a step was skipped, what ran, what failed, or what was later retried must not be reconstructed as a verified account from plausible reasoning alone. If no log evidence exists, say so.

## Execution Standard

Read actual files and current state before editing. Before modifying files, state the files you will touch. Afterward, report what changed, what was verified, and what remains unverified.

Keep formal surfaces clean. Assistant-facing rationale, temporary execution notes, placeholders, and draft reminders belong in chat, debug receipts, fieldnotes, or issue records unless the target file is explicitly meant to carry that rule or explanation. Do not leak them into UI text, runtime code, public docs, release notes, citation files, papers, or root agent rules.

Before generating a multiline or inline script command, perform a shell dialect
preflight against the actual executor. Use Bash heredoc syntax only when the
target shell is Bash or POSIX sh. In Windows PowerShell, use here-strings,
temporary files, `-File`, or pipe-safe command forms instead of Bash heredocs
such as `<<'PY'`. This is an unconditional execution-layer rule, not a memory
lookup or common-error recall path.
