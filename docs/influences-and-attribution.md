# Influences And Attribution

Agent Cognitive Continuity Framework is a composed framework. Some parts are independent
design choices in this repository, and some parts are adapted from public
projects or established engineering patterns. This page keeps that boundary
explicit.

External references are source-prior inputs. They are useful for design,
terminology, and validation ideas, but they do not prove this framework works in
an adopting runtime until local smoke checks pass.

`CREDITS.toml` is the machine-readable companion to this page. Keep public
external influences there; do not use it for private discussions or local
deployment notes.

## Public GitHub Influences

| Source | Absorbed or adapted ideas | Boundary |
| --- | --- | --- |
| mattpocock/skills `codebase-design`: https://github.com/mattpocock/skills/tree/main/skills/engineering/codebase-design | The deletion thought experiment, adapted by CBH into a reversible freeze/temporary-isolation probe, and the rule that one adapter is a hypothetical seam while two independent adapters make it real. | The CBH probe itself performs no mutation; an external executor must restore state and provide an audit receipt. Tracer-bullet delivery and invocation topology are local CBH profiles, not attributed to this source. CBH does not vendor the full skill collection, authorize deletion, add a second scheduler, or treat one adapter with multiple providers as two independent seams. |
| rohitg00/agentmemory: https://github.com/rohitg00/agentmemory | Lifecycle hook coverage, explicit memory command semantics, memory retrieval metadata pressure, and client-update hook drift concerns. | This repository does not require an external memory backend, memory server, vector database, automatic cross-agent shared memory, or automatic memory mutation. Project, conversation, common-error, and archive lanes remain isolated. |
| LanNguyenSi/harness: https://github.com/LanNguyenSi/harness | Declarative control-plane vocabulary, adapter compatibility thinking, evidence-ledger and policy/enforcement separation ideas. | This repository does not require its manifest format, CLI, Rego-like policy layer, generated runtime config, or always-on hook enforcement. |
| trustgraph-ai/trustgraph: https://github.com/trustgraph-ai/trustgraph | Portable context packaging and explicit load-state inspiration, plus workspace-root structural isolation as a narrow memory-integrity pattern. CBH adapts these ideas into its existing capsule, lane, source-validity, and cached-hash contracts. | This repository does not adopt TrustGraph's Pulsar/microservice stack, graph or vector databases, GraphRAG platform, agent orchestration, thought storage, Flow Blueprint runtime, or default full candidate-route recording. TrustGraph remains a source-prior, not local validation. |
| epicsagas/epic-harness: https://github.com/epicsagas/epic-harness | Hook health, pipeline state, multi-tool harness framing, and self-improvement as a staged maintenance concern. | This repository does not adopt always-on self-evolution, autonomous spec-to-PR behavior, or unified memory as the default. |
| ChatBotKit template-node-agent-cli-js: https://github.com/chatbotkit/template-node-agent-cli-js | Tool schema, CLI-agent structure, and structured command-output inspiration. | This repository does not depend on ChatBotKit or its SDK. |
| Anthropic Contextual Retrieval: https://www.anthropic.com/news/contextual-retrieval | Chunk-level context pressure informed the source context header and bounded evidence-window reading contract. | This repository does not require Claude-generated contextual chunks, embeddings, vector databases, BM25, rerankers, prompt caching, or generated chunk context as a fact source. |
| Liu et al., "Lost in the Middle": https://arxiv.org/abs/2307.03172 | Position sensitivity in long contexts informed the middle-safe evidence layout, position-risk marker, and bounded middle-reread gate. | This repository does not claim to solve model attention behavior, add positional training, or rely on blind long-context stuffing. |

## Established Pattern Influences

| Pattern | Absorbed idea | Boundary |
| --- | --- | --- |
| Policy decision point / policy enforcement point separation | Keep routing decisions separate from actual execution or blocking. | This is not a complete policy engine and does not become a sandbox unless the adopting runtime honors the gate. |
| Admission-control style hooks | Check critical actions before persistence or execution. | Only critical risks should be hard-gated; ordinary tools stay low cost. |
| Append-only ledgers | Keep decision, error, solution, and rejected-edit records auditable. | Records are lightweight files, not a database by default. |
| Structured provenance | Carry source, confidence, and derivation fields with reusable memory. | Provenance fields do not make a claim true; they preserve the evidence boundary. |
| Meta-first retrieval | Read summaries and indexes before opening deep payloads. | This is a retrieval discipline, not a guarantee of semantic correctness. |
| Project manuals and wiki-style knowledge bases | Keep stable module maps, commands, conventions, and interface notes close to the repository. | Static notes are source-prior orientation aids until checked against files, tests, or other evidence. |
| Structural causal models and do-calculus, including Judea Pearl's causal-graph work: https://arxiv.org/abs/1210.4852 | Separate observation, intervention, counterfactual-style reasoning, and causal-effect claims. This informs the four-level causal-attribution boundary. | ACCF does not perform formal causal identification or claim statistical causal proof from text alone. |
| Systems thinking and system dynamics, including Meadows/Forrester-style feedback, stock/flow, delay, and leverage-point framing | Prevent local symptoms from being treated as the whole system; inform `global_task_context_gate` and root-cause cleanup boundaries. | ACCF does not build a simulation model or prove system dynamics; it only routes agents to read outer task context before local causal claims. |
| Situation awareness research, including Endsley's perception/comprehension/projection model | Treat current task state, active lane, goal, and projection of next effects as part of the context needed before action. | ACCF does not measure human situation awareness; it adapts the pattern into an agent task-context check. |
| Long-context position-sensitivity research, including Liu et al. "Lost in the Middle": https://arxiv.org/abs/2307.03172 | Position risk, middle-safe reading, and evidence-window design. | ACCF does not solve model attention bias; it uses bounded rereading and evidence placement as a mitigation. |

## Project Contributions

The repository's own contribution is the combined boundary contract and runnable
whiteboard package:

- a claim-boundary vocabulary that separates source-prior, bounded claim,
  local validation, conflict, and rejection states;
- a low-cost router receipt that decides memory, external search, skill,
  claim, and runtime-gate needs before opening larger context;
- project, conversation, common-error, and archive memory lanes with explicit
  cross-lane boundaries;
- retrieval-result requirements that carry `source_tag` `derived_from`
  `belief_status` `confidence` `score_method`;
- an optional static knowledge layer that adapts wiki-style project manuals into
  indexed, source-prior, claim-bounded agent context;
- task-local, verifier-bound behavior correction that remains nonblocking and
  separate from host authorization;

Those contributions are a composition and adaptation layer, not a claim that
each underlying mechanism was invented here.
