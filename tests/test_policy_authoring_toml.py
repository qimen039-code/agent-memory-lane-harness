from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


if sys.version_info < (3, 11):
    pytest.skip("tomllib requires Python 3.11+", allow_module_level=True)

import tomllib  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
AUTHORING = ROOT / "skills" / "embedded-harness" / "embedded_harness_policy.authoring.toml"
COMPILER = ROOT / "skills" / "embedded-harness" / "compile_policy_from_toml.py"
RUNTIME_POLICY = ROOT / "skills" / "embedded-harness" / "embedded_harness_policy.json"


def test_policy_authoring_toml_is_machine_readable() -> None:
    payload = tomllib.loads(AUTHORING.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "cbh.policy_authoring.v1"
    assert payload["compiled_sections"]
    router = payload["router_decision_contract"]
    continuity = router["task_continuity_contract"]
    assert continuity["schema"] == "cbh.task_continuity_contract.v1"
    assert continuity["lifecycle_values"] == [
        "DORMANT",
        "ARMED",
        "ACTIVE",
        "VERIFYING",
        "RETIRED",
    ]
    assert continuity["short_answer_default"] == "dormant"
    assert continuity["write_intent_requires_arm"] is True
    assert continuity["state_storage"] == "process_local_only"
    assert continuity["authority_granted"] is False
    assert continuity["decision_values"] == ["dormant", "arm", "continue"]
    assert continuity["activation_reasons"] == [
        "write_intent",
        "tool_required",
        "long_running_task",
        "multi_stage_task",
        "task_resume",
        "open_loop",
        "prior_failure",
        "explicit_request",
        "existing_active_capsule",
    ]
    assert continuity["progress_status_values"] == ["verified", "inferred", "unknown"]
    engineering = router["engineering_execution_contract"]
    assert engineering["schema"] == "cbh.engineering_execution_contract.v1"
    assert engineering["profile_values"] == [
        "tracer_bullet_plan",
        "deep_module_review",
        "skill_invocation_topology",
        "adapter_seam_review",
    ]
    assert set(engineering["profile_triggers"]) == set(engineering["profile_values"])
    assert engineering["state_storage"] == "none"
    assert engineering["authority_granted"] is False
    lifecycle = router["correction_lifecycle_contract"]
    assert lifecycle["schema"] == "cbh.correction_lifecycle_contract.v1"
    assert lifecycle["objective_order"] == [
        "real_effectiveness_and_required_components",
        "minimum_sufficient_implementation",
        "execution_time_and_token_efficiency",
        "surface_simplicity",
    ]
    assert "postcondition_verification" in lifecycle["stages"]
    assert "task_local_retirement" in lifecycle["stages"]
    correction = payload["runtime_enforcement"]["behavior_correction_contract"]
    assert correction["schema"] == "cbh.behavior_correction_contract.v1"
    assert correction["migration_hook"]["host_blocking"] is False
    assert correction["migration_hook"]["stateful"] is False
    assert correction["migration_hook"]["ambiguous_behavior"] == "no_output_original_input_unchanged"
    retrieval = payload["search_and_learning_decision_matrix"]["external_retrieval_contract"]
    assert retrieval["schema"] == "cbh.external_retrieval_contract.v1"
    assert retrieval["receipt_schema"] == "cbh.external_retrieval_receipt.v1"
    assert {"doi_resolver", "pypi", "npm", "huggingface", "github_repository"} <= set(
        retrieval["source_native_routes"]
    )
    assert "max_queries" not in retrieval
    assert "max_sources" not in retrieval
    assert "provider" in retrieval["negative_claim_rule"].lower()
    assert "miss" in retrieval["negative_claim_rule"].lower()
    assert retrieval["currentness_evidence_rule"]
    direct_outcome = router["direct_outcome_first_contract"]
    assert direct_outcome["required_gate"] == "direct_outcome_first_gate"
    assert len(direct_outcome["expansion_allowed_only_if"]) == 4
    assert direct_outcome["first_mutation_rule"]
    assert direct_outcome["retire_condition"]


def test_policy_authoring_toml_matches_runtime_json() -> None:
    result = subprocess.run(
        [sys.executable, str(COMPILER), "--check"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "pass"
    assert payload["changed_tracked_paths"] == []


def test_runtime_policy_accepts_resolved_current_exposure() -> None:
    policy = json.loads(RUNTIME_POLICY.read_text(encoding="utf-8"))
    values = policy["router_decision_contract"]["tool_discovery_status_values"]

    assert "resolved_current_exposure" in values
    assert len(values) == len(set(values))
