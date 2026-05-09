from __future__ import annotations

from typing import Any

from sherlock import memory as _mem


def _slug_from_finding(finding: dict[str, Any]) -> str:
    raw = f"{finding['service']}-{finding['metric']}"
    return raw.replace("_", "-").lower()


def _new_case(finding: dict[str, Any], now_iso: str, extra_offset: int = 0) -> dict[str, Any]:
    case_id = _mem.allocate_case_id(extra_offset)
    return {
        "case_id": case_id,
        "slug": _slug_from_finding(finding),
        "status": "open",
        "severity": finding["severity"],
        "first_seen": now_iso,
        "last_seen": now_iso,
        "last_severity_change": now_iso,
        "resolved_at": None,
        "resolution_reason": None,
        "dedup_signature": finding["dedup_signature"],
        "hypothesis": (
            f"{finding['service']} {finding['metric']} increased above baseline."
        ),
        "_body": (
            "\n## Evidence log\n\n"
            "## Decision log\n\n"
            f"- {now_iso} — case opened by detector `threshold_breach`.\n"
        ),
    }


def match_or_create(
    findings: list[dict[str, Any]],
    open_cases: list[dict[str, Any]],
) -> list[tuple[dict[str, Any], dict[str, Any], bool]]:
    sig_map: dict[str, dict[str, Any]] = {}
    for case in open_cases:
        if case.get("status") == "open":
            sig_map[case["dedup_signature"]] = case

    results: list[tuple[dict[str, Any], dict[str, Any], bool]] = []
    seen_sigs: set[str] = set()
    new_case_count = 0

    for finding in findings:
        sig = finding["dedup_signature"]
        if sig in seen_sigs:
            results = [(c, f, n) for c, f, n in results if f["dedup_signature"] != sig]
        seen_sigs.add(sig)

        if sig in sig_map:
            results.append((sig_map[sig], finding, False))
        else:
            new_case = _new_case(finding, finding["timestamp"], extra_offset=new_case_count)
            new_case_count += 1
            sig_map[sig] = new_case
            results.append((new_case, finding, True))

    return results
