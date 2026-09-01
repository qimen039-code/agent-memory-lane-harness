from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = (
    ROOT / "skills" / "embedded-harness"
    if (ROOT / "skills" / "embedded-harness").is_dir()
    else ROOT
)
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")
CASES = json.loads(
    (ROOT / "tests" / "fixtures" / "external_route_parity.json").read_text(encoding="utf-8")
)["cases"]
def _run(script: str, *args: str) -> dict:
    if not POWERSHELL:
        pytest.skip("PowerShell is not available on PATH")
    completed = subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(HARNESS / script),
            *args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="strict",
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    return json.loads(completed.stdout)


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=[case["id"] for case in CASES],
)
def test_router_and_external_gate_share_external_need(case: dict[str, object]) -> None:
    task = str(case["task"])
    expected = bool(case["expected"])
    router = _run(
        "harness_intake_router.ps1",
        "-TaskText",
        task,
        "-Cwd",
        str(ROOT),
        "-ReceiptMode",
        "diagnostic",
    )
    gate = _run("harness_external_research_gate.ps1", "-TaskText", task)

    assert router["needs_external_research"] is expected
    assert gate["needs_external_research"] is expected
