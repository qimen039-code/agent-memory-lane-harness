#!/usr/bin/env python3
"""One-shot adoption diagnostics for Agent Cognitive Continuity Framework.

This tool is a read-only preflight check. It does not install packages, change
hooks, edit configuration, or claim runtime enforcement for a host agent. It
only reports whether the local reference package and basic gate surfaces look
usable from the current machine.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


REQUIRED_FILES = [
    "AGENTS.md",
    "CREDITS.toml",
    "VERSION",
    "README.md",
    "README_zh.md",
    "docs/deployment-risk-patterns.md",
    "docs/agent-deployment-map.md",
    "docs/reproduction.md",
    "docs/test-cases.md",
    "docs/memory-feedback-loop-trial.md",
    "docs/memory-write-granularity-contract.md",
    "docs/hybrid-memory-retrieval-contract.md",
    "docs/content-reading-contract.md",
    "docs/skill-lifecycle-contract.md",
    "templates/skill-lifecycle/skill_release_receipt.json",
    "skills/embedded-harness/embedded_harness_policy.authoring.toml",
    "skills/embedded-harness/embedded_harness_policy.json",
    "skills/embedded-harness/embedded_harness_policy.local.example.json",
    "skills/embedded-harness/compile_policy_from_toml.py",
    "skills/embedded-harness/behavior_correction_gate.py",
    "skills/embedded-harness/behavior_correction_hook.py",
    "skills/embedded-harness/behavior_correction_profiles.json",
    "skills/embedded-harness/nested_tool_preflight.py",
    "skills/embedded-harness/compact_failure_audit.py",
    "skills/embedded-harness/task_continuity.py",
    "skills/embedded-harness/engineering_execution.py",
    "skills/embedded-harness/external_route_trigger_helpers.ps1",
    "skills/embedded-harness/dangerous_delete_guard.py",
    "skills/embedded-harness/harness_intake_router.ps1",
    "skills/embedded-harness/validate_policy.ps1",
    "skills/embedded-harness/bash/harness_intake_router.sh",
    "skills/embedded-harness/bash/validate_policy.sh",
    "tests/test_credits.py",
    "tests/test_codex_session_ledger.py",
    "tests/test_nested_tool_preflight.py",
    "tests/test_compact_failure_audit.py",
    "tests/test_task_continuity.py",
    "tests/test_engineering_execution.py",
    "tests/test_external_route_parity.py",
    "tests/test_dangerous_delete_guard.py",
    "tests/fixtures/nested_tool_failures.json",
    "tests/test_documentation_contracts.py",
    "tests/test_router_contract.py",
]


@dataclass
class Check:
    id: str
    status: str
    summary: str
    evidence: dict[str, Any]
    next_step: str = ""


def repo_path(root: Path, relative: str) -> Path:
    return root / relative


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def run_command(args: list[str], cwd: Path, timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def find_powershell() -> str | None:
    return shutil.which("pwsh") or shutil.which("powershell")


def load_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), ""
    except Exception as exc:  # noqa: BLE001 - diagnostic surface should report exact failure
        return None, str(exc)


def parse_router_json(output: str) -> dict[str, Any]:
    return json.loads(output)


def add_status(statuses: list[str]) -> str:
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    return "pass"


def check_required_files(root: Path) -> Check:
    missing = [path for path in REQUIRED_FILES if not repo_path(root, path).is_file()]
    return Check(
        id="doctor.required_files",
        status="fail" if missing else "pass",
        summary="Required reference files are present." if not missing else "Some required reference files are missing.",
        evidence={"missing": missing, "checked": REQUIRED_FILES},
        next_step="Restore the missing files from the release package or repository." if missing else "",
    )


def check_policy_shape(root: Path) -> Check:
    policy_path = repo_path(root, "skills/embedded-harness/embedded_harness_policy.json")
    policy, error = load_json(policy_path)
    if policy is None:
        return Check(
            id="doctor.policy_shape",
            status="fail",
            summary="Policy JSON could not be parsed.",
            evidence={"path": rel(root, policy_path), "error": error},
            next_step="Fix JSON syntax before running adapters or hooks.",
        )

    required_keys = [
        "risk_trigger_rules",
        "r5_context_decision_rules",
        "risk_gate_rules",
        "risk_approval_rules",
        "router_decision_contract",
        "memory_roots",
    ]
    missing = [key for key in required_keys if key not in policy]
    r5_rules = policy.get("r5_context_decision_rules", {})
    r5_required = [
        "direct_action_terms",
        "context_required_candidate_terms",
        "always_action_candidate_terms",
        "action_context_terms",
        "non_action_context_terms",
        "documentation_context_terms",
    ]
    empty_r5 = [key for key in r5_required if not r5_rules.get(key)]
    issues = missing + [f"r5_context_decision_rules.{key}" for key in empty_r5]
    router = policy.get("router_decision_contract", {})
    continuity = router.get("task_continuity_contract", {}) if isinstance(router, dict) else {}
    if continuity.get("schema") != "cbh.task_continuity_contract.v1":
        issues.append("router_decision_contract.task_continuity_contract")
    if "task_continuity" not in router.get("module_need_values", []):
        issues.append("router_decision_contract.module_need_values.task_continuity")
    return Check(
        id="doctor.policy_shape",
        status="fail" if issues else "pass",
        summary="Policy shape contains required routing and R5 context sections." if not issues else "Policy shape is incomplete.",
        evidence={"path": rel(root, policy_path), "missing_or_empty": issues},
        next_step="Run the policy validator and restore missing sections." if issues else "",
    )


def check_policy_authoring(root: Path) -> Check:
    result = run_command(
        [sys.executable, "skills/embedded-harness/compile_policy_from_toml.py", "--check"],
        cwd=root,
    )
    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(result.stdout)
    except Exception:
        pass
    ok = result.returncode == 0 and payload is not None and payload.get("status") == "pass"
    return Check(
        id="doctor.policy_authoring_toml",
        status="pass" if ok else "fail",
        summary="TOML policy authoring layer matches runtime JSON." if ok else "TOML policy authoring layer drifted from runtime JSON.",
        evidence={
            "returncode": result.returncode,
            "payload": payload,
            "stderr": result.stderr[-500:],
        },
        next_step="Run compile_policy_from_toml.py, inspect changed_tracked_paths, and update either TOML or JSON deliberately." if not ok else "",
    )


def check_powershell_validator(root: Path, shell: str | None) -> Check:
    if not shell:
        return Check(
            id="doctor.powershell_validator",
            status="warn",
            summary="PowerShell was not found on PATH.",
            evidence={"shell": None},
            next_step="Install or expose PowerShell, or use the Bash reference path on macOS/Linux.",
        )
    result = run_command(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "skills/embedded-harness/validate_policy.ps1",
        ],
        cwd=root,
    )
    status = "pass"
    summary = "PowerShell policy validator passed."
    next_step = ""
    try:
        payload = json.loads(result.stdout)
        if result.returncode != 0 or payload.get("status") != "pass":
            status = "fail"
            summary = "PowerShell policy validator reported issues."
            next_step = "Inspect validate_policy output before wiring runtime hooks."
    except Exception:
        status = "fail"
        payload = {"stdout": result.stdout[-1000:], "stderr": result.stderr[-1000:]}
        summary = "PowerShell policy validator did not return valid JSON."
        next_step = "Check PowerShell execution policy, script path, and stdout encoding."
    return Check(
        id="doctor.powershell_validator",
        status=status,
        summary=summary,
        evidence={"returncode": result.returncode, "payload": payload},
        next_step=next_step,
    )


def route(shell: str, root: Path, task: str) -> tuple[int, dict[str, Any] | None, str]:
    result = run_command(
        [
            shell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "skills/embedded-harness/harness_intake_router.ps1",
            "-TaskText",
            task,
            "-Cwd",
            str(root / "path with spaces"),
            "-ReceiptMode",
            "diagnostic",
        ],
        cwd=root,
    )
    try:
        return result.returncode, parse_router_json(result.stdout), result.stderr
    except Exception:
        return result.returncode, None, (result.stderr + "\n" + result.stdout[-1000:])


def check_router_probes(root: Path, shell: str | None) -> Check:
    if not shell:
        return Check(
            id="doctor.router_probes",
            status="warn",
            summary="Router probes were skipped because PowerShell was not found.",
            evidence={},
            next_step="Run Bash smoke checks or install PowerShell.",
        )

    probes = [
        {
            "id": "negated_delete",
            "task": "do not delete anything",
            "expect": lambda p: p.get("risk_level") != "R5"
            and "delete" in p.get("negated_risk_triggers", {}).get("R5", []),
        },
        {
            "id": "docs_r5_context",
            "task": "trigger list contains commit push 删除 提交, docs discussion only, no npm/pip distribution",
            "expect": lambda p: p.get("risk_level") != "R5"
            and p.get("risk_context_decisions", {}).get("R5", {}).get("action_surface") == "documentation_or_discussion",
        },
        {
            "id": "delete_release",
            "task": "删除旧 release",
            "expect": lambda p: p.get("risk_level") == "R5"
            and bool(p.get("risk_context_decisions", {}).get("R5", {}).get("promote_to_risk")),
        },
        {
            "id": "submit_report",
            "task": "提交报告",
            "expect": lambda p: p.get("risk_level") != "R5",
        },
    ]
    results = []
    failed = []
    for probe in probes:
        code, payload, error = route(shell, root, probe["task"])
        ok = payload is not None and probe["expect"](payload)
        if not ok:
            failed.append(probe["id"])
        results.append(
            {
                "id": probe["id"],
                "returncode": code,
                "ok": ok,
                "risk_level": None if payload is None else payload.get("risk_level"),
                "error": error[-500:] if error else "",
            }
        )
    return Check(
        id="doctor.router_probes",
        status="fail" if failed else "pass",
        summary="Router probes passed." if not failed else "One or more router probes failed.",
        evidence={"probes": results, "failed": failed},
        next_step="Run docs/reproduction.md router checks and inspect risk_context_decisions." if failed else "",
    )


def check_behavior_correction_profiles(root: Path) -> Check:
    result = run_command(
        [
            sys.executable,
            "-B",
            "skills/embedded-harness/behavior_correction_gate.py",
            "--list-profiles",
        ],
        cwd=root,
    )
    payload: dict[str, Any] | None = None
    try:
        payload = json.loads(result.stdout)
    except Exception:
        pass
    ok = bool(
        result.returncode == 0
        and payload
        and payload.get("status") == "pass"
        and int(payload.get("profile_count") or 0) > 0
        and payload.get("host_blocking") is False
    )
    return Check(
        id="doctor.behavior_correction_profiles",
        status="pass" if ok else "fail",
        summary="Nonblocking correction profiles are loadable." if ok else "Correction profiles could not be validated.",
        evidence={
            "returncode": result.returncode,
            "status": None if payload is None else payload.get("status"),
            "profile_count": None if payload is None else payload.get("profile_count"),
            "host_blocking": None if payload is None else payload.get("host_blocking"),
            "stderr": result.stderr[-500:],
        },
        next_step="Inspect the correction registry and policy contract." if not ok else "",
    )


def check_bash_surface(root: Path) -> Check:
    bash = shutil.which("bash")
    jq = shutil.which("jq")
    if not bash or not jq:
        return Check(
            id="doctor.bash_surface",
            status="warn",
            summary="Bash reference checks cannot run on this machine.",
            evidence={"bash": bash, "jq": jq},
            next_step="Run the Ubuntu GitHub Actions smoke job or install bash and jq on the target host.",
        )
    result = run_command([bash, "skills/embedded-harness/bash/validate_policy.sh"], cwd=root)
    ok = result.returncode == 0
    return Check(
        id="doctor.bash_surface",
        status="pass" if ok else "fail",
        summary="Bash validator passed." if ok else "Bash validator failed.",
        evidence={"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]},
        next_step="Inspect Bash validator output and jq availability." if not ok else "",
    )


def check_docs_alignment(root: Path) -> Check:
    credits = repo_path(root, "CREDITS.toml")
    deployment_doc = repo_path(root, "docs/deployment-risk-patterns.md")
    issues = []
    if not credits.is_file():
        issues.append("CREDITS.toml missing")
    if deployment_doc.is_file() and "cbh_doctor.py" not in deployment_doc.read_text(encoding="utf-8", errors="replace"):
        issues.append("deployment-risk-patterns.md does not mention cbh_doctor.py")
    return Check(
        id="doctor.docs_alignment",
        status="warn" if issues else "pass",
        summary="Public docs mention diagnostic and credit surfaces." if not issues else "Some optional docs links are missing.",
        evidence={"issues": issues},
        next_step="Add lightweight docs links if this package is being prepared for public adoption." if issues else "",
    )


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Agent Cognitive Continuity Framework Doctor",
        "",
        f"Status: `{report['status']}`",
        "",
        "| Check | Status | Summary |",
        "| --- | --- | --- |",
    ]
    for check in report["checks"]:
        lines.append(f"| `{check['id']}` | `{check['status']}` | {check['summary']} |")
    lines.append("")
    lines.append("This is a local diagnostic report, not a certification that a host agent honors every hook path.")
    return "\n".join(lines) + "\n"


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    shell = find_powershell()
    checks = [
        check_required_files(root),
        check_policy_shape(root),
        check_policy_authoring(root),
        check_powershell_validator(root, shell),
        check_router_probes(root, shell),
        check_behavior_correction_profiles(root),
        check_bash_surface(root),
        check_docs_alignment(root),
    ]
    status = add_status([check.status for check in checks])
    return {
        "tool": "cbh-doctor",
        "version": "1",
        "status": status,
        "repo_root": str(root),
        "checks": [asdict(check) for check in checks],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run local Agent Cognitive Continuity Framework adoption diagnostics.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a compact text summary.")
    parser.add_argument("--markdown-output", help="Optional path for a markdown report.")
    parser.add_argument(
        "--fail-on",
        choices=["fail", "warn"],
        default="fail",
        help="Exit nonzero on fail only, or on warn/fail.",
    )
    args = parser.parse_args(argv)

    report = build_report(Path(args.repo_root))
    if args.markdown_output:
        Path(args.markdown_output).write_text(render_markdown(report), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"cbh-doctor status: {report['status']}")
        for check in report["checks"]:
            print(f"- {check['id']}: {check['status']} - {check['summary']}")

    if report["status"] == "fail":
        return 2
    if args.fail_on == "warn" and report["status"] == "warn":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
