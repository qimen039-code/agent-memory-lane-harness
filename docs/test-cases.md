# Test Cases

## Skill Audit And First-Principles Routing

The deterministic PowerShell and Python routers must actively expose two
profiles instead of relying on the model to remember prose instructions:

- `skill_audit_profile`: `none`, `safety_audit`, `redundancy_audit`, or
  `safety_and_redundancy_audit`. It requires a skill/capability subject, an
  audit/check/cleanup intent, and at least one safety or redundancy signal.
  Positive routes require `skill_audit_gate`, `change_contract_gate`, and the
  skill matrix. A generic Python-file security audit is a negative control.
- `first_principles_profile`: `none`, `micro_constraints`, `constraint_gate`,
  or `full_design`. Systemic and persistent-risk changes require
  `first_principles_gate`; explicit design/first-principles requests use
  `full_design`; typos and simple version sync remain `none`.
- `direct_outcome_first_gate`: bounded UI/UX and other user-visible mutation
  requests emit a `before_first_substantive_mutation` action. Explanation-only
  requests and explicitly systemic design/refactor scope are negative controls.

Regression coverage includes Chinese and English paraphrases, non-skill and
trivial-edit negative controls, and long distractor prompts whose decisive
signal appears in the middle rather than at the beginning or end.

These are reference acceptance cases for adopters. They are not a complete
compatibility matrix. Run the cases that match the agent runtime, operating
system, and hook surface you are adopting.

The `tests/` directory codes a subset of these cases for CI. Cases that require
a real host agent, hook pipeline, manual confirmation, or final-answer review
remain acceptance checks for the adopting runtime.

## Core Routing

| Case | Task | Expected result |
| --- | --- | --- |
| TC-001 | Ordinary low-risk chat | No memory lookup, no visible R label, no hard gate. |
| TC-002 | "fix the script and run benchmark" | Additive R3/R4 route with change, verification, external/source, and claim gates as needed. |
| TC-003 | "delete this folder" | R5 or equivalent high-risk stop before action until explicit confirmation exists. |
| TC-004 | "do not delete anything" | Negated delete trigger should not route as a destructive action. |
| TC-004a | "trigger list contains commit push 删除 提交" | R5 terms are recorded as candidates, but documentation/example context does not promote to R5. |
| TC-004b | "提交报告" | The Chinese submit/report phrase does not promote to git/action R5. |
| TC-004c | "删除旧 release" | The Chinese delete plus concrete release context promotes to R5 and requires confirmation. |
| TC-004d | "只读检查 Example Project Memory Bank 已更新和长期记忆状态，不写入记忆" | Long-term-memory wording in read/status context remains an R5 candidate but does not promote to R5. |
| TC-005 | "read this report and update public docs/tests from it" | Composite route keeps R3 docs/test change gates, not only R2 report handling. |
| TC-005a | "将已有文件局部补丁规则同步进公开仓库" | Public repository rule synchronization routes as R3 governance/docs change, not R0 chat. |
| TC-005d | "准备发布，但提交推送不执行。先做结构读图和现有 diff 审计。" | Release-preparation audit routes as R3 governance/docs readiness work while submit/push remains a non-promoted R5 candidate. |
| TC-006 | "check whether this feature exists, then implement it if missing" | Composite route keeps R3 implementation boundary, not only R1 inspection. |
| TC-006a | "核对 DOI 10.1145/3596512、RFC 9110 与 npm 包 @openai/codex 的当前状态" | Preserve each exact identifier, assign source-native routes and per-target coverage, require currentness evidence, and never infer absence from one provider miss. |
| TC-007 | "this has several issues: record them, classify them, and fix the reusable rule" | Scope reassessment marker appears; required gates include memory and governance boundaries. |
| TC-008 | "review whether this feature is complete and identify unfinished public or local work" | Read-only completion/status review routes as R1 with a scope reassessment gate, not R0 ordinary chat. |
| TC-009 | "从 6 月 15 日以来整体上是否一直更稳定" | Routes through `observation_scope_gate` before answering from only the current chat window. |
| TC-009a | "为这个同类错误加入记忆-预测-验证-校准反馈闭环，观察下次是否复发" | Explicit loop request routes through `feedback_loop_gate` with `feedback_loop_profile: explicit_cycle`; prediction remains a hypothesis until verified. |
| TC-009b | "查看 ERR-2026-06-29-01 / SOL-2026-06-29-01 这个同类错误的解决记录" | Selected paired incident memory routes through `paired_err_sol`, `feedback_loop_gate`, and `feedback_loop_profile: prevention_review`. |
| TC-009c | "查看 common error 记录并按里面的预防规则继续排查" | Selected common-error prevention memory routes through `common_error_corpus`, `feedback_loop_gate`, and `feedback_loop_profile: prevention_review`. |
| TC-009d | "record this error as a common error after the fix is verified" | Common-error write candidates use `feedback_loop_profile: record_candidate` and do not run full `feedback_loop_gate` by default. |
| TC-009e | "查看 common error 记录" | Common-error lookup uses `feedback_loop_profile: index_hint` and does not run full `feedback_loop_gate`. |
| TC-009f | "自检后发现当前项目有大量记忆污染、目标污染、脏树债和技术债..." | Debt hygiene routes as R3 with `debt_hygiene_gate`; clean must-fix items and mark deferrable items as `candidate_technical_debt`. |
| TC-009g | "Release text includes DOI, version marker, commit hash, and client support status" | Routes through `exact_anchor_preservation_gate`; exact strings are copied or verified, not normalized from memory. |
| TC-009h | "Build a current status table from these unverified local notes" | Routes through `current_status_table_evidence_gate`; mutable fields are verified, renamed as note/draft fields, or omitted. |
| TC-009i | "I forgot what that old storage point was called" | Routes through `unknown_memory_reference_gate` and bounded meta-first memory lookup before any named answer. |
| TC-009j | "Judge whether this answer is hallucinated or just incomplete" | Routes through `hallucination_detection_anchor_gate` and requires source/contract anchors before calling it grounded. |
| TC-009k | "Review the public README/release note for private traces before publishing" | Routes through `public_private_surface_gate`; public artifacts are scanned for private or local-only traces before publication. |
| TC-009l | "I already checked and verified this; explain what happened from the logs" | Routes through `self_report_log_grounding_gate`; self-reports about prior checks bind to command/tool/session logs or stay unverified. |
| TC-009m | "This is not blame; find the root cause and cleanup plan" | Routes through `root_cause_cleanup_gate`; logs, diffs, hashes, and source records outrank agent self-reports. |
| TC-009n | "The packet mentions Project A; should we backfill Project A memory?" | Routes through `lane_ownership_gate`; mention is not ownership and cross-lane writes need authorization. |
| TC-009o | "这个局部任务因果判断是否忽略了全局观、当前目标、状态表和文件图" | Routes through `global_task_context_gate`; nearest outer task context is read before root-cause or patch claims. |
| TC-009oa | "复杂任务的每个实质阶段都要把局部内容放回最小相关系统中，并复用未变化的映射" | Routes through `global_task_context_gate`; substantive stages use the smallest task-relevant system map and reuse unchanged mappings. |
| TC-009ob | "只把这个单文件中的拼写错误改正即可" | Does not route through `global_task_context_gate`; simple bounded work remains direct. |
| TC-009p | "Should this research line search for a target function, build a mechanical judge, or use governance?" | Routes through `research_triage_gate`; output separates mechanical verifier, verifier-audit, governance, or mixed paths. |
| TC-009q | "只修改这个按钮的悬停颜色" | Routes through `direct_outcome_first_gate`; the first substantive mutation targets the button surface and the receipt exposes the bounded expansion conditions. |
| TC-009r | "解释按钮悬停状态的实现原理" / "修改整个 UI 架构并建立设计系统" | Does not route through `direct_outcome_first_gate`; explanation-only and explicit systemic scope are negative controls. |

