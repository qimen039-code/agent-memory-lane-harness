from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
import tomllib


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HARNESS = ROOT / "skills" / "embedded-harness"
HARNESS = PUBLIC_HARNESS if PUBLIC_HARNESS.is_dir() else ROOT
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from task_continuity import (  # noqa: E402
    apply_task_event,
    build_dynamic_reminders,
    build_task_capsule_context,
    decide_task_continuity,
    initialize_task_capsule,
    new_task_capsule,
    page_result,
    plan_transport,
    process_worker_request,
)


def event(event_id: str, event_type: str, **payload: object) -> dict[str, object]:
    return {
        "schema": "cbh.task_event.v1",
        "event_id": event_id,
        "type": event_type,
        "observed_at": "2026-08-13T00:00:00Z",
        **payload,
    }


def write_route() -> dict[str, object]:
    return {
        "edit_operation_profile": "in_place_patch",
        "memory_mode": "none",
        "tool_surface_need": "local_filesystem",
        "action_bindings": [],
    }


def test_short_answer_only_question_stays_dormant() -> None:
    decision = decide_task_continuity(
        {
            "edit_operation_profile": "read_only",
            "memory_mode": "none",
            "tool_surface_need": "none",
            "action_bindings": [],
        },
        event("answer:1", "task_observed", objective="什么是检索增强生成？"),
    )

    assert decision == {
        "schema": "cbh.task_continuity_decision.v1",
        "decision": "dormant",
        "reasons": [],
        "source_event_ids": ["answer:1"],
        "host_delivery": "not_needed",
    }


def test_initial_write_intent_arms_even_when_turn_relation_is_ambiguous() -> None:
    decision = decide_task_continuity(
        {
            "edit_operation_profile": "none",
            "memory_mode": "none",
            "tool_surface_need": "none",
            "action_bindings": [],
        },
        event(
            "initial-write:1",
            "task_observed",
            objective="修改并验证专用动态投影",
            intent_kind="ambiguous",
            intent_confidence="low",
            intent_source="fallback",
        ),
    )

    assert decision["decision"] == "arm"
    assert decision["reasons"] == ["write_intent", "tool_required"]
    assert decision["host_delivery"] == "ready"


def test_existing_active_capsule_uses_contract_continue_decision() -> None:
    route = write_route()
    capsule = new_task_capsule(
        route,
        event("start:1", "task_observed", objective="修复文件"),
    )
    decision = decide_task_continuity(
        route,
        event("observe:2", "task_observed", objective="继续修复"),
        capsule,
    )
    assert decision["decision"] == "continue"


def test_first_substantive_event_is_applied_when_capsule_is_created() -> None:
    capsule, transition = initialize_task_capsule(
        write_route(),
        event(
            "write:first",
            "write_result_received",
            objective="写入并验证文件",
            acceptance_id="write_applied",
            postcondition_satisfied=False,
        ),
    )
    assert transition is not None
    assert capsule["lifecycle"] == "VERIFYING"
    assert capsule["acceptance_criteria"][0]["status"] == "inferred"
    assert "write:first" in capsule["applied_event_ids"]


def test_plan_progress_is_separate_from_the_acceptance_contract() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "plan:start",
            "task_observed",
            objective="实现并验证功能",
            acceptance_criteria=[
                {"id": "delivery_verified", "text": "交付物通过独立验证"},
            ],
        ),
    )
    transition = apply_task_event(
        capsule,
        event(
            "plan:update",
            "progress_snapshot",
            plan_steps=[
                {"id": "plan-0", "text": "实现功能", "status": "inferred"},
                {"id": "plan-1", "text": "运行验证", "status": "unknown"},
            ],
            current_step="运行验证",
            next_action="运行验证",
        ),
    )
    updated = transition["capsule"]
    assert updated["lifecycle"] == "ACTIVE"
    assert updated["next_action"] == "运行验证"
    assert not updated["verified_completed"]
    assert updated["acceptance_criteria"] == [
        {
            "id": "delivery_verified",
            "text": "交付物通过独立验证",
            "status": "unknown",
        }
    ]
    assert updated["plan_steps"] == [
        {"id": "plan-0", "text": "实现功能", "status": "inferred"},
        {"id": "plan-1", "text": "运行验证", "status": "unknown"},
    ]


def test_unmatched_active_turn_preserves_the_global_goal_as_a_local_delta() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "global:start",
            "task_observed",
            objective="修复连续工作记忆并完成统一验证",
            purpose="长对话中始终围绕整体目标执行",
            acceptance_criteria=[{"id": "verified", "text": "整体修复经过验证"}],
        ),
    )

    response = process_worker_request(
        {
            "op": "observe",
            "route_receipt": write_route(),
            "task_event": event(
                "global:delta",
                "task_observed",
                objective="其他的呢，为什么刚才的上下文不见了",
                intent_kind="ambiguous",
                intent_confidence="low",
                intent_source="fallback",
                intent_reason_codes=["active_turn_relation_unresolved"],
            ),
            "capsule": capsule,
        }
    )

    updated = response["capsule"]
    assert updated["capsule_id"] == capsule["capsule_id"]
    assert updated["objective"] == "修复连续工作记忆并完成统一验证"
    assert updated["global_goal_anchor"]["objective"] == updated["objective"]
    assert updated["active_local_delta"]["turn_ref"] == "global:delta"
    assert updated["turn_relation"] == {
        "kind": "ambiguous",
        "confidence": "low",
        "source": "fallback",
        "reason_codes": ["active_turn_relation_unresolved"],
        "reviewed_against": {
            "capsule_id": capsule["capsule_id"],
            "goal_revision": 1,
        },
    }
    assert updated["semantic_review_required"] is True


