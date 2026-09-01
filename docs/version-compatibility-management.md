# Version Compatibility Management

Agent clients change. A working harness adapter can stop working after a client update because the hook name, payload schema, executable path, bundled runtime, or settings file moved.

The compatibility manifest records the current adapter/runtime relationship so adopters can re-check it cheaply.

It should stay compact. The manifest records the minimum facts needed to decide whether the adapter is still safe to trust after drift. It is not a full runtime inventory and should not trigger broad memory, source, or tool scans by default.

## Purpose

Use the compatibility manifest to answer:

- which agent/runtime version was checked;
- which instruction entry is loaded;
- which hook events exist;
- which lifecycle capture points are actually wired, such as prompt, pre-tool, post-tool, pre-compaction, and final stages;
- which hook matchers are intentionally narrow versus broad;
- which wrapper paths and language runtimes are available;
- which denial schema and exit code are expected;
- which encoding and transcript payload fields were checked;
- which smoke tests were last run;
- which surfaces are known bypasses.

The public template is:

```text
templates/adapter-contract/compatibility.manifest.json
```

## Compatibility Evidence

Record the inspected runtime and checks:

```text
runtime name: Codex
runtime version checked
adapter version checked
hook schema observed
wrapper path observed
last smoke test result
known untested surfaces
```

If a field is not checked, mark it `unverified`. Do not infer compatibility from another runtime.

## Manifest Sections

| Section | Meaning |
| --- | --- |
| `runtime` | Product/client name, version, platform, and checked date. |
| `instruction_entry` | File or setting the agent actually reads for root rules. |
| `hook_schema` | Event names, payload fields, denial payload, and blocked exit code. |
| `wrappers` | Python, PowerShell, Bash, cmd, or other wrapper entry points and their verification status. |
| `payload_safety` | Encoding, sanitation, and logging assumptions. |
| `media_payloads` | Whether voice or recording input reaches the hook as transcript text instead of raw media only. |
| `claim_payloads` | How nested claim JSON is passed without shell-quoting loss. |
| `quality_reference` | Whether optional domain rubrics and source-tier catalogs are supported as advisory/source-prior context. |
| `claim_artifact_contracts` | Whether structured claim artifacts can be passed with original evidence refs and checked by deterministic scripts. |
| `external_model_delivery` | Whether an external model can safely act as a structured JSON filler with bounded repair and deterministic render/verify. |
| `acceptance_tests` | Last result for active routing, denial, payload safety, log writing, and version drift. |
| `bypass_surfaces` | Tool paths or background actions that are not covered by the adapter. |
| `drift_policy` | What to do after client updates or adapter changes. |

## Update Triggers

Refresh the manifest when any of these change:

- agent client version;
- adapter version;
- hook settings path;
- hook event name or payload schema;
- Python, PowerShell, Bash, Node, or shell path;
- generated command dialect such as PowerShell here-strings versus Bash heredocs;
- instruction entry filename;
- denial payload or exit code behavior;
- hook matcher scope such as `*` versus command tools only;
- final-answer or Stop hook availability;
- encoding defaults such as `PYTHONUTF8` and `PYTHONIOENCODING`;
- transcript payload field names for voice or recording input;
- nested JSON or claim-file handoff format;
- memory root or project-lane root;
- external memory server, MCP memory tool, or plugin path;
- operating system or shell.

Do not refresh the manifest on every turn. Refresh it only on adapter install, agent client update, wrapper/hook edits, failed smoke tests, or explicit user request.

## Drift Response

Use this response order:

1. Re-read the manifest.
2. Run adapter tests outside the agent.
3. Run the exact hook or wrapper command.
4. Run one active routing test.
5. Run one blocked-action test in a disposable workspace.
6. Run one false-positive guard test for non-command file content if file tools are hooked.
7. Run one final-claim test if the runtime exposes a final-answer hook.
8. Run one transcript routing test if the runtime supports voice or recording input.
9. Mark bypass or unknown surfaces explicitly.
10. Only then claim the adapter is compatible with that runtime version.

Automatic repair should be opt-in. Compatibility checks may read local config and version metadata, but they should not rewrite client settings unless the user confirms that repair action.

## Source-Prior Influences

- LanNguyenSi/harness is a source-prior influence for manifest-style declarative control planes and validation vocabulary: https://github.com/LanNguyenSi/harness
- Epic Harness is a source-prior influence for hook health and pipeline state ideas, but its self-evolving skill behavior is not part of this default contract: https://github.com/epicsagas/epic-harness
- rohitg00/agentmemory is a source-prior influence for lifecycle hook coverage, memory command semantics, hybrid retrieval vocabulary, and client-update hook drift caveats. It is not a required backend for this framework: https://github.com/rohitg00/agentmemory

Treat those as design references. Local compatibility remains unverified until the target runtime passes its acceptance matrix.
