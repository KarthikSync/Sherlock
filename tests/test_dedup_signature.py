from sherlock.detector import compute_dedup_signature


def test_same_service_metric_same_signature():
    r1 = {"service": "checkout", "metric": "p95_latency_ms"}
    r2 = {"service": "checkout", "metric": "p95_latency_ms"}
    assert compute_dedup_signature(r1) == compute_dedup_signature(r2)


def test_different_service_different_signature():
    r1 = {"service": "checkout", "metric": "p95_latency_ms"}
    r2 = {"service": "payments", "metric": "p95_latency_ms"}
    assert compute_dedup_signature(r1) != compute_dedup_signature(r2)


def test_different_metric_different_signature():
    r1 = {"service": "checkout", "metric": "p95_latency_ms"}
    r2 = {"service": "checkout", "metric": "error_rate"}
    assert compute_dedup_signature(r1) != compute_dedup_signature(r2)


def test_signature_format():
    r = {"service": "checkout", "metric": "p95_latency_ms"}
    assert compute_dedup_signature(r) == "service=checkout|metric=p95_latency_ms"


def test_no_window_in_signature():
    r = {"service": "checkout", "metric": "p95_latency_ms"}
    assert "window" not in compute_dedup_signature(r)


def test_value_threshold_do_not_affect_signature():
    r1 = {"service": "svc", "metric": "rps", "value": 100, "threshold": 50}
    r2 = {"service": "svc", "metric": "rps", "value": 200, "threshold": 50}
    assert compute_dedup_signature(r1) == compute_dedup_signature(r2)