def test_repeated_bounded_side_questions_preserve_one_global_frame_and_request_turn_adjudication() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "side-chat:start",
            "task_observed",
            objective="完成连续记忆修复、验证并发布小版本",
            next_action="运行最终验证",
        ),
    )
    original_id = capsule["capsule_id"]
    original_anchor = capsule["global_goal_anchor"]

    for index, question in enumerate(("顺便问一下今天星期几？", "那明天呢？"), start=1):
        response = process_worker_request(
            {
                "op": "observe",
                "route_receipt": write_route(),
                "task_event": event(
                    f"side-chat:{index}",
                    "task_observed",
                    objective=question,
                    intent_kind="ambiguous",
                    intent_confidence="low",
                    intent_source="fallback",
                    intent_reason_codes=["active_turn_relation_unresolved"],
                ),
                "capsule": capsule,
                "host_limits": {"max_chars": 3000, "max_tokens": 850},
            }
        )
        capsule = response["capsule"]

    control = json.loads(response["additional_context_entries"]["control"]["value"].split("\n", 1)[1])
    assert capsule["capsule_id"] == original_id
    assert capsule["global_goal_anchor"] == original_anchor
    assert capsule["suspended_task_stack"] == []
    assert capsule["semantic_review_required"] is True
    assert control["required_action_code"] == "adjudicate_current_turn_without_replacing_global_goal"
    assert control["turn_relation_options"] == [
        "global_goal_delta",
        "bounded_side_conversation",
        "explicit_global_replacement",
    ]
    assert control["bounded_side_conversation_policy"] == "answer_current_turn_then_keep_global_goal_resumable"


def test_explicit_return_to_global_task_clears_transient_semantic_review() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("return:start", "task_observed", objective="完成原有长期任务"),
    )
    ambiguous = apply_task_event(
        capsule,
        event(
            "return:side",
            "task_observed",
            objective="临时问一个无关问题",
            intent_kind="ambiguous",
            intent_confidence="low",
            intent_source="fallback",
        ),
    )["capsule"]
    resumed = apply_task_event(
        ambiguous,
        event(
            "return:resume",
            "task_observed",
            objective="回到刚才的主任务，继续",
            intent_kind="continue_ack",
            intent_confidence="high",
            intent_source="explicit_marker",
            reviewed_against={
                "capsule_id": ambiguous["capsule_id"],
                "goal_revision": ambiguous["goal_revision"],
            },
        ),
    )["capsule"]

    assert resumed["capsule_id"] == capsule["capsule_id"]
    assert resumed["objective"] == "完成原有长期任务"
    assert resumed["semantic_review_required"] is False
    assert resumed["turn_relation"]["kind"] == "continue_ack"


def test_unbound_fallback_new_task_cannot_supersede_an_active_global_goal() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("guard:start", "task_observed", objective="完成原有整体任务"),
    )

    response = process_worker_request(
        {
            "op": "observe",
            "route_receipt": write_route(),
            "task_event": event(
                "guard:unbound",
                "task_observed",
                objective="一句措辞不同的局部问题",
                intent_kind="new_task",
                intent_confidence="medium",
                intent_source="fallback",
                intent_reason_codes=["independent_substantive_turn"],
            ),
            "capsule": capsule,
        }
    )

    assert response["capsule"]["capsule_id"] == capsule["capsule_id"]
    assert response["capsule"]["objective"] == "完成原有整体任务"
    assert response["capsule"]["semantic_review_required"] is True
    assert response["transition"]["transition_reasons"] == [
        "global_goal_preserved_pending_semantic_review"
    ]


def test_only_current_revision_bound_explicit_replacement_supersedes() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("replace:start", "task_observed", objective="完成旧整体任务"),
    )
    request = {
        "op": "observe",
        "route_receipt": write_route(),
        "task_event": event(
            "replace:explicit",
            "task_observed",
            objective="放弃旧目标，改为完成新的整体任务",
            intent_kind="new_task",
            intent_confidence="high",
            intent_source="explicit_marker",
            intent_reason_codes=["explicit_global_replacement"],
            reviewed_against={
                "capsule_id": capsule["capsule_id"],
                "goal_revision": capsule["goal_revision"],
            },
        ),
        "capsule": capsule,
    }

    replaced = process_worker_request(request)["capsule"]
    assert replaced["capsule_id"] != capsule["capsule_id"]
    assert replaced["objective"] == "放弃旧目标，改为完成新的整体任务"
    assert replaced["supersedes_capsule_id"] == capsule["capsule_id"]
    assert replaced["state_version"] == 3

    stale_request = json.loads(json.dumps(request, ensure_ascii=False))
    stale_request["task_event"]["event_id"] = "replace:stale"
    stale_request["task_event"]["reviewed_against"]["goal_revision"] = 0
    preserved = process_worker_request(stale_request)["capsule"]
    assert preserved["capsule_id"] == capsule["capsule_id"]
    assert preserved["semantic_review_required"] is True


def test_side_task_pushes_and_pops_without_replacing_the_global_goal() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("side:start", "task_observed", objective="完成连续记忆修复"),
    )
    side = process_worker_request(
        {
            "op": "observe",
            "route_receipt": write_route(),
            "task_event": event(
                "side:push",
                "task_observed",
                objective="先确认一个独立的小问题，之后继续原任务",
                intent_kind="side_task",
                intent_confidence="high",
                intent_source="explicit_marker",
                intent_reason_codes=["explicit_temporary_side_task"],
                reviewed_against={
                    "capsule_id": capsule["capsule_id"],
                    "goal_revision": capsule["goal_revision"],
                },
            ),
            "capsule": capsule,
        }
    )["capsule"]

    assert side["objective"] == "完成连续记忆修复"
    assert side["active_local_delta"]["kind"] == "side_task"
    assert side["suspended_task_stack"][-1]["resume_entry"]["global_objective"] == "完成连续记忆修复"

    resumed = apply_task_event(
        side,
        event("side:pop", "side_task_completed", postcondition_satisfied=True),
    )["capsule"]
    assert resumed["objective"] == "完成连续记忆修复"
    assert resumed["suspended_task_stack"] == []
    assert resumed["active_local_delta"]["kind"] == "resume"


def test_model_context_is_global_first_and_does_not_duplicate_current_turn_text() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("order:start", "task_observed", objective="完成稳定的整体目标"),
    )
    updated = apply_task_event(
        capsule,
        event(
            "order:local",
            "task_observed",
            objective="这一句只应作为局部增量",
            intent_kind="ambiguous",
            intent_confidence="low",
            intent_source="fallback",
        ),
    )["capsule"]
    context = build_task_capsule_context(updated, [])
    payload = json.loads(context["entry"]["value"].split("\n", 1)[1])

    assert payload["reading_order"][0] == "global_goal_anchor"
    assert payload["global_goal_anchor"]["objective"] == "完成稳定的整体目标"
    assert payload["active_local_delta"]["turn_ref"] == "order:local"
    assert "text" not in payload["active_local_delta"]
    assert "这一句只应作为局部增量" not in context["entry"]["value"]


