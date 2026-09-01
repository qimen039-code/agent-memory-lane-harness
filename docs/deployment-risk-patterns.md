# Deployment Risk Patterns

Use this guide when adapting Agent Cognitive Continuity Framework into an agent runtime.

The core deployment risk is that copying framework files is not the same as
loading the model-layer pre-action contract or wiring an independent host gate
into the execution path. If the model does not load the contract, the
model-layer stop is inactive; if the runtime does not call a gate before the
protected action, host-enforced denial is inactive.

This document is intentionally version-neutral. Agent clients change hook names, config locations, environment variables, and tool schemas. Treat every product-specific integration as unverified until it passes the local acceptance tests below.

For a quick local preflight, run the read-only doctor from the repository root:

```bash
python tools/cbh_doctor.py --repo-root . --json
```

The doctor checks package files, policy shape, PowerShell routing probes,
documentation alignment, and Bash/jq availability. It does not configure
hooks, install dependencies, write memory, or prove that a host agent honors
every execution path.

For a concrete adapter, keep two compact records near the adapter layer:

- a declarative governance contract describing stages, denial semantics, payload safety, and cost boundaries;
- a compatibility manifest describing the runtime version, hook schema, wrapper paths, last smoke tests, and bypass surfaces.

These records are not meant to expand every turn. Use them during adapter setup, client updates, hook/wrapper changes, failed smoke tests, or explicit audits.

## Deployment Levels

The model-layer pre-action stop and host-native physical enforcement are
separate surfaces. The table below records what each wired level can actually
enforce.

| Level | What is wired | What it can enforce |
| --- | --- | --- |
| L0 instruction only | Root `AGENTS.md` or configured workspace rules | Model-layer behavior contract. Protected actions stop before execution when the model loads and follows it; no independent host denial is claimed. |
| L1 model-layer pre-action control plane | Intake router, memory/search/claim gates called by the agent or user | Structured decisions plus a mandatory stop before unauthorized protected actions. Still not an independent host execution blocker. |
| L2 optional behavior correction | Verified current-candidate rewrite hook | Can rewrite one mechanically matched input; no match or failure is a no-op. |
| L3 tool proxy / in-process middleware | All protected tool execution goes through one policy function or proxy | Stronger runtime enforcement for covered tools. Bypass paths still matter. |
| L4 sandbox/runtime enforcement | The host runtime or sandbox owns the policy check before execution | Physical blocking for covered execution paths. Requires host/runtime support. |

Most adopters should aim for L1 plus an optional, verified L2 correction path. Do not wrap every tool call.

## Agent Runtime Families

| Runtime family | Typical integration surface | Main deployment risk | Practical solution |
| --- | --- | --- | --- |
| Instruction-file agents | Workspace rule files, project docs, memory files | The file is present but not loaded by the agent | Ask the agent to report the routing receipt on a test task, and keep a visible root instruction entry. |
| CLI agents with hooks | Pre-prompt, pre-tool, post-tool, stop hooks | Hook exists but is not on the actual execution path | Use ACCF for model-layer routing and pre-action stopping; if the host exposes a native denial hook, verify that host-native denial before relying on it. |
| IDE or desktop agents | IDE extension settings, tool executor pipeline, output gate | UI actions, background tasks, or built-in tools bypass the wrapper | Identify every tool execution surface and mark unhooked surfaces as advisory. |
| Custom orchestrators | Python/Node middleware, tool registry, function dispatcher | Policy is called after execution or its result is ignored | Keep the model-layer pre-action stop and put an adopter-owned host-native enforcement function before dispatch when independent physical blocking is required. |
| Hosted or SaaS agents | Limited settings, system prompts, external tools | No local pre-tool hook is available | Use the model-layer pre-action stop and describe host execution denial as unavailable, or move protected actions behind an external proxy you control. |
| Terminal-only assistants | Shell aliases, wrapper scripts, project instructions | Users or tools can call the raw shell directly | Use wrappers for high-risk commands and state clearly that raw shell paths bypass enforcement. |

