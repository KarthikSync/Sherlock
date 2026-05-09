from __future__ import annotations

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

import sherlock.memory as mem_mod
from sherlock.cli import cli


def _write_telemetry(path, data):
    path.write_text(json.dumps(data))
    return path


def test_below_threshold_no_output(tmp_path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    tel = _write_telemetry(tmp_path / "t.json", {
        "service": "checkout", "metric": "p95_latency_ms",
        "value": 1200, "threshold": 1500,
        "timestamp": "2026-05-09T08:00:00Z",
    })
    runner = CliRunner()
    with patch.object(mem_mod, "CASES_DIR", cases_dir):
        result = runner.invoke(cli, ["run", "--input", str(tel)])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_at_threshold_no_output(tmp_path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    tel = _write_telemetry(tmp_path / "t.json", {
        "service": "api", "metric": "error_rate",
        "value": 1500, "threshold": 1500,
        "timestamp": "2026-05-09T09:00:00Z",
    })
    runner = CliRunner()
    with patch.object(mem_mod, "CASES_DIR", cases_dir):
        result = runner.invoke(cli, ["run", "--input", str(tel)])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_second_run_same_severity_is_silent(tmp_path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()
    runner = CliRunner()

    tel1 = _write_telemetry(tmp_path / "run1.json", {
        "service": "checkout", "metric": "p95_latency_ms",
        "value": 2500, "threshold": 1500,
        "timestamp": "2026-05-09T08:00:00Z",
    })
    tel2 = _write_telemetry(tmp_path / "run2.json", {
        "service": "checkout", "metric": "p95_latency_ms",
        "value": 2600, "threshold": 1500,
        "timestamp": "2026-05-09T08:15:00Z",
    })

    with patch.object(mem_mod, "CASES_DIR", cases_dir):
        r1 = runner.invoke(cli, ["run", "--input", str(tel1)])
        assert "NEW CASE" in r1.output

        r2 = runner.invoke(cli, ["run", "--input", str(tel2)])
        assert r2.exit_code == 0
        assert r2.output.strip() == ""