def test_reusable_exact_source_triggers_reuse_before_regenerate() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "reuse:start",
            "task_observed",
            objective="更新已有配置",
            reuse_candidates=[
                {
                    "record_id": "artifact-existing",
                    "path": "C:/fixture/existing.toml",
                    "sha256": "a" * 64,
                    "eligible_for_current_reuse": True,
                }
            ],
        ),
    )
    transition = apply_task_event(
        capsule,
        event("reuse:select", "candidate_selected", current_step="准备配置内容"),
    )
    reminders = build_dynamic_reminders(transition["capsule"], transition)

    assert reminders[0]["trigger"] == "reuse_before_regenerate"
    context = build_task_capsule_context(
        reminders[0]["capsule_snapshot"],
        [{key: value for key, value in reminders[0].items() if key != "capsule_snapshot"}],
    )
    assert "C:/fixture/existing.toml" in context["entry"]["value"]


def test_new_substantive_task_supersedes_stale_working_set() -> None:
    stale = new_task_capsule(
        write_route(),
        event(
            "stale:start",
            "task_observed",
            objective="修复旧版 R5 路由",
            acceptance_criteria=[{"id": "old-r5", "text": "旧 R5 修复完成"}],
        ),
    )
    stale = apply_task_event(
        stale,
        event(
            "stale:failure",
            "unchanged_dispatch_repeated",
            subject_signature="old-dispatch",
            error_class="host_error_observed",
        ),
    )["capsule"]

    response = process_worker_request(
        {
            "op": "observe",
            "route_receipt": {
                "edit_operation_profile": "read_only",
                "memory_mode": "none",
                "tool_surface_need": "none",
                "action_bindings": [],
            },
            "task_event": event(
                "fresh:start",
                "task_observed",
                objective="比较数据库记忆与语义文件记忆",
                intent_kind="new_task",
                intent_confidence="high",
                intent_source="explicit_marker",
                intent_reason_codes=["explicit_global_replacement"],
                reviewed_against={
                    "capsule_id": stale["capsule_id"],
                    "goal_revision": stale["goal_revision"],
                },
            ),
            "capsule": stale,
        }
    )

    fresh = response["capsule"]
    assert fresh["capsule_id"] != stale["capsule_id"]
    assert fresh["objective"] == "比较数据库记忆与语义文件记忆"
    assert fresh["supersedes_capsule_id"] == stale["capsule_id"]
    assert fresh["unresolved_failures"] == []
    assert "旧 R5 修复完成" not in response["additional_context_entry"]["value"]


def test_continue_ack_does_not_replace_the_active_goal() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("ack:start", "task_observed", objective="修复并验证工作记忆"),
    )

    response = process_worker_request(
        {
            "op": "observe",
            "route_receipt": write_route(),
            "task_event": event(
                "ack:continue",
                "task_observed",
                objective="可以，继续",
                intent_kind="continue_ack",
            ),
            "capsule": capsule,
        }
    )

    assert response["capsule"]["objective"] == "修复并验证工作记忆"
    assert response["capsule"]["last_user_delta"] == {
        "kind": "continue_ack",
        "text": "可以，继续",
        "turn_ref": "ack:continue",
    }


def test_all_verified_acceptance_items_retire_without_adapter_flag() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "auto-retire:start",
            "task_observed",
            objective="完成并验证唯一交付物",
            acceptance_criteria=[{"id": "done", "text": "交付物已验证"}],
        ),
    )

    verified = apply_task_event(
        capsule,
        event(
            "auto-retire:verified",
            "verifier_completed",
            acceptance_id="done",
            postcondition_satisfied=True,
        ),
    )["capsule"]

    assert verified["lifecycle"] == "RETIRED"
    assert verified["retirement"] == {
        "outcome": "completed",
        "reason": "all_acceptance_items_verified",
        "evidence_refs": [],
    }


def test_retirement_preserves_bounded_structured_evidence_references() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "structured-ref:start",
            "task_observed",
            objective="核验一条可回钻证据",
            acceptance_criteria=[{"id": "verified", "text": "证据已核验"}],
        ),
    )
    evidence_ref = {
        "source_id": "codex-session:abc",
        "resolved_path": "C:/archive/session.jsonl",
        "line": 42,
        "line_sha256_16": "0123456789abcdef",
        "status": "relocated_verified",
        "raw_payload": "must-not-be-persisted",
    }
    retired = apply_task_event(
        capsule,
        event(
            "structured-ref:verified",
            "verifier_completed",
            acceptance_id="verified",
            postcondition_satisfied=True,
            evidence_refs=[evidence_ref],
        ),
    )["capsule"]

    expected = {key: value for key, value in evidence_ref.items() if key != "raw_payload"}
    assert retired["evidence_refs"] == [expected]
    assert retired["retirement"]["evidence_refs"] == [expected]


def test_refinement_and_correction_are_source_bound_goal_deltas() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("delta:start", "task_observed", objective="实现并验证工作记忆"),
    )

    refined = apply_task_event(
        capsule,
        event(
            "delta:refine",
            "task_observed",
            objective="再补充重启后的精确恢复",
            intent_kind="refine",
        ),
    )["capsule"]
    corrected = apply_task_event(
        refined,
        event(
            "delta:correction",
            "task_observed",
            objective="不对，恢复时必须校验最新 head",
            intent_kind="correction",
        ),
    )["capsule"]

    assert corrected["objective"] == "实现并验证工作记忆"
    assert corrected["goal_revision"] == 3
    assert corrected["goal_deltas"] == [
        {
            "kind": "refine",
            "text": "再补充重启后的精确恢复",
            "source_ref": "delta:refine",
        },
        {
            "kind": "correction",
            "text": "不对，恢复时必须校验最新 head",
            "source_ref": "delta:correction",
        },
    ]