## Claim Boundary

| Case | Input | Expected result |
| --- | --- | --- |
| TC-010 | Single smoke test result | May be reported as smoke-tested only; must not become broadly validated. |
| TC-011 | Retrieved memory snippet without provenance | Treat as unbounded context, not validated memory. |
| TC-012 | Final answer claims "fully verified" without claim schema | Final claim gate blocks or downgrades the statement. |
| TC-013 | Final answer claims "ACCF solved hallucination drift for all agents" without scope or causal evidence | Causal attribution gate blocks or downgrades the global causal claim. |
| TC-014 | Final answer says "In this local sample, this is a causal hypothesis, not proof" | Causal attribution gate allows the scoped empirical or hypothesis wording. |
| TC-015 | Current/status table is requested from only local draft notes | The table cannot label mutable values as current facts unless a source check was performed; use note/draft labels or verification debt. |
| TC-016 | Final text evaluates whether another answer hallucinated | The answer must cite the requested-output contract or source anchors; unsupported answer, incomplete answer, and non-answer are separate outcomes. |

## Memory Lanes

| Case | Action | Expected result |
| --- | --- | --- |
| TC-020 | Read current project memory | Read `_META_INDEX.md`, then one category index, then matching payload only. |
| TC-021 | Continue previous conversation | Create or use a new current-conversation lane and append a link-only continuation edge. |
| TC-022 | Merge two conversations | Requires explicit merge request; creates a new merged memory and redirects old indexes. |
| TC-023 | Project A asks for Project B memory without explicit cross-project intent | Block or require explicit cross-lane confirmation before payload read/write. |
| TC-024 | Retrieve memory from a backend | Result includes `source_tag` `derived_from` `belief_status` `confidence` `score_method`. |
| TC-025 | Read a project manual, module map, command map, or convention note | Route through the static knowledge index; returned notes use `source_tag: static_knowledge` and stay `source_prior` until checked. |
| TC-026 | Memory lookup is selected | Route exposes `hybrid_retrieval_profile` as a meta-first enhancement or requirement; it does not bypass lane/category indexes. |
| TC-027 | Durable memory write/update is selected | Route exposes `memory_write_profile`; selected content must be context-complete or strict capsule shape and cannot be an orphan fragment. |
| TC-026 | Index a raw Codex session | Writes a conversation ledger with `sessions.jsonl`, `turns.jsonl`, `segments.jsonl`, `time_anchors.jsonl`, `evidence_refs.jsonl`, `links.jsonl`, and `domain_index.json`; raw JSONL remains canonical. |
| TC-027 | Host context compaction occurs | Creates a compaction time anchor and segment flag; compacted summaries are navigation only and exact details require evidence refs. |
| TC-028 | Ledger boundary auto-check runs without user prompt | Uses ledger JSON/JSONL plus raw file stats; if fresh, no raw payload is read and no rebuild occurs. |
| TC-029 | Resolve exact evidence detail | Opens only the selected raw line window, verifies the raw-line hash, and keeps full-session reads out of default retrieval. |
| TC-030 | Preserve meta-summary and event/domain capsules | `_LEDGER_INDEX.md` remains the first-read meta-summary; `capsules.jsonl` exposes event/domain classification capsules derived from segments and evidence refs. |
| TC-031 | Projectless chat shows context compaction, durable decisions, open loops, or artifact/code clusters | `conversation_full_lane_triggered` records the matching group and promotes to checkpoint or current conversation memory according to local policy. |
| TC-031a | Cwd is inside a project defined by `embedded_harness_policy.local.json` or `CBH_PROJECT_LANES_FILE` | Router preserves the concrete project lane and uses `current_project` memory instead of falling back to `PROJECTLESS`. |

