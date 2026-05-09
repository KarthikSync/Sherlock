from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from sherlock import case_matcher as cm
from sherlock import detector as det
from sherlock import memory as mem
from sherlock import renderer as rend
from sherlock import transitions as tr


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run_cycle(
    input_path: str | Path | None,
    summarize: bool = False,
) -> tuple[list[str], list[str]]:
    """
    Run one detection cycle.
    Returns (transition_lines, steady_state_case_ids).
    """
    records = det.parse_telemetry(input_path)
    findings = det.detect(records)
    all_cases = mem.load_cases()
    open_cases = [c for c in all_cases if c.get("status") == "open"]

    matched = cm.match_or_create(findings, open_cases)
    matched_sigs = {finding["dedup_signature"] for _, finding, _ in matched}

    lines: list[str] = []
    steady_ids: list[str] = []

    for case, finding, is_new in matched:
        timestamp = finding["timestamp"]
        transitions = tr.compute_transitions(case, finding, is_new)
        tr.update_case(case, finding, is_new, timestamp)
        if summarize and is_new:
            from sherlock import llm
            hypothesis = llm.summarize(finding)
            if hypothesis:
                case["hypothesis"] = hypothesis
        mem.save_case(case)
        for t in transitions:
            line = rend.format_transition(t)
            if line is not None:
                lines.append(line)
            else:
                steady_ids.append(case["case_id"])

    # Build a map of below-threshold records (recovery observations) by dedup signature
    recovery_by_sig: dict[str, dict] = {}
    for rec in records:
        sig = det.compute_dedup_signature(rec)
        if det.compute_severity(rec["value"], rec["threshold"]) is None:
            recovery_by_sig[sig] = rec

    resolution_timestamp = records[-1]["timestamp"] if records else _utc_now()
    for case in open_cases:
        if case["dedup_signature"] not in matched_sigs:
            recovery_rec = recovery_by_sig.get(case["dedup_signature"])
            timestamp = recovery_rec["timestamp"] if recovery_rec else resolution_timestamp
            transitions = tr.compute_transitions(case, None, False)
            tr.update_case(case, None, False, timestamp, recovery_rec)
            mem.save_case(case)
            for t in transitions:
                line = rend.format_transition(t)
                if line is not None:
                    lines.append(line)

    return lines, steady_ids


@click.group()
def cli() -> None:
    """Sherlock — stateful telemetry detective."""


@cli.command("run")
@click.option("--input", "input_path", default=None,
              help="Path to telemetry JSON file. Reads stdin if omitted.")
@click.option("--no-llm", is_flag=True, default=False, hidden=True)
@click.option("--summarize", is_flag=True, default=False,
              help="Generate hypothesis text via OpenRouter (requires OPENROUTER_API_KEY).")
def run_cmd(input_path: str | None, no_llm: bool, summarize: bool) -> None:
    """Run one detection cycle against telemetry input."""
    if input_path is None and sys.stdin.isatty():
        click.echo(
            "Error: no --input provided and stdin is a TTY. "
            "Pipe telemetry JSON or use --input <path>.",
            err=True,
        )
        sys.exit(1)
    lines, _ = _run_cycle(input_path, summarize=summarize)
    for line in lines:
        click.echo(line)


@cli.command("demo")
@click.option("--reset", is_flag=True, default=False,
              help="Clear existing cases before running demo.")
def demo_cmd(reset: bool) -> None:
    """Run the four-phase demo scenario."""
    cases_dir = mem.CASES_DIR
    existing = [p for p in cases_dir.glob("*.md") if p.name != ".gitkeep"]

    if existing and not reset:
        click.echo(
            f"Demo aborted: {len(existing)} case file(s) already exist in {cases_dir}.\n"
            "Run with --reset to clear them first.",
            err=True,
        )
        sys.exit(1)

    if reset:
        for path in existing:
            path.unlink()

    examples_dir = Path(__file__).parent.parent / "examples" / "telemetry"
    runs = [
        ("run1_new_case.json", "Run 1"),
        ("run2_same_issue.json", "Run 2"),
        ("run3_severity_change.json", "Run 3"),
        ("run4_resolved.json", "Run 4"),
    ]

    for filename, label in runs:
        click.echo(label)
        lines, steady_ids = _run_cycle(examples_dir / filename)
        for line in lines:
            click.echo(line)
        if not lines and steady_ids:
            ids = ", ".join(steady_ids)
            click.echo(f"(no human-visible transitions; evidence appended to {ids})")
        click.echo("")
