from __future__ import annotations

import argparse
import fnmatch
import json
import shutil
from pathlib import Path
from typing import Any


INTEGRATION_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = INTEGRATION_ROOT / "deployment-profile.json"


def load_profiles() -> dict[str, Any]:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def selected_files(profile_id: str) -> tuple[dict[str, Any], list[str]]:
    document = load_profiles()
    profiles = document.get("profiles", {})
    if profile_id not in profiles:
        raise ValueError(f"unknown deployment profile: {profile_id}")
    profile = profiles[profile_id]
    selected = sorted(dict.fromkeys(str(item) for item in profile.get("include", [])))
    excluded = [str(item) for item in document.get("excluded_by_default", [])]
    for relative in selected:
        if any(fnmatch.fnmatch(relative, pattern) for pattern in excluded):
            raise ValueError(f"profile includes excluded-by-default content: {relative}")
        path = REPO_ROOT / Path(relative)
        if not path.is_file():
            raise FileNotFoundError(f"profile file is missing: {relative}")
    return profile, selected


def stage(profile_id: str, output: Path) -> dict[str, Any]:
    profile, selected = selected_files(profile_id)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    for relative in selected:
        source = REPO_ROOT / Path(relative)
        destination = output / Path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    receipt = {
        "schema": "cbh.deployment_bundle_receipt.v1",
        "profile_id": profile_id,
        "runtime_mode": profile.get("runtime_mode"),
        "required_predeployment_read": profile.get("required_predeployment_read"),
        "file_count": len(selected),
        "files": selected,
        "full_repository_copy": False,
    }
    (output / "cbh-deployment-receipt.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="List or stage a local deployment profile.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--list", action="store_true", help="Print the resolved file list without writing files.")
    parser.add_argument("--output", type=Path, help="Empty destination directory for a staged bundle.")
    args = parser.parse_args()
    profile, selected = selected_files(args.profile)
    if args.list:
        print(json.dumps({"profile_id": args.profile, "runtime_mode": profile.get("runtime_mode"), "required_predeployment_read": profile.get("required_predeployment_read"), "files": selected}, indent=2))
        return 0
    if args.output is None:
        parser.error("--output is required unless --list is used")
    print(json.dumps(stage(args.profile, args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
