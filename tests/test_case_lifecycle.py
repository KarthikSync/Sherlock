from __future__ import annotations

from unittest.mock import patch

import sherlock.memory as mem_mod
import sherlock.case_matcher as cm_mod
import sherlock.transitions as tr_mod


def _finding(value, threshold, timestamp, service="checkout", metric="p95_latency_ms"):
    from sherlock.detector import compute_severity, compute_dedup_signature
    rec = {"service": service, "metric": metric, "value": value,
           "threshold": threshold, "timestamp": timestamp}
    return {**rec, "severity": compute_severity(value, threshold),
            "dedup_signature": compute_dedup_signature(rec)}


def test_full_lifecycle(tmp_path):
    cases_dir = tmp_path / "cases"
    cases_dir.mkdir()

    with patch.object(mem_mod, "CASES_DIR", cases_dir):
        # Phase 1: new case (high)
        f1 = _finding(2500, 1500, "2026-05-09T08:00:00Z")
        assert f1["severity"] == "high"

        matched = cm_mod.match_or_create([f1], [])
        case, finding, is_new = matched[0]
        assert is_new is True

        transitions = tr_mod.compute_transitions(case, finding, is_new)
        assert transitions[0]["type"] == "new_case"

        tr_mod.update_case(case, finding, is_new, finding["timestamp"])
        mem_mod.save_case(case)

        files = list(cases_dir.glob("CASE-*.md"))
        assert len(files) == 1
        text = files[0].read_text()
        assert "status: open" in text
        assert "severity: high" in text
        assert "CASE-0001" in text

        # Phase 2: same severity (steady state)
        all_cases = mem_mod.load_cases()
        open_cases = [c for c in all_cases if c.get("status") == "open"]

        f2 = _finding(2600, 1500, "2026-05-09T08:15:00Z")
        matched2 = cm_mod.match_or_create([f2], open_cases)
        case2, finding2, is_new2 = matched2[0]
        assert is_new2 is False

        transitions2 = tr_mod.compute_transitions(case2, finding2, is_new2)
        assert transitions2[0]["type"] == "steady_state"

        tr_mod.update_case(case2, finding2, is_new2, finding2["timestamp"])
        mem_mod.save_case(case2)

        assert "2026-05-09T08:15:00Z" in files[0].read_text()

        # Phase 3: severity escalates to critical
        all_cases3 = mem_mod.load_cases()
        open_cases3 = [c for c in all_cases3 if c.get("status") == "open"]

        f3 = _finding(3100, 1500, "2026-05-09T08:30:00Z")
        matched3 = cm_mod.match_or_create([f3], open_cases3)
        case3, finding3, is_new3 = matched3[0]
        assert is_new3 is False

        transitions3 = tr_mod.compute_transitions(case3, finding3, is_new3)
        assert transitions3[0]["type"] == "severity_changed"
        assert transitions3[0]["old_severity"] == "high"
        assert transitions3[0]["new_severity"] == "critical"

        tr_mod.update_case(case3, finding3, is_new3, finding3["timestamp"])
        mem_mod.save_case(case3)

        assert "severity: critical" in files[0].read_text()

        # Phase 4: resolution
        all_cases4 = mem_mod.load_cases()
        open_cases4 = [c for c in all_cases4 if c.get("status") == "open"]

        transitions4 = tr_mod.compute_transitions(open_cases4[0], None, False)
        assert transitions4[0]["type"] == "resolved"

        tr_mod.update_case(open_cases4[0], None, False, "2026-05-09T08:45:00Z")
        mem_mod.save_case(open_cases4[0])

        text4 = files[0].read_text()
        assert "status: resolved" in text4
        assert "resolved_at:" in text4
        assert "severity: critical" in text4  # frozen, not reset to ok
        assert "resolution_reason:" in text4
