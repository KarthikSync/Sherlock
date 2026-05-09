---
case_id: CASE-0001
slug: checkout-p95-latency-ms
status: resolved
severity: critical
first_seen: '2026-05-09T08:00:00Z'
last_seen: '2026-05-09T08:30:00Z'
last_severity_change: '2026-05-09T08:30:00Z'
resolved_at: '2026-05-09T08:45:00Z'
resolution_reason: metric recovered below threshold
dedup_signature: service=checkout|metric=p95_latency_ms
hypothesis: checkout p95_latency_ms increased above baseline.
---

## Evidence log

- 2026-05-09T08:45:00Z — p95_latency_ms 1200, threshold 1500 (recovered).
- 2026-05-09T08:30:00Z — p95_latency_ms 3100, threshold 1500.
- 2026-05-09T08:15:00Z — p95_latency_ms 2600, threshold 1500.
- 2026-05-09T08:00:00Z — p95_latency_ms 2500, threshold 1500.
## Decision log

- 2026-05-09T08:45:00Z — case resolved: metric recovered below threshold.
- 2026-05-09T08:00:00Z — case opened by detector `threshold_breach`.