def test_context_epoch_changes_only_for_global_or_validity_changes() -> None:
    initial_anchor = {
        "schema": "cbh.workspace_fact_anchor.v1",
        "workspace_id_sha256": "a" * 64,
        "source": "git",
        "git_head": "1" * 40,
        "git_branch": "main",
        "worktree_state_sha256": "b" * 64,
        "observed_at": "2026-08-24T00:00:00Z",
    }
    capsule = new_task_capsule(
        write_route(),
        event(
            "epoch:start",
            "task_observed",
            objective="保持全局目标并完成验证",
            workspace_anchor=initial_anchor,
        ),
    )
    initial_epoch = capsule["context_epoch"]["epoch_id"]

    progress_transition = apply_task_event(
        capsule,
        event(
            "epoch:progress",
            "tool_dispatched",
            current_step="读取实现",
            workspace_anchor={
                **initial_anchor,
                "worktree_state_sha256": "c" * 64,
                "observed_at": "2026-08-24T00:01:00Z",
            },
            workspace_change_expected=True,
        ),
    )
    progressed = progress_transition["capsule"]
    assert progressed["context_epoch"]["epoch_id"] == initial_epoch
    assert progressed["workspace_review_required"] is False
    assert build_dynamic_reminders(progressed, progress_transition) == []

    refined = apply_task_event(
        progressed,
        event(
            "epoch:refine",
            "task_observed",
            objective="再补充一项明确验收标准",
            intent_kind="refine",
            workspace_anchor={
                **initial_anchor,
                "worktree_state_sha256": "c" * 64,
                "observed_at": "2026-08-24T00:02:00Z",
            },
        ),
    )["capsule"]
    assert refined["context_epoch"]["epoch_id"] != initial_epoch
    context = build_task_capsule_context(refined, [])
    payload = json.loads(context["entry"]["value"].split("\n", 1)[1])
    control = json.loads(context["control_entry"]["value"].split("\n", 1)[1])
    assert payload["context_epoch_id"] == refined["context_epoch"]["epoch_id"]
    assert control["context_epoch_id"] == refined["context_epoch"]["epoch_id"]


def test_unexpected_workspace_change_keeps_goal_but_invalidates_old_progress() -> None:
    initial_anchor = {
        "schema": "cbh.workspace_fact_anchor.v1",
        "workspace_id_sha256": "a" * 64,
        "source": "git",
        "git_head": "1" * 40,
        "git_branch": "main",
        "worktree_state_sha256": "b" * 64,
        "observed_at": "2026-08-24T00:00:00Z",
    }
    capsule = new_task_capsule(
        write_route(),
        event(
            "workspace:start",
            "task_observed",
            objective="修改并验证目标文件",
            acceptance_criteria=[
                {"id": "verified", "text": "目标文件已验证"},
                {"id": "final-review", "text": "最终状态已复核"},
            ],
            workspace_anchor=initial_anchor,
        ),
    )
    verified = apply_task_event(
        capsule,
        event(
            "workspace:verified",
            "verifier_completed",
            acceptance_id="verified",
            postcondition_satisfied=True,
            workspace_anchor=initial_anchor,
            workspace_change_expected=True,
        ),
    )["capsule"]
    prior_epoch = verified["context_epoch"]["epoch_id"]

    changed_transition = apply_task_event(
        verified,
        event(
            "workspace:changed",
            "task_observed",
            objective="继续",
            intent_kind="continue_ack",
            workspace_anchor={
                **initial_anchor,
                "git_head": "2" * 40,
                "worktree_state_sha256": "d" * 64,
                "observed_at": "2026-08-24T01:00:00Z",
            },
        ),
    )
    changed = changed_transition["capsule"]

    assert changed["objective"] == "修改并验证目标文件"
    assert changed["acceptance_criteria"][0]["status"] == "verified"
    assert changed["workspace_review_required"] is True
    assert changed["workspace_review_reason"] == "workspace_anchor_changed"
    assert changed["context_epoch"]["epoch_id"] != prior_epoch
    context = build_task_capsule_context(changed, [])
    assert "workspace_revalidation_required" in context["control_entry"]["value"]
    assert "workspace_fact_status" in context["entry"]["value"]
    reminders = build_dynamic_reminders(changed, changed_transition)
    assert reminders[0]["trigger"] == "workspace_revalidation_required"
    assert reminders[0]["context_epoch_id"] == changed["context_epoch"]["epoch_id"]

    revalidated = apply_task_event(
        changed,
        event(
            "workspace:revalidated",
            "verifier_completed",
            acceptance_id="final-review",
            postcondition_satisfied=True,
            workspace_anchor=changed["workspace_anchor"],
            workspace_change_expected=True,
            workspace_revalidated=True,
        ),
    )["capsule"]
    assert revalidated["workspace_review_required"] is False
    assert revalidated["workspace_review_reason"] is None
    assert revalidated["context_epoch"]["epoch_id"] != changed["context_epoch"]["epoch_id"]


def test_working_frame_preserves_goal_outputs_purpose_and_stop_condition() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "frame:start",
            "task_observed",
            objective="实现可靠的短期连续记忆",
            purpose="让模型始终知道为什么做、做到什么程度",
            required_outputs=[
                {"id": "runtime", "text": "可恢复的工作记忆运行时"},
                {"id": "tests", "text": "真实复发回归测试"},
            ],
            acceptance_criteria=[
                {"id": "latest-head", "text": "只恢复校验后的最新 head"},
            ],
            stop_condition="实现与回归均通过后停止扩张",
        ),
    )
    context = build_task_capsule_context(capsule, [], host_limits={"max_chars": 3_200})

    assert capsule["purpose"] == "让模型始终知道为什么做、做到什么程度"
    assert capsule["required_outputs"] == [
        {"id": "runtime", "text": "可恢复的工作记忆运行时", "status": "unknown"},
        {"id": "tests", "text": "真实复发回归测试", "status": "unknown"},
    ]
    assert capsule["stop_condition"] == "实现与回归均通过后停止扩张"
    assert "可恢复的工作记忆运行时" in context["entry"]["value"]
    assert "让模型始终知道为什么做、做到什么程度" in context["entry"]["value"]
    assert "实现与回归均通过后停止扩张" in context["entry"]["value"]


