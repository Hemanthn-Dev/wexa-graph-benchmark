\# Benchmark Results



\## Test Environment



| Item | Value |

|---|---|

| Database | CognoDB |

| Python | 3.10.5 |

| Dataset | soc-pokec-200k |

| Expected nodes | 91,489 |

| Expected relationships | 200,000 |

| Actual nodes loaded | 91,489 |

| Actual relationships loaded | 50,000 |



> The full 200,000 relationship load was not completed because the

> Bolt connection repeatedly became defunct during relationship

> ingestion.



\---



\## Lookup Latency



| Metric | Result |

|---|---:|

| Iterations | 100 |

| Min | 285.416 ms |

| Average | 464.450 ms |

| p50 | \*\*408.677 ms\*\* |

| p95 | \*\*801.277 ms\*\* |

| Max | 1638.035 ms |



\---



\## Traversal Latency



| Metric | Result |

|---|---:|

| Starting user | 1 |

| Iterations | 50 |

| Neighbors found | 14 |

| Min | 290.311 ms |

| Average | 503.721 ms |

| p50 | \*\*362.610 ms\*\* |

| p95 | \*\*788.685 ms\*\* |

| Max | 4191.022 ms |



\---



\## Aggregation Latency



| Metric | Result |

|---|---:|

| Iterations | 30 |

| Relationships counted | 50,000 |

| Min | 240.671 ms |

| Average | 259.826 ms |

| p50 | \*\*246.443 ms\*\* |

| p95 | \*\*288.668 ms\*\* |

| Max | 541.415 ms |



\---



\## Concurrent Throughput



| Metric | Result |

|---|---:|

| Concurrent workers | 10 |

| Total requests | 100 |

| Total time | 14.596 seconds |

| Throughput | \*\*6.85 requests/sec\*\* |

| p50 | \*\*1303.085 ms\*\* |

| p95 | \*\*2587.818 ms\*\* |



\---



\## Summary



| Workload | p50 | p95 |

|---|---:|---:|

| Lookup | 408.677 ms | 801.277 ms |

| Traversal | 362.610 ms | 788.685 ms |

| Aggregation | 246.443 ms | 288.668 ms |

| Concurrent lookup | 1303.085 ms | 2587.818 ms |



\## Observations



\- Aggregation had the lowest measured p50 latency.

\- Lookup and traversal had similar p50 latency.

\- Concurrent requests significantly increased latency compared with

&#x20; single-request lookup.

\- The traversal workload had a high maximum latency of 4191.022 ms.

\- Relationship ingestion encountered repeated Bolt connection failures.

\- Resource utilization was not directly measured.

\- Query results were obtained with 91,489 users and 50,000 relationships.