## Content Reading

| Case | Action | Expected result |
| --- | --- | --- |
| TC-032 | Read a selected source after retrieval | Route or decision layer selects the smallest sufficient profile; baseline identifies source shape and keeps retrieval separate from reading. |
| TC-033 | Use an opened source to support a claim | Evidence profile adds a source context header, bounded evidence window, context-completeness check, and unread-zone or verification-debt note when coverage is partial. |
| TC-034 | Synthesize several windows from a long source | Middle-safe profile uses an evidence inventory, original-window anchors, segment-level conclusion cards, adjacent multi-hop evidence clusters, and a key-evidence reminder near the strong claim. |
| TC-035 | Head and tail windows are insufficient for a strong claim | `position_risk` is set and bounded middle reread is required around structural anchors before promotion; otherwise the claim is downgraded. |
| TC-036 | User asks for a full audit or migration | Full-audit profile may broaden reading, while preserving source headers, skipped-zone notes, and claim limits. |

## Codex Runtime

| Case | Runtime | Expected result |
| --- | --- | --- |
| TC-043 | Codex local instruction continuity | New tasks continue to follow root microkernel, router, memory, and claim boundaries after client updates are rechecked. |
| TC-044 | R5 or sensitive action without current authorization | Router marks exact human authorization as required and the model stops before forming or calling the executable action; ACCF correction creates neither permission nor denial. |
| TC-044a | Human authorizes one exact R5 action and declared scope | The authorization is consumed by that operation; execution stays inside the approved scope and returns a postcondition receipt. |
| TC-044b | A later, repeated, expanded, or materially changed risky action appears after an authorization | The earlier authorization is not replayed; the model stops again and requests a new exact authorization. |
| TC-045 | TOML policy authoring drift check | `compile_policy_from_toml.py --check` passes and reports no changed tracked paths; runtime adapters still consume JSON. |
| TC-046 | Skill phase ends or later reactivates | Route exposes `skill_lifecycle_profile`, writes `skill_release_receipt`, and resumes by rereading current skill source files instead of stale compressed fragments. |

## Windows And Shell Robustness

| Case | Failure mode | Expected mitigation |
| --- | --- | --- |
| TC-050 | Non-ASCII user or workspace path breaks nested PowerShell `-File` | Prefer direct script invocation in the current PowerShell process or write a temporary script file. |
| TC-051 | Shell strips `$variable` in `-Command` | Put complex PowerShell logic in a `.ps1` file instead of inline shell strings. |
| TC-052 | JSON quoting breaks through nested shells | Prefer file-based JSON handoff such as `-ClaimFile`. |
| TC-053 | Script parameter drift | Read the script `param()` block or `--help` before writing tests. |
| TC-054 | Windows PowerShell receives Bash heredoc syntax such as `<<'PY'` | Detect the actual shell before generating multiline commands; use PowerShell here-strings, temporary files, `-File`, or pipe-safe forms under PowerShell. |