def test_dispatched_action_is_bound_to_the_earliest_acceptance_item() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "action:start",
            "task_observed",
            objective="实现并验证工作记忆",
            acceptance_criteria=[
                {"id": "behavior-fixed", "text": "旧目标不再污染新任务"},
                {"id": "tests-green", "text": "真实复发测试通过"},
            ],
        ),
    )

    active = apply_task_event(
        capsule,
        event(
            "action:dispatch",
            "tool_dispatched",
            current_step="修改连续记忆 reducer",
        ),
    )["capsule"]

    assert active["current_action"] == {
        "text": "修改连续记忆 reducer",
        "serves_output_ids": [],
        "serves_criterion_ids": ["behavior-fixed"],
        "reason": "serves_acceptance_criterion:behavior-fixed",
    }


def test_retired_capsule_cannot_be_reactivated_by_a_late_event() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "retire:start",
            "task_observed",
            objective="完成一个动作",
            acceptance_criteria=[{"id": "done", "text": "done"}],
        ),
    )
    verified = apply_task_event(
        capsule,
        event(
            "retire:verify",
            "verifier_completed",
            acceptance_id="done",
            postcondition_satisfied=True,
            retire_if_complete=True,
        ),
    )["capsule"]
    late = apply_task_event(
        verified,
        event("retire:late", "candidate_selected", next_action="must not run"),
    )
    assert late["capsule"]["lifecycle"] == "RETIRED"
    assert late["changed"] is False
    assert late["event_outcome"] == "retired_ignored"


def test_host_task_identity_prevents_cross_task_event_contamination() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("identity:start", "task_observed", task_key="thread-a", objective="修改 A"),
    )
    with pytest.raises(ValueError, match="task_identity_mismatch"):
        apply_task_event(
            capsule,
            event("identity:wrong", "tool_dispatched", task_key="thread-b"),
        )


@pytest.mark.parametrize(
    ("route", "task_event", "reason"),
    [
        (write_route(), event("write:1", "task_observed", objective="修改 README"), "write_intent"),
        (
            {
                "edit_operation_profile": "read_only",
                "tool_surface_need": "browser",
                "action_bindings": [],
            },
            event("tool:1", "task_observed", objective="检查这个网页"),
            "tool_required",
        ),
        (
            {"edit_operation_profile": "read_only", "action_bindings": []},
            event("long:1", "task_observed", objective="分三阶段完成并持续验证", multi_stage=True),
            "multi_stage_task",
        ),
        (
            {"edit_operation_profile": "read_only", "action_bindings": []},
            event("resume:1", "task_observed", objective="继续之前未完成的任务", resume=True),
            "task_resume",
        ),
    ],
)
def test_write_tool_long_and_resume_tasks_arm(
    route: dict[str, object], task_event: dict[str, object], reason: str
) -> None:
    decision = decide_task_continuity(route, task_event)

    assert decision["decision"] == "arm"
    assert reason in decision["reasons"]
    assert decision["host_delivery"] == "ready"


def test_runtime_reasons_are_declared_by_the_policy_contract() -> None:
    authoring = tomllib.loads(
        (HARNESS / "embedded_harness_policy.authoring.toml").read_text(encoding="utf-8")
    )
    declared = set(
        authoring["router_decision_contract"]["task_continuity_contract"][
            "activation_reasons"
        ]
    )
    probes = [
        (write_route(), event("reason:write", "task_observed", objective="修改文件")),
        ({"tool_surface_need": "web"}, event("reason:tool", "task_observed", objective="检查网页")),
        ({}, event("reason:multi", "task_observed", objective="分阶段完成", multi_stage=True)),
        ({}, event("reason:resume", "task_observed", objective="继续", resume=True)),
        ({}, event("reason:long", "task_observed", objective="执行", long_running=True)),
        ({}, event("reason:open", "task_observed", objective="任务", open_loops=["x"])),
        ({}, event("reason:prior", "task_observed", objective="任务", prior_failure=True)),
        ({}, event("reason:explicit", "task_observed", objective="任务", continuity_requested=True)),
    ]
    emitted: set[str] = set()
    for route, task_event in probes:
        emitted.update(decide_task_continuity(route, task_event)["reasons"])
    capsule = new_task_capsule(write_route(), event("reason:active", "task_observed", objective="修改"))
    emitted.update(decide_task_continuity({}, event("reason:next", "task_observed", objective="任务"), capsule)["reasons"])
    assert emitted <= declared
    assert declared <= emitted


def test_write_capsule_requires_both_application_and_verification() -> None:
    observed = event(
        "write:observed",
        "task_observed",
        objective="更新配置并确认解析成功",
        acceptance_criteria=[
            {"id": "write_applied", "text": "目标写入已应用"},
            {"id": "write_verified", "text": "写入结果已验证"},
        ],
    )
    capsule = new_task_capsule(write_route(), observed)
    assert capsule["lifecycle"] == "ARMED"

    active = apply_task_event(
        capsule,
        event("write:selected", "candidate_selected", next_action="应用最小补丁"),
    )["capsule"]
    assert active["lifecycle"] == "ACTIVE"

    applied = apply_task_event(
        active,
        event(
            "write:result",
            "write_result_received",
            outcome="completed",
            acceptance_id="write_applied",
            postcondition_satisfied=True,
        ),
    )["capsule"]
    assert applied["lifecycle"] == "VERIFYING"
    assert [item["id"] for item in applied["verified_completed"]] == ["write_applied"]
    assert [item["id"] for item in applied["remaining_work"]] == ["write_verified"]

    verified = apply_task_event(
        applied,
        event(
            "write:verified",
            "verifier_completed",
            outcome="completed",
            acceptance_id="write_verified",
            postcondition_satisfied=True,
            retire_if_complete=True,
        ),
    )["capsule"]
    assert verified["lifecycle"] == "RETIRED"
    assert verified["remaining_work"] == []


