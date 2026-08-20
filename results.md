# Benchmark Results

## Test Environment

| Item | Value |
|---|---|
| Database | CognoDB |
| Python | 3.10.5 |
| Dataset | soc-pokec-200k |
| Expected nodes | 91,489 |
| Expected relationships | 200,000 |
| Actual nodes loaded | 91,489 |
| Actual relationships loaded | 200,000 |
| User ID index | RANGE index on `User.id` |

---

## Dataset Loading

| Metric | Result |
|---|---:|
| Users loaded | 91,489 |
| Relationships loaded | 200,000 |
| Relationship test throughput | 899.88 relationships/sec |

The dataset was successfully loaded into CognoDB with 91,489 users and 200,000 relationships.

A `RANGE` index was created on `User.id` to improve indexed user lookups and relationship ingestion.

---

## Point Lookup Latency

| Metric | Result |
|---|---:|
| Iterations | 100 |
| Min | 235.680 ms |
| Average | 238.851 ms |
| p50 | **237.212 ms** |
| p95 | **249.243 ms** |
| Max | 273.473 ms |

---

## Indexed / Filtered Lookup Latency

| Metric | Result |
|---|---:|
| Iterations | 100 |
| Indexed property | `User.id` |
| Min | 238.764 ms |
| Average | 242.274 ms |
| p50 | **240.174 ms** |
| p95 | **258.890 ms** |
| Max | 295.793 ms |

---

## Traversal Latency

### 1-Hop

| Metric | Result |
|---|---:|
| Starting user | 1 |
| Iterations | 100 |
| Results found | 14 |
| Min | 246.264 ms |
| Average | 251.346 ms |
| p50 | **249.049 ms** |
| p95 | **257.953 ms** |
| Max | 316.793 ms |

### 2-Hop

| Metric | Result |
|---|---:|
| Starting user | 1 |
| Iterations | 100 |
| Results found | 307 |
| Min | 247.128 ms |
| Average | 252.551 ms |
| p50 | **249.045 ms** |
| p95 | **282.959 ms** |
| Max | 298.508 ms |

### 3-Hop

| Metric | Result |
|---|---:|
| Starting user | 1 |
| Iterations | 100 |
| Results found | 10,224 |
| Min | 275.252 ms |
| Average | 307.974 ms |
| p50 | **281.402 ms** |
| p95 | **401.405 ms** |
| Max | 616.930 ms |

---

## Aggregation Latency

| Metric | Result |
|---|---:|
| Iterations | 100 |
| Relationships counted | 200,000 |
| Min | 236.536 ms |
| Average | 239.860 ms |
| p50 | **238.008 ms** |
| p95 | **248.295 ms** |
| Max | 271.397 ms |

---

## Mixed Read/Write Concurrency

| Metric | Result |
|---|---:|
| Concurrent workers | 10 |
| Total requests | 100 |
| Reads | 80 |
| Writes | 20 |
| Read/write mix | 80/20 |
| Total time | 6.452 seconds |
| Throughput | **15.50 requests/sec** |
| Overall p50 | **247.779 ms** |
| Overall p95 | **1594.500 ms** |
| Read p50 | 246.563 ms |
| Read p95 | 1351.876 ms |
| Write p50 | 739.644 ms |
| Write p95 | 1594.500 ms |

---

## Summary

| Workload | p50 | p95 |
|---|---:|---:|
| Point lookup | 237.212 ms | 249.243 ms |
| Indexed / filtered lookup | 240.174 ms | 258.890 ms |
| 1-hop traversal | 249.049 ms | 257.953 ms |
| 2-hop traversal | 249.045 ms | 282.959 ms |
| 3-hop traversal | 281.402 ms | 401.405 ms |
| Aggregation | 238.008 ms | 248.295 ms |
| Mixed read/write concurrency | 247.779 ms | 1594.500 ms |

---

## Observations

- The final dataset contained 91,489 users and 200,000 relationships.
- Point lookup had a p50 latency of 237.212 ms.
- Indexed / filtered lookup using the `User.id` RANGE index had a p50 latency of 240.174 ms.
- 1-hop and 2-hop traversal had very similar p50 latency.
- 3-hop traversal had higher latency, with a p95 of 401.405 ms.
- Aggregation had a p50 latency of 238.008 ms.
- Mixed read/write concurrency achieved 15.50 requests/sec with 10 concurrent workers and an 80/20 read/write mix.
- Write operations were slower than read operations in the mixed workload.
- The final benchmark was performed on the complete 200,000-relationship dataset.
- Resource utilization was not directly measured.