from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

from scripts.update_all_data import DATASET_REGISTRY, select_steps

ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR = ROOT / "scripts" / "update_all_data.py"


def test_orchestrator_help_is_available() -> None:
    result = subprocess.run([sys.executable, str(ORCHESTRATOR), "--help"], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0
    assert "--only" in result.stdout
    assert "--offline" in result.stdout
    assert "--skip-network" in result.stdout
    assert "--dry-run" in result.stdout


def test_registry_covers_every_root_data_json() -> None:
    dataset_names = {path.name for path in (ROOT / "data").glob("*.json")}
    assert dataset_names <= set(DATASET_REGISTRY)


def test_offline_dry_run_does_not_change_data() -> None:
    data_files = sorted((ROOT / "data").glob("*.json"))
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in data_files}
    result = subprocess.run(
        [sys.executable, str(ORCHESTRATOR), "--only", "niti-reports.json", "--offline", "--dry-run"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "build-niti-reports" in result.stdout
    assert "export-catalog" in result.stdout
    assert "build-explainers" in result.stdout
    assert "dry run" in result.stdout
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in data_files}
    assert after == before


def test_selected_input_includes_derived_outputs() -> None:
    names = {step.name for step in select_steps(["union_budget.json"])}
    assert "build-fiscal-layer" in names
    assert "export-catalog" in names
    assert "build-explainers" in names
