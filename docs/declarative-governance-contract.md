# Declarative Governance Contract

The governance contract is the machine-readable boundary between an agent runtime and Agent Cognitive Continuity Framework.

It does not replace host permissions or sandboxing. It declares what the model-facing runtime should decide before deeper work starts and which bounded outputs it can consume.

## Purpose

Use this contract to prevent three common failures:

- the agent starts work before it understands risk, memory, search, or claim boundaries;
- a runtime says a hook is installed, but the hook is not on the action path;
- a reference correction protocol is mistaken for execution authority.

This contract is intentionally small. It is a leverage layer, not a new runtime framework. It should make the existing router, memory gate, search gate, claim gate, and optional correction receipt easier to wire and verify without making ordinary conversations or read-only tasks more expensive.

## Minimal Contract Shape

```text
contract metadata
-> supported stages
-> required decisions
-> authorization boundary and optional rewrite semantics
-> payload safety boundary
-> evidence and claim boundary
-> cost profile
-> acceptance references
```

The public template is:

```text
templates/adapter-contract/governance.contract.json
```

## Stage Contract

The stage vocabulary below includes optional adopter-owned host integration.
The bundled CBH core implements the model-facing route and a task-local
`pending_user_confirmation` receipt; it does not translate legacy
`status: pass` into execution authority and does not install a generic deny or
Stop surface.

| Stage | Purpose | Required When | Typical Output |
| --- | --- | --- | --- |
| `prompt_stage` | Active routing before planning | Nontrivial task, memory/search/claim decision, adapter route context | `compact_receipt` or `routing_receipt` |
| `pre_tool` | Selective hard gate before protected tool execution | R5, high-risk command tools, package install, shell/network actions | `allow`, `warn`, `require_approval`, or `deny` |
| `schema_aware_file_tool` | Optional file-tool gate with file-tool semantics | File edits need hard enforcement beyond command gating | file-specific `allow`, `require_approval`, or `deny` |
| `memory_access` | Meta-first and lane-isolated memory read/write | Memory read/write, project-lane ambiguity, long-term memory request | `allow`, `cross_reference_allowed`, or `deny` |
| `external_research` | Source-grounded learning or current fact routing | Latest/current/version/GitHub/open-source/policy/legal/price claims | source ledger route and validation boundary |
| `final_claim` | Strong-claim boundary before final answer | Validated/verified/stable/proven/performance/external fact claims | pass or claim downgrade/block |

Start command hard gates with command-tool matchers such as `Bash|PowerShell` where the host supports matchers. Do not route every Write/Edit payload through command-pattern matching unless the adapter understands that file tool's schema; otherwise normal documentation text can be mistaken for a dangerous command.

## Decision Vocabulary

Use a small shared decision set:

```text
allow
warn
require_approval
deny
```

This vocabulary applies only to an adopter-owned host surface that actually
implements and tests those decisions. In the bundled router,
`routing_status: classified` describes successful classification, while
`execution_disposition: pending_user_confirmation` describes the model-facing
pre-action boundary. Neither field grants execution authority or claims a host
hard block.

## Authorization Scope And Responsibility Boundary

`require_approval` is a model-layer pre-action stop even when the adapter has no
deny-capable hook. The governed model must not form or call the executable
action until it receives exact current authorization.

Authorization must be bound to:

- one concrete event;
- one declared target and scope;
- one use;
- the risks and recovery boundary disclosed before approval.

The authorized operation consumes that authorization. A later, repeated,
expanded, or materially changed risky operation requires a new
`require_approval` decision. Human authorization accepts the disclosed
decision risk for the exact operation; it does not certify the operation as
safe or make CBH responsible for its consequences. The runtime must still
constrain execution to the approved scope and return a postcondition receipt.

## Required Receipts

The contract should not force full receipts for every ordinary task. Use the existing profile model:

- `compact_runtime`: default for ordinary local work;
- `extended_governance`: public/framework/adapter/memory/project-boundary work;
- `debug_receipt`: router diagnosis only.

At minimum, a nontrivial prompt-stage receipt should include:

```text
task_type
project_lane
risk_level
required_gates
external_search_need
memory_need
claim_gate_need
human_confirmation_need
```

Do not add fields unless they change the next action. If a field is only useful for debugging, put it behind `debug_receipt`. If a field is only useful for public/framework governance, put it behind `extended_governance`.

## Denial Semantics

A runtime capability claim is incomplete unless it declares how a denial is honored:

```text
denial payload schema
blocked exit code
host honors denial: observed / unverified / unsupported
bypass surfaces
last blocked-action test
```

This is more important than listing hook names. A `PreToolUse` hook that returns `deny` but is ignored by the host is advisory, not hard enforcement.

## Payload Safety

The governance contract should reference the payload safety boundary used by the adapter. At minimum:

- stdin JSON must be parsed without executing payload content;
- the hook process should force UTF-8 where the host shell can drift, for example `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` for Python hook runners;
- invalid Unicode such as lone UTF-16 surrogate escapes must be sanitized before route, log, state, or output writes;
- hook output must be ASCII-safe or otherwise guaranteed to encode in the hook runner environment;
- voice or recording input must arrive as bounded transcript text before routing; raw media blobs, bytes, base64 strings, and arbitrary recording paths are not decoded by the default adapter;
- nested claim payloads should use a file-based handoff when shell quoting would corrupt JSON;
- captured raw payloads must not be published.

## Source-Prior Influences

This contract is an adapted design, not a vendored copy.

- LanNguyenSi/harness is a source-prior influence for declarative control planes, policy packs, and action-aware risk gates: https://github.com/LanNguyenSi/harness
- ChatBotKit's agent CLI template is a source-prior influence for tool schemas, JSON output, and iteration/timeout boundaries: https://github.com/chatbotkit/template-node-agent-cli-js

External source-prior material can guide shape and vocabulary. It does not count as local validation. A contract becomes `local_validated` only after the adopting workspace passes the acceptance tests for that runtime.