def test_success_without_semantic_postcondition_is_only_inferred() -> None:
    capsule = new_task_capsule(
        {"tool_surface_need": "shell", "edit_operation_profile": "read_only"},
        event(
            "tool:observed",
            "task_observed",
            objective="检查项目状态",
            acceptance_criteria=[{"id": "status_checked", "text": "项目状态已核对"}],
        ),
    )
    capsule = apply_task_event(
        capsule,
        event("tool:dispatch", "tool_dispatched", next_action="运行状态检查"),
    )["capsule"]

    transition = apply_task_event(
        capsule,
        event(
            "tool:result",
            "tool_result_received",
            outcome="completed",
            acceptance_id="status_checked",
            postcondition_satisfied=False,
        ),
    )

    assert transition["capsule"]["verified_completed"] == []
    assert [item["id"] for item in transition["capsule"]["inferred_progress"]] == [
        "status_checked"
    ]
    assert transition["capsule"]["lifecycle"] == "VERIFYING"


def test_duplicate_event_is_idempotent() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("dup:observed", "task_observed", objective="修改一个文件"),
    )
    first = apply_task_event(capsule, event("dup:event", "tool_dispatched"))
    second = apply_task_event(first["capsule"], event("dup:event", "tool_dispatched"))

    assert first["changed"] is True
    assert second["changed"] is False
    assert second["capsule"] == first["capsule"]


def test_unchanged_failure_reminder_is_deduplicated_by_revision() -> None:
    capsule = new_task_capsule(
        {"tool_surface_need": "shell", "edit_operation_profile": "read_only"},
        event("failure:observed", "task_observed", objective="执行并验证命令"),
    )
    transition = apply_task_event(
        capsule,
        event(
            "failure:repeat",
            "unchanged_dispatch_repeated",
            subject_signature="a" * 64,
            error_class="parser_error",
        ),
    )
    first = build_dynamic_reminders(transition["capsule"], transition)
    second = build_dynamic_reminders(first[0]["capsule_snapshot"], transition)

    assert len(first) == 1
    assert first[0]["trigger"] == "unchanged_dispatch_repeated"
    assert second == []


def test_continuity_never_creates_or_consumes_authority() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("auth:observed", "task_observed", objective="执行受保护写入"),
    )
    transition = apply_task_event(
        capsule,
        event(
            "auth:pending",
            "verifier_pending",
            blocking_condition="pending_user_confirmation",
        ),
    )

    assert transition["capsule"]["lifecycle"] == "VERIFYING"
    assert transition["capsule"]["blocking_condition"] == "pending_user_confirmation"
    assert transition["capsule"]["authority"] == {
        "granted": False,
        "consumed": False,
        "source": "none",
    }


def test_text_transport_pages_round_trip_and_binds_cursor() -> None:
    payload = "甲乙丙丁" * 40
    plan = plan_transport(
        None,
        {"kind": "text", "original_chars": len(payload), "original_items": 1},
        {"max_chars": 37, "max_items": 10},
    )
    pages: list[str] = []
    cursor = None
    while True:
        page = page_result(payload, plan, cursor)
        pages.append(page["content"])
        if page["next_cursor"] is None:
            break
        cursor = page["next_cursor"]

    rebuilt = "".join(pages)
    assert rebuilt == payload
    assert hashlib.sha256(rebuilt.encode("utf-8")).hexdigest() == page["full_result_sha256"]
    assert all(len(part) <= 37 for part in pages)

    with pytest.raises(ValueError, match="cursor_result_hash_mismatch"):
        page_result(payload, plan, {"result_sha256": "0" * 64, "next_char": 1})


def test_item_transport_respects_item_and_character_limits() -> None:
    items = [{"id": index, "text": f"item-{index}"} for index in range(11)]
    plan = plan_transport(
        None,
        {"kind": "items", "original_items": len(items), "original_chars": 500},
        {"max_chars": 90, "max_items": 3},
    )
    rebuilt: list[dict[str, object]] = []
    cursor = None
    while True:
        page = page_result(items, plan, cursor)
        rebuilt.extend(page["items"])
        assert len(page["items"]) <= 3
        if page["next_cursor"] is None:
            break
        cursor = page["next_cursor"]

    assert rebuilt == items
    canonical = json.dumps(items, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha256(canonical.encode("utf-8")).hexdigest() == page["full_result_sha256"]


def test_typed_media_payload_is_never_serialized_into_context() -> None:
    secret = "base64-secret-payload"
    plan = plan_transport(
        None,
        {"kind": "items", "original_items": 1, "original_chars": 1000},
        {"max_chars": 1000, "max_items": 10},
    )
    page = page_result(
        [{"type": "image", "mimeType": "image/png", "data": secret}],
        plan,
    )
    serialized = json.dumps(page, ensure_ascii=False)

    assert secret not in serialized
    assert page["items"][0]["inline_payload_omitted_from_text"] is True


def test_model_context_contains_progress_not_chain_of_thought() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("context:observed", "task_observed", objective="修改并验证配置"),
    )
    context = build_task_capsule_context(capsule, [], host_limits={"max_chars": 1800})

    assert context["entry"]["kind"] == "untrusted"
    assert context["control_entry"]["kind"] == "application"
    assert "修改并验证配置" not in context["control_entry"]["value"]
    assert "continue_task_from_evidence_entry" in context["control_entry"]["value"]
    assert "修改并验证配置" in context["entry"]["value"]
    assert "chain-of-thought" not in context["entry"]["value"].lower()
    assert context["char_count"] <= 1800


def test_task_context_exposes_projection_identity_and_causal_relation() -> None:
    current = new_task_capsule(
        write_route(),
        event(
            "projection:start",
            "task_observed",
            objective="实现并验证运行时投影",
            acceptance_criteria=[
                {"id": "projection-verified", "text": "运行时投影已验证"},
            ],
        ),
    )
    current = apply_task_event(
        current,
        event(
            "projection:dispatch",
            "tool_dispatched",
            current_step="commandExecution",
        ),
    )["capsule"]
    context = build_task_capsule_context(current, [])
    evidence = json.loads(context["entry"]["value"].split("\n", 1)[1])
    control = json.loads(context["control_entry"]["value"].split("\n", 1)[1])

    assert len(evidence["runtime_projection_id"]) == 64
    assert len(control["runtime_projection_source_digest"]) == 64
    assert len(evidence["full_capsule_sha256"]) == 64
    assert evidence["causal_relation"] == {
        "status": "explicit_binding",
        "specificity": "host_kind_only",
        "serves_output_ids": [],
        "serves_criterion_ids": ["projection-verified"],
        "reason": "serves_acceptance_criterion:projection-verified",
    }
    assert control["runtime_projection_id"] == evidence["runtime_projection_id"]
    assert "实现并验证运行时投影" not in context["control_entry"]["value"]