## Common Deployment Failures And Fixes

| ID | Symptom | Likely cause | Fix | Acceptance check |
| --- | --- | --- | --- | --- |
| DEP-001 | The harness files exist but behavior does not change | The agent never loaded the root instruction file | Map `AGENTS.md` to the instruction filename or settings surface the agent actually reads | Ask for a routing receipt on a mixed-risk task and verify the expected gates are named |
| DEP-002 | The router runs, but dangerous tools still execute | The pre-tool hook or wrapper is not in the execution path | Wire the gate into the runtime's earliest pre-execution surface | Run a disposable high-risk command test and confirm it is blocked before execution |
| DEP-003 | The hook runs, returns blocked, but the tool still runs | The host ignores the hook result, exit code, or denial schema | Use the host-supported denial format and exit code; if unsupported, mark the path advisory | Confirm logs show both hook invocation and blocked tool suppression |
| DEP-004 | A command wrapper works in tests but not during agent use | The agent uses another shell, terminal, or internal tool executor | Identify the actual executor and move the wrapper there | Compare wrapper logs with the agent's real tool calls |
| DEP-005 | `PreToolUse` routing is wrong or loses context | The pre-tool event lacks the original user prompt | Store prompt/session state at prompt submit time and reload it in pre-tool checks | Verify the pre-tool log contains the original task text, not only `R5` or a compact receipt field |
| DEP-006 | Hook command fails only on Windows or only on macOS/Linux | Shell, quoting, executable bit, path separator, `bash` availability, or Python launcher differs | Use explicit shell invocation, quote workspace paths, and expose `PYTHON_BIN` or equivalent; on Windows use `cmd.exe` wrappers when Bash is unavailable | Run the hook command from the same shell the agent uses |
| DEP-007 | The adapter passes unit tests but not inside the agent | Tests cover the decision layer, not the host hook pipeline | Add one end-to-end blocked-action test inside the actual agent runtime | Confirm the protected action never happens, not just that the adapter returned `blocked` |
| DEP-008 | Logs are missing or permission errors appear | Log directory is treated as a file, blocked by sandbox policy, or outside the workspace | Use a workspace-local log directory and create it before enforcement | Verify the JSONL event file is written after both pass and block cases |
| DEP-009 | Memory isolation appears to work but cross-project data leaks | Memory roots are broad, symbolic paths are unresolved, or the agent reads memory before the gate | Use resolved absolute roots and run memory isolation before payload reads | Test allowed root, sibling-prefix blocked root, and cross-lane blocked root |
| DEP-010 | Final answer still overclaims weak evidence | The claim gate lacks the actual final response body | Pass final text into the final-answer gate, or downgrade final claims when final text cannot be checked | Test a final sentence containing a strong claim and confirm it blocks or is downgraded |
| DEP-011 | External research rules are skipped for current facts | Search gate is advisory and not connected to dynamic re-evaluation | Trigger search gate on currentness, version, GitHub, legal, policy, price, or release-date claims | Ask for a latest/current version claim and verify the route demands external evidence |
| DEP-012 | Hooks stop working after a client update | Client paths, hook names, bundled runtimes, or config schema changed | Run adapter smoke tests after every client update before trusting enforcement | Use the update smoke checklist in `docs/adoption.md` |
| DEP-013 | Public repository examples leak local settings | Local hook configs or personal paths were committed | Keep product-specific local settings out of the public package; publish templates only | Scan docs and examples for local paths, private project names, and credential-like fields |
| DEP-014 | Everything becomes slow after adoption | The adapter wraps every tool call or loads all memory/skills by default | Keep L0/L1 cheap and use event-triggered expansion; hard-wrap only critical risks | Compare ordinary read-only task latency before and after adoption |
| DEP-015 | `--fail-open` remains enabled | Setup diagnostics were left in production mode | Remove fail-open flags after first-time hook setup | Force a hook-runner error and confirm high-risk pre-tool calls fail closed |
| DEP-016 | Human confirmation becomes too broad | Host or model treats one confirmation as future authority | Bind confirmation to the exact current action in the governing host flow; ACCF correction must not carry or create permission | Confirm a later or changed action still requires its own host-governed decision |
| DEP-017 | Built-in background actions bypass gates | The agent performs background indexing, auto-fixes, or hidden commands outside tool hooks | Identify background execution surfaces and mark unhooked surfaces advisory | Check runtime logs during startup, indexing, and automatic actions |
| DEP-018 | Tool input parsing misses dangerous commands | The command is nested under a tool-specific field not parsed by the adapter | Update the adapter to inspect the actual tool schema used by the host | Capture one real tool event JSON and verify hard patterns are detected |
| DEP-019 | Hook runner logs `codec can't encode character '\ud...'` | Host stdin JSON decoded to lone UTF-16 surrogate values, then output/logging writes them as Unicode | Sanitize hook payloads before routing and log/output writes; prefer ASCII-escaped hook output | Replay a captured hook payload with `\udcac` or `\udc80` and confirm routing still returns context |
| DEP-020 | Pre-tool blocking works, but the agent says it did not proactively route the task | Only the tool-stage hook is wired, or the prompt-stage hook failed before adding route context | Wire `UserPromptSubmit` or equivalent prompt-stage hook to store the original prompt and inject compact route context | Start a normal task and confirm the agent receives a compact routing receipt before tool planning |
| DEP-021 | Chinese or non-ASCII prompts become garbled in hook logs or route decisions | Hook shell or Python process is not forced to UTF-8, especially in Windows Git Bash or mixed Windows shells | Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` in hook wrappers; replay a Chinese trigger prompt | Confirm the route detects the original Chinese trigger text and the hook log is readable UTF-8 |
| DEP-022 | Write/Edit file content is blocked because it mentions high-risk words | A broad `PreToolUse` matcher sends non-command file payloads through command-pattern gating | Start with command-tool matchers such as `Bash|PowerShell`, or add a separate schema-aware policy for file tools | A document containing `delete`, `permission`, or `rm -rf` as text examples does not block a safe file edit |
| DEP-023 | Final answers still overclaim validation or verification | No Stop/final-answer hook is wired, or final text is not passed into the claim gate | Wire a Stop/final hook when the host exposes final text; otherwise mark final claims advisory and require self-downgrade wording | A final sentence with a strong validation claim and no claim schema blocks or is rewritten |
| DEP-024 | Voice or recording prompts do not affect routing | The host passes raw audio, file paths, blobs, or base64 data instead of a transcript field | Add host-side transcription and pass bounded text fields such as `transcript`, `transcription`, `caption`, `content`, `message`, or `text` | A recording whose transcript contains an R5 action produces an R5 route before planning |
| DEP-025 | Nested claim JSON works in direct tests but fails inside hooks | Multiple shells reinterpret quotes or escapes before the adapter receives JSON | Use a file-based handoff such as `--ClaimFile` or a JSON file path for nested claims | Replay a nested claim payload through the exact hook shell and confirm the parser receives the same JSON |
| DEP-026 | The agent continues an old conversation without reading the right memory lane | Conversation linking is advisory or the host never asks for a link decision before tools | Add a pre-action gate that blocks continuation, merge, archive, or cross-conversation memory tasks until meta-first lookup resolves the link | Ask to continue the previous conversation; the first protected tool call should block with `conversation_link_decision_required` until the link is selected |
| DEP-027 | A product-specific guide exists, but the installed client behaves differently | The guide is a reference mapping, not completed validation for that client version | Build a compatibility manifest from the actual client and run local acceptance tests | Do not claim hard enforcement until the installed client blocks a disposable high-risk action before execution |
| DEP-028 | Memory retrieval returns a plausible paragraph with no metadata | The retrieval backend or memory tool returns text snippets without source, provenance, belief status, or score-method fields | Require returned memories to include these fields before the agent can use them as reusable context: `source_tag` `derived_from` `belief_status` `confidence` `score_method` | A retrieved snippet without those fields is treated as unbounded context, not validated memory |
| DEP-029 | A shared memory server improves recall but leaks context across projects | The backend is shared across agents but not lane-scoped before retrieval and writing | Add project, conversation, and global lane IDs at write time; filter by lane before payload retrieval; keep cross-lane reads explicit | A query from project A cannot retrieve project B payloads unless the user explicitly requested cross-project lookup |
| DEP-030 | A Windows PowerShell command starts with Bash heredoc syntax such as `<<'PY'` | The agent generated a shell fragment before checking the actual executor dialect | Add an unconditional shell dialect preflight before multiline command generation; use PowerShell here-strings, temporary files, `-File`, or pipe-safe forms under PowerShell | A Python inline-script command generated for PowerShell contains no Bash heredoc syntax and succeeds without an initial syntax failure |

## Deployment Problem Examples And Solution Playbooks

These examples are written for the adopting user's agent. They are not product-specific guarantees. Use them as candidate solution paths, then verify the exact hook, wrapper, shell, and runtime behavior on the target machine.

### Example 1: Instruction File Exists But The Agent Ignores It

Symptom:

```text
The repository contains `AGENTS.md`, but the agent answers as if no framework instructions exist.
```

Check:

- Confirm which instruction filename the agent actually reads.
- Confirm the file is at the workspace root or configured path.
- Ask the agent for a compact routing receipt on a mixed-risk task.

Solution path:

1. Confirm that the installed client reads the repository's `AGENTS.md` or configured instruction path.
2. Keep the root file short enough to load reliably.
3. Put large memory, examples, and adapter details behind links or meta indexes.
4. Re-run the routing receipt test.

Acceptance check:

```text
A task that includes edit + benchmark + commit is not treated as ordinary chat, and commit still requires explicit confirmation.
```

### Example 2: Hook Returns Blocked But Tool Still Executes

Symptom:

```text
Hook logs show status=blocked, but the shell command or tool action still runs.
```

Check:

- Is the hook attached to a pre-action event, or only a post-action event?
- Does the host require a specific denial payload, exception type, or exit code?
- Is the command executed through a different tool path than the one matched by the hook?

Solution path:

1. Move the gate to the earliest pre-tool or pre-command surface.
2. Match the host's required denial schema exactly.
3. Return the host-supported blocked exit code or raised exception.
4. Add a disposable blocked-action test.
5. Mark any unhooked paths as advisory.

Acceptance check:

```text
The blocked action does not happen. Do not count the test as passed just because the hook printed blocked.
```

### Example 3: Pre-Tool Hook Loses The Original User Task

Symptom:

```text
PreToolUse receives only a compact value such as R5, or only the tool command, so memory/search/claim routing is wrong.
```

Check:

- Does the prompt-stage payload expose the original user text?
- Is a session id available in both prompt and pre-tool events?
- Does the adapter store prompt state in a workspace-local state file?

Solution path:

1. Add a prompt-stage hook that stores `session_id`, `cwd`, original task text, and compact receipt.
2. During pre-tool checks, reload the stored task by session id.
3. Pass both the compact risk override and the original task text into the model-facing decision router, and separately into any adopter-owned host-native enforcer if one exists.
4. If the host has no prompt-stage event, state that automatic route injection is unavailable; direct model-layer loading may still provide the pre-action stop.

Acceptance check:

```text
The pre-tool log shows the original task, not only the tool command and not only a risk label.
```

### Example 4: File Edits Are Blocked Because The File Mentions Dangerous Words

Symptom:

```text
A safe documentation edit is denied because the file content contains examples such as delete, permission, or rm -rf.
```

Check:

- Is a broad `*` pre-tool matcher sending file-write payloads into a command-pattern gate?
- Does the gate distinguish command fields from document content fields?
- Is the tool a command executor or a file editor?

Solution path:

1. Start hard enforcement with command-tool matchers such as `Bash`, `PowerShell`, `Shell`, or `Command`.
2. Inspect only command-like fields for command risk.
3. Add a separate file-tool policy if file edits need hard enforcement.
4. Keep documentation examples from being interpreted as attempted commands.

Acceptance check:

```text
A file edit that merely documents rm -rf is allowed, while an actual shell command `rm -rf build` is blocked without confirmation.
```

### Example 5: Current Facts And GitHub Claims Skip Search

Symptom:

```text
The agent claims a latest version, release status, GitHub behavior, license fact, or policy fact without current sources.
```

Check:

- Does the router detect `latest`, `current`, `release`, `GitHub`, `repo`, `issue`, `license`, `policy`, or `price`?
- Is the external research gate connected to dynamic re-evaluation?
- Does the final answer separate source-prior facts from local validation?

Solution path:

1. Route official/current facts to official or authority sources first.
2. Route GitHub claims to README, source tree, releases/changelog, issues, and license surfaces.
3. Record source date and boundary.
4. Do not upgrade external reading into `local_validated` until a local check or reproduction confirms it.

Acceptance check:

```text
The final answer says what was externally sourced, what was locally verified, and what remains unverified.
```

### Example 6: Conversation Continuation Reads The Wrong Memory

Symptom:

```text
The user asks to continue the previous conversation, but the agent opens the globally newest memory or an unrelated project memory.
```

Check:

- Is there a lane-scoped conversation index?
- Are active, paused, sealed, archived, merged, and superseded states represented?
- Does the adapter require link decision resolution before tools?

Solution path:

1. Read the current project or PROJECTLESS conversation index first.
2. Filter out sealed, archived, merged, and superseded memories.
3. Sort active candidates by `updated_at` inside the active lane only.
4. If ambiguous, ask the user to choose from a few summaries.
5. Create a link-only continuation by default; do not write into the old memory unless explicitly requested.
6. If a pre-tool hook exists, block protected tool calls until the link decision is resolved.

Acceptance check:

```text
An unresolved continuation blocks with conversation_link_decision_required; after the selected memory is resolved, the same action proceeds.
```

### Example 7: Final Answer Still Says Validated Without Evidence

Symptom:

```text
The final message says validated, verified, stable, or proven, but there is no claim schema or evidence boundary.
```

Check:

- Can the runtime inspect final text before display?
- Does the claim gate receive `final_text`?
- Are claim type, source type, source reference, and evidence boundary present for strong claims?

Solution path:

1. Wire a Stop/final-answer hook when the host supports it.
2. Pass final response text into the claim gate.
3. If no final hook exists, require the agent to self-downgrade claims in the root instruction file.
4. Use `validated` only for locally verified checks, not for source-prior or partial smoke results.

Acceptance check:

```text
A strong final claim without evidence schema blocks, or the agent downgrades it before display.
```

### Example 8: Hook Fails On Non-ASCII Or Recording Payloads

Symptom:

```text
The hook fails with a UTF-8 encoding error, or a voice/recording prompt routes as ordinary chat.
```

Check:

- Does stdin JSON contain lone surrogate escapes such as `\udcac` or `\udc80`?
- Are hook wrappers forcing UTF-8 mode?
- Does the payload contain transcript text, or only raw audio/base64/file path data?

Solution path:

1. Sanitize nested strings before routing, logging, state writes, and output.
2. Use ASCII-escaped hook output when the host shell is fragile.
3. Set `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` for Python hook runners.
4. Add host-side transcription and pass bounded fields such as `transcript`, `transcription`, `caption`, `content`, `message`, or `text`.
5. Ignore raw media blobs inside the harness adapter unless a separate permission policy exists.

Acceptance check:

```text
A payload with malformed surrogate text does not crash the hook, and a recording transcript containing a high-risk action routes before planning.
```

### Example 9: Windows PowerShell Parses Policy JSON Incorrectly

Symptom:

```text
ConvertFrom-Json fails on policy files that contain non-ASCII trigger text, even though Python can parse the JSON.
```

Check:

- Is the PowerShell gate using default `Get-Content -Raw` encoding?
- Does the file contain non-ASCII triggers or comments copied from docs?
- Are all policy readers patched, or only the validator?

Solution path:

1. Use explicit UTF-8 reads in every PowerShell policy reader.
2. Search all scripts for `Get-Content ... ConvertFrom-Json`.
3. Keep machine policy JSON parseable in the exact shell that will execute it.
4. Validate the standalone validator and intake router; validate any adopter-owned host-native enforcer separately.

Acceptance check:

```text
The validator and intake router parse the same policy file in the target shell. Any adopter-owned host-native enforcer has its own explicit compatibility check.
```

### Example 10: Windows PowerShell Receives Bash Heredoc Syntax

Symptom:

```text
A command generated for Windows PowerShell starts with `<<'PY'` or another
Bash heredoc form, then fails before the intended Python or script body runs.
```

Check:

- Which shell will execute the command: PowerShell, cmd, Bash, POSIX sh, or an
  agent-owned wrapper?
- Does the generated command use syntax from a different shell dialect?
- Is this a multiline or inline script where a temporary file or `-File` would
  be safer?

Solution path:

1. Run shell dialect preflight before emitting multiline commands.
2. Use Bash heredocs only for Bash or POSIX sh executors.
3. Under Windows PowerShell, use here-strings, temporary files, `-File`, or
   pipe-safe command forms.
4. Treat this as an execution-layer rule; do not rely on memory or CE lookup to
   remember the correction after the first failure.

Acceptance check:

```text
The first generated PowerShell command for an inline Python/script body uses
PowerShell-compatible syntax and does not fail once with Bash heredoc parsing.
```

### Example 11: Client Update Silently Breaks The Adapter

Symptom:

```text
The harness worked before, then stopped after the agent client updated.
```

Check:

- Did the instruction file path change?
- Did hook names, hook payload schema, or denial semantics change?
- Did the bundled Python, Node, Bash, or command path change?
- Did the client reset workspace settings?

Solution path:

1. Re-run instruction-load, allowed-action, blocked-action, and hook payload tests.
2. Refresh the compatibility manifest with the checked client version and adapter version.
3. Re-confirm wrapper paths and environment variables.
4. Treat enforcement as unverified until the blocked-action test passes again.

Acceptance check:

```text
After the update, the same disposable blocked action is still stopped before execution.
```

### Example 12: Memory Backend Returns Unbounded Context

Symptom:

```text
The agent recalls a useful-looking memory, but the result does not say where it came from or whether it was verified.
```

Check:

- Does the memory result include `source_tag` `derived_from` `belief_status` `confidence` `score_method`?
- Is `score_method` only ranking relevance, or is it incorrectly used as truth evidence?
- Was the query filtered by project or conversation lane before payload retrieval?

Solution path:

1. Treat text-only retrieval as unbounded context, not as memory evidence.
2. Require a result envelope with source-monitoring fields.
3. Use `score_method: none` when no numeric score is provided, and omit `score`.
4. Keep raw observations separate from current guidance.
5. Filter by lane before opening payloads from a shared backend.

Acceptance check:

```text
The agent can explain whether a retrieved memory is raw observation, working memory, capsule, or archive, and whether it is source_prior, bounded_claim, local_validated, conflicted, or rejected.
```

## Agent-Facing Troubleshooting Runbook

When an adopting agent reports "the harness is deployed but it does not behave like a hard gate", do not guess from repository files alone. Check the actual runtime path in this order.

### 1. Confirm The Instruction Entry Is Loaded

Inspect:

- workspace root `AGENTS.md` and configured instruction paths;
- agent settings page or config file that declares instruction paths;
- the first agent response after a test prompt.

Test:

```text
Ask the agent: "Classify this task with the harness routing receipt: edit code, run a benchmark, then commit."
```

Expected:

- the response mentions a routing receipt or equivalent route;
- risk is not treated as ordinary chat;
- R5 actions such as commit require explicit confirmation.

If this fails, fix the instruction entry before debugging hooks.

### 2. Confirm The Gate Works Outside The Agent

Inspect:

- harness root path;
- policy file path;
- Python, PowerShell, Bash, or Node runtime availability;
- adapter logs and standard output.

Test the gate directly from the same workspace:

```text
Run the intake router directly with a known mixed-risk task. If the adopter also has host-native enforcement, test that independent path with a disposable action.
```

Expected:

- ACCF returns the expected risk, gates, and mandatory pre-action confirmation need;
- the optional correction path only rewrites a mechanically verified current input;
- any host-native enforcement test uses the host's documented denial schema and exit behavior.

If direct execution fails, the problem is adapter setup, dependencies, policy JSON, quoting, or file paths. Do not debug the agent hook yet.

### 3. Confirm The Hook Command Runs In The Agent's Real Shell

Inspect:

- hook settings or hook UI;
- the exact command string stored in the agent config;
- the shell used by the hook runner;
- `cwd`, `PATH`, Python launcher, Bash availability, and environment variables exposed inside hooks.

Test:

```text
Run the exact hook command from the same shell style the agent uses.
```

Expected:

- the hook command can import the adapter;
- it can read stdin JSON;
- it can write its log directory;
- it returns the same decision as the direct gate test.

If direct gate works but the hook command fails, the problem is shell quoting, path expansion, missing environment variables, executable permissions, or runtime discovery.

### 4. Capture One Real Hook Event Payload

Inspect:

- hook debug logs;
- the harness JSONL log file;
- event fields such as event name, session id, cwd, tool name, and tool input;
- state file used to preserve the original prompt.
- raw stdin JSON when the hook runner reports decoding or encoding errors.

Expected fields:

```text
hook event name
session id or conversation id
cwd / workspace root
tool name
tool input
original user task or stored prompt state
transcript or transcription text when the user used voice/recording input
```

If the payload lacks the original task, add a prompt-stage hook that stores it. If the tool command is nested in an unexpected field, update the adapter to parse that field.

If the payload contains invalid Unicode such as lone surrogate escapes (`\udcac`, `\udc80`), sanitize nested strings before routing, state writes, JSONL logging, or hook output. Do not rely on the host to clean these values.

If the payload contains raw audio, a recording file path, base64 media, or bytes without transcript text, the harness cannot route the spoken content. Add transcription at the host layer, then pass the transcript through a bounded text field.

### 5. Confirm The Host Honors The Blocked Result

Inspect:

- hook return payload;
- process exit code;
- host documentation for deny/block semantics;
- agent runtime logs around the tool call.

Test:

```text
Use a disposable workspace and attempt a known blocked action through the normal agent path.
```

Expected:

```text
hook runs before tool execution
hook returns blocked / deny
hook exits with the host-supported blocked code
tool does not execute
```

If the hook returns blocked but the tool still runs, the issue is not the harness policy. The host is ignoring the hook result, the hook is attached to the wrong event, or that specific tool path bypasses hooks.

### 6. Search For Bypass Paths

Inspect every action surface the agent can use:

- shell command execution;
- file edit tools;
- package installation tools;
- browser or network tools;
- memory read/write tools;
- background indexing or auto-fix tasks;
- built-in commit, deploy, or project-management actions;
- secondary terminals or remote runners.

For each surface, classify it:

```text
model-layer pre-action-gated
host hard-gated
advisory receipt only
not covered
unknown, needs test
```

Do not claim full host hard enforcement while any protected action still has an
untested or known bypass path. A verified model-layer stop may still be claimed
at its own layer when the agent demonstrably halted before action formation.

### 7. Check Memory, Search, And Final-Claim Stages Separately

These are often not the same hook as tool execution.

Inspect:

- memory root resolution and meta-index lookup;
- external research trigger route;
- final answer or output gate;
- whether final text is available before display.

Tests:

```text
Memory: allowed memory path passes, sibling or cross-lane path blocks.
Search: latest/current/GitHub/release-date task routes to external research.
Final claim: strong claim without evidence schema blocks or is downgraded.
```

If these fail while pre-tool blocking works, the tool hook is deployed but the memory/search/final-answer surfaces are not.

### 8. Diagnose By Failure Boundary

Use this decision tree:

| Observation | Boundary | Likely fix |
| --- | --- | --- |
| Direct gate fails | adapter/policy/runtime | Fix dependencies, policy JSON, script path, or shell quoting. |
| Direct gate passes, hook command fails | hook shell/environment | Fix hook command path, env vars, Python/Bash launcher, cwd, or quoting. |
| Hook command passes, agent tool still runs | host integration | Move hook to the pre-execution event or use the host's required denial schema / exit code. |
| One tool blocks, another bypasses | coverage | Wire every protected tool surface or document uncovered paths as advisory. |
| Prompt route is correct, pre-tool route is wrong | state transfer | Store original prompt at prompt-submit time and reload it during pre-tool checks. |
| File edits block because of text examples | matcher/tool-schema boundary | Narrow command gates to command tools and add separate schema-aware file gates only when needed. |
| Voice tasks route as ordinary chat | media payload boundary | Confirm the hook receives transcript text rather than only raw audio or a file path. |
| Final overclaims still display | final-answer boundary | Wire a Stop/final hook or mark final-claim enforcement advisory for that runtime. |
| Tests pass until client update | drift | Re-check client version, hook schema, paths, bundled runtimes, and settings format. |

## Mainstream Agent Checklist

Use this checklist when deploying or revalidating the framework in Codex.

1. **Instruction entry:** which file or setting is actually read by the agent?
2. **Prompt stage:** is there a prompt-submit or pre-task surface where routing can store the original task?
3. **Tool stage:** is there a pre-tool hook, tool proxy, middleware, or command wrapper that runs before the action?
4. **Block semantics:** does the host support a denial payload, nonzero exit code, raised exception, or policy decision that stops execution?
5. **Bypass surfaces:** can the agent still run shell, file, browser, network, package-manager, or memory actions through another path?
6. **State preservation:** can pre-tool checks access the original user task, cwd, session id, project lane, and receipt?
7. **Final answer surface:** can the final response text be checked before display? If not, require self-downgrade language.
8. **Memory surface:** are memory reads/writes routed through meta-first and lane-isolation checks?
9. **External facts:** are currentness and GitHub/open-source triggers connected to a real research route?
10. **Media input surface:** when the user speaks or uploads a recording, does the hook payload include transcript text rather than raw audio only?
11. **Update drift:** what smoke test runs after the agent client updates?

## Minimal Acceptance Tests

Run these before claiming that the harness is deployed in an agent runtime:

1. **Instruction load test:** ask the agent to classify a mixed-risk task and report a compact routing receipt.
2. **Allowed action test:** run a harmless read-only command through the normal agent path and confirm it proceeds.
3. **Blocked action test:** in a disposable workspace, attempt a known high-risk action and confirm it is stopped before execution.
4. **Bypass test:** try the other tool surfaces the agent can use and document which are hard-gated versus advisory.
5. **Memory isolation test:** test one allowed memory path and one sibling-prefix or cross-lane blocked path.
6. **Current fact test:** ask for a latest/current or GitHub/release claim and confirm the external research route is triggered.
7. **Final claim test:** attempt a strong claim without evidence schema and confirm it blocks or downgrades.
8. **Transcript route test:** if the runtime supports voice or recording input, pass a recording transcript with a known R5 action and confirm it routes before planning.
9. **Client update test:** after updating the agent client, re-run tests 1 through 4 at minimum.

## Public Documentation Rule

Public deployment docs should describe reusable setup patterns and templates, not one maintainer's private configuration. Do not publish local settings files, private project paths, real memory records, personal machine paths, credentials, auth values, or screenshots that reveal local state.

When a product-specific behavior has not been tested on the adopter's exact version, say so. Use wording such as:

```text
This adapter was tested as a local decision layer. Protected high-risk actions
use a mandatory model-layer pre-action stop. Independent host hard enforcement
depends on your agent runtime honoring the pre-tool hook or wrapper result.
```
