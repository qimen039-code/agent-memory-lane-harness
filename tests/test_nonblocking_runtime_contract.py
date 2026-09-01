from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "skills" / "embedded-harness"


def _load_harness_module(name: str):
    module_path = HARNESS / f"{name}.py"
    assert module_path.is_file(), f"missing public harness module: {module_path}"
    harness_text = str(HARNESS)
    if harness_text not in sys.path:
        sys.path.insert(0, harness_text)
    return importlib.import_module(name)


def test_mixed_heredoc_profiles_choose_semantic_review() -> None:
    gate = _load_harness_module("behavior_correction_gate")
    receipt = gate.build_behavior_correction_receipt(
        stage="pretool",
        environment="powershell",
        tool_role="shell",
        tool_surface="exec_command",
        text=(
            "python - <<'PY'\n"
            "print('quoted')\n"
            "PY\n"
            "python - <<PY\n"
            "print('unquoted')\n"
            "PY"
        ),
    )

    assert receipt["match_count"] == 2
    assert receipt["decision"] == "semantic_review_required"
    assert receipt["host_blocking"] is False


def test_behavior_hook_is_silent_for_unmatched_destructive_command() -> None:
    hook = _load_harness_module("behavior_correction_hook")
    output = hook.handle_event(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "cwd": str(ROOT),
            "tool_input": {"command": "rm -rf build"},
        },
        parser=lambda _text: [],
    )

    assert output == {}


def test_public_behavior_profiles_contain_no_private_session_paths() -> None:
    profile_path = HARNESS / "behavior_correction_profiles.json"
    assert profile_path.is_file(), f"missing public profile registry: {profile_path}"
    raw = profile_path.read_text(encoding="utf-8")
    assert "C:\\Users\\" not in raw
    assert "\\.codex\\sessions\\" not in raw
    assert "rollout-2026" not in raw


def test_external_retrieval_planner_is_task_local_and_nonexecuting() -> None:
    planner = _load_harness_module("external_retrieval_strategy")
    receipt = planner.build_external_retrieval_receipt(
        "核对 RFC 9110 当前状态",
        recommended_modes=["official_authority_source_search"],
    )
    assert receipt["schema"] == "cbh.external_retrieval_receipt.v1"
    assert receipt["network_access_performed"] is False
    assert receipt["durable_memory_write_performed"] is False
    assert receipt["execution_owner"] == "host_model_agent"


def test_legacy_blocking_entry_scripts_are_retired() -> None:
    for name in (
        "harness_runtime_enforcer.ps1",
        "harness_task_wrapper.ps1",
        "harness_tool_proxy.ps1",
    ):
        assert not (HARNESS / name).exists(), name