def test_worker_returns_separate_small_dynamic_projection() -> None:
    current = new_task_capsule(
        write_route(),
        event(
            "dynamic:start",
            "task_observed",
            objective="修改并验证动态提醒投影",
            acceptance_criteria=[
                {"id": "postcondition", "text": "语义后置条件已验证"},
            ],
        ),
    )
    response = process_worker_request(
        {
            "op": "observe",
            "response_profile": "compact",
            "route_receipt": write_route(),
            "task_event": event(
                "dynamic:result",
                "tool_result_received",
                acceptance_id="postcondition",
                postcondition_satisfied=False,
            ),
            "capsule": current,
        }
    )

    dynamic = response["dynamic_context_entries"]
    dynamic_text = json.dumps(dynamic, ensure_ascii=False)
    normal_text = json.dumps(response["additional_context_entries"], ensure_ascii=False)
    assert dynamic["control"]["kind"] == "application"
    assert len(response["dynamic_projection_id"]) == 64
    assert dynamic["evidence"]["kind"] == "untrusted"
    assert "missing_postcondition" in dynamic_text
    assert "修改并验证动态提醒投影" not in dynamic_text
    assert len(dynamic_text) < len(normal_text)


def test_host_limit_fallback_keeps_global_goal_and_next_action_model_visible() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "context:host-limit",
            "task_observed",
            objective="在长期项目中保持整体目标、处理临时问答并完成发布",
            next_action="先判断当前输入与整体目标的关系",
            acceptance_criteria=[
                {"id": f"criterion-{index}", "text": "验收步骤 " + ("长内容" * 40)}
                for index in range(18)
            ],
        ),
    )
    ambiguous = apply_task_event(
        capsule,
        event(
            "context:host-limit-side",
            "task_observed",
            objective="临时问一个不相关的小问题",
            intent_kind="ambiguous",
            intent_confidence="low",
            intent_source="fallback",
        ),
    )["capsule"]

    context = build_task_capsule_context(
        ambiguous,
        [],
        host_limits={"max_chars": 1000, "max_tokens": 850},
    )
    evidence = json.loads(context["entry"]["value"].split("\n", 1)[1])

    assert evidence["global_goal_anchor"]["objective"] == "在长期项目中保持整体目标、处理临时问答并完成发布"
    assert evidence["next_action"] == ambiguous["next_action"]
    assert evidence["causal_relation"]["status"] in {
        "fallback_objective",
        "unresolved",
    }


def test_task_context_owns_host_limit_independently_from_internal_projection() -> None:
    current = new_task_capsule(
        write_route(),
        event(
            "context:projection-limit",
            "task_observed",
            objective="保持目标并完成验证",
            acceptance_criteria=[{"id": "done", "text": "完成验证"}],
        ),
    )
    context = build_task_capsule_context(
        current,
        [],
        host_limits={"max_chars": 800, "max_tokens": 850},
    )
    evidence = json.loads(context["entry"]["value"].split("\n", 1)[1])

    assert context["char_count"] <= 800
    assert evidence["global_goal_anchor"]["objective"] == "保持目标并完成验证"
    assert evidence["next_action"] == current["next_action"]
    assert evidence["next_action"]
    assert evidence["turn_relation"]["kind"] == "ambiguous"
    assert context["char_count"] <= 1000


def test_model_context_omits_empty_optionals_and_duplicate_initial_delta() -> None:
    """Catches token growth from serializing empty state and the objective twice."""

    capsule = new_task_capsule(
        write_route(),
        event(
            "context:compact",
            "task_observed",
            objective="修改并验证路由器",
            intent_kind="new_task",
            turn_ref="turn:compact",
        ),
    )
    context = build_task_capsule_context(capsule, [])
    payload = json.loads(context["entry"]["value"].split("\n", 1)[1])

    assert payload["objective"] == "修改并验证路由器"
    assert payload["remaining_work"]
    assert payload["next_action"]
    assert payload["full_capsule_sha256"]
    for redundant in (
        "constraints",
        "goal_deltas",
        "inferred_progress",
        "memory_working_set",
        "plan_steps",
        "reminders",
        "resume_entry",
        "uncovered_counts",
        "unresolved_failures",
        "verified_completed",
    ):
        assert redundant not in payload
    assert "last_user_delta" not in payload


def test_context_reports_unforwarded_progress_instead_of_silent_list_clipping() -> None:
    capsule = new_task_capsule(
        write_route(),
        event(
            "many:1",
            "task_observed",
            objective="完成多阶段写入",
            acceptance_criteria=[
                {"id": f"criterion-{index}", "text": f"step {index}"}
                for index in range(20)
            ],
        ),
    )
    context = build_task_capsule_context(capsule, [], host_limits={"max_chars": 3_200})
    assert "uncovered_counts" in context["entry"]["value"]
    assert "full_capsule_sha256" in context["entry"]["value"]


def test_pending_dynamic_reminder_is_rendered_on_the_next_supported_turn() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("reminder:start", "task_observed", task_key="thread-a", objective="修改文件"),
    )
    response = process_worker_request(
        {
            "op": "observe",
            "route_receipt": {},
            "task_event": event(
                "reminder:next",
                "task_observed",
                task_key="thread-a",
                objective="继续",
            ),
            "capsule": capsule,
            "pending_reminders": [
                {
                    "schema": "cbh.dynamic_reminder.v1",
                    "trigger": "missing_postcondition",
                    "required_action": "verify the semantic postcondition",
                    "expires_when": "postcondition_verified",
                }
            ],
            "host_limits": {"max_chars": 3000, "max_tokens": 850},
        }
    )
    assert "missing_postcondition" in response["additional_context_entry"]["value"]
    assert "verify the semantic postcondition" in response["additional_context_entry"]["value"]


