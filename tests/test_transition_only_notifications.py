from sherlock.renderer import format_transition


def test_new_case_produces_output():
    t = {"type": "new_case", "case_id": "CASE-0001", "slug": "checkout-p95-latency-ms",
         "severity": "high"}
    line = format_transition(t)
    assert line is not None
    assert "NEW CASE" in line
    assert "CASE-0001" in line
    assert "high" in line


def test_severity_changed_produces_output():
    t = {"type": "severity_changed", "case_id": "CASE-0001", "slug": "s",
         "old_severity": "high", "new_severity": "critical"}
    line = format_transition(t)
    assert line is not None
    assert "SEVERITY CHANGED" in line
    assert "high -> critical" in line


def test_resolved_produces_output():
    t = {"type": "resolved", "case_id": "CASE-0001", "slug": "checkout-p95-latency-ms"}
    line = format_transition(t)
    assert line is not None
    assert "RESOLVED" in line
    assert "CASE-0001" in line


def test_steady_state_produces_none():
    t = {"type": "steady_state", "case_id": "CASE-0001"}
    assert format_transition(t) is None


def test_format_new_case_exact():
    t = {"type": "new_case", "case_id": "CASE-0002", "slug": "my-slug", "severity": "medium"}
    assert format_transition(t) == "NEW CASE: CASE-0002 medium my-slug"


def test_format_severity_changed_exact():
    t = {"type": "severity_changed", "case_id": "CASE-0003", "slug": "s",
         "old_severity": "medium", "new_severity": "high"}
    assert format_transition(t) == "SEVERITY CHANGED: CASE-0003 medium -> high"


def test_format_resolved_exact():
    t = {"type": "resolved", "case_id": "CASE-0004", "slug": "my-slug"}
    assert format_transition(t) == "RESOLVED: CASE-0004 my-slug"