def test_jsonl_worker_keeps_state_external_and_returns_one_context_entry() -> None:
    request = {
        "id": "worker:1",
        "op": "observe",
        "route_receipt": write_route(),
        "task_event": event("worker:event", "task_observed", objective="修改一个文件"),
        "capsule": None,
        "host_limits": {"max_chars": 1600, "max_items": 20},
    }
    completed = subprocess.run(
        [sys.executable, str(HARNESS / "task_continuity.py"), "--worker-once"],
        input=json.dumps(request, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response["id"] == "worker:1"
    assert response["result"]["decision"]["decision"] == "arm"
    assert response["result"]["capsule"]["lifecycle"] == "ARMED"
    assert response["result"]["additional_context_entry"]["kind"] == "untrusted"
    assert response["result"]["additional_context_entries"]["control"]["kind"] == "application"
    assert response["result"]["additional_context_entries"]["evidence"]["kind"] == "untrusted"


def test_compact_worker_response_removes_exact_duplicate_payloads() -> None:
    """Catches duplicate capsule/context copies in adapter-facing JSONL responses."""

    route = write_route()
    capsule = new_task_capsule(
        route,
        event("compact:start", "task_observed", objective="修改并验证文件"),
    )
    response = process_worker_request(
        {
            "op": "observe",
            "response_profile": "compact",
            "route_receipt": route,
            "task_event": event(
                "compact:progress",
                "progress_snapshot",
                plan_steps=[
                    {"id": "inspect", "text": "检查", "status": "completed"},
                    {"id": "patch", "text": "修改", "status": "in_progress"},
                    {"id": "verify", "text": "验证", "status": "pending"},
                ],
            ),
            "capsule": capsule,
            "host_limits": {"max_chars": 3_200, "max_tokens": 900},
        }
    )

    assert response["capsule"]["progress_revision"] == 2
    assert response["additional_context_entries"]["evidence"]["kind"] == "untrusted"
    assert response["transport_receipt"]["delivery"] in {
        "ready",
        "continuation_required",
    }
    transport = response["transport_receipt"]
    assert transport["total_char_count"] == (
        transport["evidence_char_count"] + transport["control_char_count"]
    )
    assert transport["total_estimated_tokens"] == (
        transport["evidence_estimated_tokens"]
        + transport["control_estimated_tokens"]
    )
    assert "additional_context_entry" not in response
    assert "capsule" not in response["transition"]


def test_page_result_reclamps_a_forged_oversized_transport_plan() -> None:
    page = page_result(
        "x" * 50_000,
        {
            "schema": "cbh.transport_plan.v1",
            "max_chars": 1_000_000,
            "max_items": 1_000_000,
        },
    )

    assert page["forwarded_chars"] == 20_000
    assert page["uncovered_chars"] == 30_000
    assert page["next_cursor"] is not None


def test_memory_working_set_preserves_conversation_and_ledger_navigation_handles() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("memory-nav:start", "task_observed", objective="回顾之前的 CBH 记忆"),
    )
    receipt = {
        "selected_records": [],
        "retrieval": {"coverage_status": "complete"},
        "conversation_navigation": {
            "status": "resolved",
            "bundles": [
                {
                    "memory_id": "cbh-long-conversation",
                    "root_path": "C:/memory/cbh",
                    "registry_path": "C:/memory/registry.json",
                    "isolation": "link_only",
                    "selected_links": [{"link_id": "LINK-CBH-001"}],
                    "ledger": {
                        "index_path": "C:/memory/ledger/_LEDGER_INDEX.md",
                        "capsules_path": "C:/memory/ledger/capsules.jsonl",
                        "evidence_refs_path": "C:/memory/ledger/evidence_refs.jsonl",
                    },
                }
            ],
        },
    }
    updated = apply_task_event(
        capsule,
        event(
            "memory-nav:selected",
            "memory_context_selected",
            memory_query_type="history_reason",
            memory_consumption_receipt=receipt,
        ),
    )["capsule"]

    assert updated["memory_working_set"]["conversation_handles"] == [
        {
            "memory_id": "cbh-long-conversation",
            "root_path": "C:/memory/cbh",
            "registry_path": "C:/memory/registry.json",
            "isolation": "link_only",
            "selected_link_ids": ["LINK-CBH-001"],
            "ledger_index_path": "C:/memory/ledger/_LEDGER_INDEX.md",
            "ledger_capsules_path": "C:/memory/ledger/capsules.jsonl",
            "ledger_evidence_refs_path": "C:/memory/ledger/evidence_refs.jsonl",
        }
    ]


def test_only_a_verified_selected_evidence_handle_can_be_marked_opened() -> None:
    capsule = new_task_capsule(
        write_route(),
        event("evidence:start", "task_observed", objective="核对历史原始证据"),
    )
    selected = apply_task_event(
        capsule,
        event(
            "evidence:selected",
            "memory_context_selected",
            memory_query_type="history_reason",
            memory_consumption_receipt={
                "retrieval": {"coverage_status": "complete"},
                "selected_records": [
                    {
                        "record_id": "INC-001",
                        "source_id": "event:INC-001",
                        "evidence_handles": [
                            {
                                "source_id": "codex-session:abc",
                                "original_path": "C:/old/session.jsonl",
                                "line": 42,
                                "line_sha256_16": "0123456789abcdef",
                            }
                        ],
                    }
                ],
            },
        ),
    )["capsule"]
    opened = apply_task_event(
        selected,
        event(
            "evidence:opened",
            "memory_evidence_opened",
            evidence_ref={
                "source_id": "codex-session:abc",
                "resolved_path": "C:/archive/session.jsonl",
                "line": 42,
                "line_sha256_16": "0123456789abcdef",
                "status": "relocated_verified",
            },
        ),
    )["capsule"]

    assert opened["memory_working_set"]["opened_evidence_refs"] == [
        {
            "source_id": "codex-session:abc",
            "resolved_path": "C:/archive/session.jsonl",
            "line": 42,
            "line_sha256_16": "0123456789abcdef",
            "status": "relocated_verified",
        }
    ]
    with pytest.raises(ValueError, match="evidence_source_not_selected"):
        apply_task_event(
            opened,
            event(
                "evidence:unselected",
                "memory_evidence_opened",
                evidence_ref={
                    "source_id": "codex-session:other",
                    "resolved_path": "C:/archive/other.jsonl",
                    "status": "relocated_verified",
                },
            ),
        )
