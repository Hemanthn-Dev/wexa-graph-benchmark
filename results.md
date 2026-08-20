# Benchmark Results

This file records the final observed results for the four graph databases tested in this project.

## Dataset

- Dataset: `soc-pokec-200k`
- Unique users: 91,489
- Relationships: 200,000

The same prepared dataset was used for the database experiments. CognoDB's final observed run completed the 200,000-relationship load shown below.

## Neo4j

### Loading

| Metric | Result |
|---|---:|
| Users | 91,489 |
| Relationships | 200,000 |
| User ingest | 4.61 s |
| Relationship ingest | 21.23 s |
| Total load | **25.85 s** |
| Node throughput | 19,826.52 nodes/s |
| Relationship throughput | 9,419.96 relationships/s |

### Indexed / filtered lookup

| Metric | Result |
|---|---:|
| Queries | 100 |
| Indexed property | `User.id` |
| Min | 84.758 ms |
| Average | 86.824 ms |
| p50 | **86.243 ms** |
| p95 | **89.941 ms** |
| Max | 102.272 ms |

### Traversal

| Depth | Results | p50 | p95 |
|---|---:|---:|---:|
| 1-hop | 14 | **86.884 ms** | **89.006 ms** |
| 2-hop | 307 | **88.918 ms** | 378.325 ms |
| 3-hop | 10,224 | **91.127 ms** | 204.578 ms |

### Aggregation

| Metric | Result |
|---|---:|
| Relationships counted | 200,000 |
| Queries | 100 |
| Min | 67.219 ms |
| Average | 105.819 ms |
| p50 | **86.243 ms** |
| p95 | 269.195 ms |
| Max | 415.026 ms |

### Mixed concurrency

| Metric | Result |
|---|---:|
| Workers | 10 |
| Requests | 100 |
| Reads / writes | 80 / 20 |
| Total time | 3.693 s |
| Throughput | 27.08 req/s |
| Overall p50 | **88.657 ms** |
| Overall p95 | 463.317 ms |
| Read p50 | 87.722 ms |
| Write p50 | 98.098 ms |

## Memgraph

### Loading

| Metric | Result |
|---|---:|
| Users | 91,489 |
| Relationships | 200,000 |
| User ingest | 5.59 s |
| Relationship ingest | 100.66 s |
| Total observed load | 106.25 s |
| Relationship throughput | 1,986.91 relationships/s |

### Indexed lookup

| Metric | Result |
|---|---:|
| Queries | 100 |
| Indexed property | `User.id` |
| Min | 146.357 ms |
| Average | 150.806 ms |
| p50 | **148.747 ms** |
| p95 | **159.014 ms** |
| Max | 187.455 ms |

### Traversal

| Depth | Results | p50 | p95 |
|---|---:|---:|---:|
| 1-hop | 14 | **158.713 ms** | 175.588 ms |
| 2-hop | 307 | **152.368 ms** | **158.095 ms** |
| 3-hop | 10,224 | **154.710 ms** | 172.409 ms |

### Aggregation

| Metric | Result |
|---|---:|
| Relationships counted | 200,000 |
| Queries | 100 |
| Min | 176.426 ms |
| Average | 188.419 ms |
| p50 | **180.567 ms** |
| p95 | **192.762 ms** |
| Max | 734.682 ms |

### Mixed concurrency

| Metric | Result |
|---|---:|
| Workers | 10 |
| Requests | 100 |
| Reads / writes | 80 / 20 |
| Total time | 3.051 s |
| Throughput | **32.78 req/s** |
| Overall p50 | **151.922 ms** |
| Overall p95 | 875.560 ms |
| Read p50 | 153.822 ms |
| Write p50 | 149.757 ms |

## CognoDB

### Loading

| Metric | Result |
|---|---:|
| Users | 91,489 |
| Relationships | 200,000 |
| Relationship throughput | 899.88 relationships/s |

### Point lookup

| Metric | Result |
|---|---:|
| Queries | 100 |
| p50 | **237.212 ms** |
| p95 | **249.243 ms** |
| Average | 238.851 ms |

### Indexed / filtered lookup

| Metric | Result |
|---|---:|
| Queries | 100 |
| Indexed property | `User.id` |
| p50 | **240.174 ms** |
| p95 | **258.890 ms** |
| Average | 242.274 ms |

### Traversal

| Depth | Results | p50 | p95 |
|---|---:|---:|---:|
| 1-hop | 14 | **249.049 ms** | 257.953 ms |
| 2-hop | 307 | **249.045 ms** | 282.959 ms |
| 3-hop | 10,224 | **281.402 ms** | 401.405 ms |

### Aggregation

| Metric | Result |
|---|---:|
| Relationships counted | 200,000 |
| Queries | 100 |
| p50 | **238.008 ms** |
| p95 | **248.295 ms** |
| Average | 239.860 ms |

### Mixed concurrency

| Metric | Result |
|---|---:|
| Workers | 10 |
| Requests | 100 |
| Reads / writes | 80 / 20 |
| Total time | 6.452 s |
| Throughput | **15.50 req/s** |
| Overall p50 | **247.779 ms** |
| Overall p95 | **1594.500 ms** |
| Read p50 | 246.563 ms |
| Write p50 | 739.644 ms |

## ArangoDB

### Loading

| Metric | Result |
|---|---:|
| Users | 91,489 |
| Relationships | 200,000 |
| User ingest | 29.86 s |
| Relationship ingest | 184.50 s |
| Total load | 214.36 s |
| Node throughput | 3,063.54 nodes/s |
| Relationship throughput | 1,084.01 relationships/s |

### Indexed lookup

| Metric | Result |
|---|---:|
| Queries | 100 |
| p50 | **291.125 ms** |
| p95 | **507.610 ms** |
| Average | 346.545 ms |

### Traversal

| Depth | Results | p50 | p95 | Queries |
|---|---:|---:|---:|---:|
| 1-hop | 14 | **264.419 ms** | 284.387 ms | 100 |
| 2-hop | 321 | **270.963 ms** | 349.459 ms | 100 |
| 3-hop | 10,545 | **3990.935 ms** | 4116.326 ms | 20 |

The 3-hop run used 20 measured queries after the original 100-query run became impractically slow.

### Aggregation

| Metric | Result |
|---|---:|
| Relationships counted | 200,000 |
| Queries | 30 |
| p50 | **301.049 ms** |
| p95 | **666.442 ms** |
| Average | 363.349 ms |

### Mixed concurrency

| Metric | Result |
|---|---:|
| Workers | 10 |
| Requests | 100 |
| Reads / writes | 80 / 20 |
| Total time | 15.062 s |
| Throughput | **6.64 req/s** |
| Overall p50 | **1314.967 ms** |
| Overall p95 | **2214.070 ms** |
| Read p50 | 1376.960 ms |
| Write p50 | 1298.372 ms |

## Cross-Database Summary

| Workload | Neo4j | Memgraph | CognoDB | ArangoDB |
|---|---:|---:|---:|---:|
| Indexed lookup p50 | **86.243 ms** | 148.747 ms | 240.174 ms | 291.125 ms |
| 1-hop p50 | **86.884 ms** | 158.713 ms | 249.049 ms | 264.419 ms |
| 2-hop p50 | **88.918 ms** | 152.368 ms | 249.045 ms | 270.963 ms |
| 3-hop p50 | **91.127 ms** | 154.710 ms | 281.402 ms | 3990.935 ms* |
| Aggregation p50 | **86.243 ms** | 180.567 ms | 238.008 ms | 301.049 ms |
| Concurrency throughput | 27.08 req/s | **32.78 req/s** | 15.50 req/s | 6.64 req/s |

*ArangoDB 3-hop used 20 queries; other traversal results used 100 queries.

## Observations

- Neo4j produced the lowest measured latency across the main lookup and traversal workloads.
- Memgraph achieved the highest mixed read/write throughput at 32.78 requests/sec.
- CognoDB completed the final observed 200,000-relationship benchmark and showed higher latency than Neo4j and Memgraph in the measured workloads.
- ArangoDB had substantially higher latency for 3-hop traversal and mixed concurrency in this test environment.
- Network latency is included in these client-side measurements.
- CPU and memory utilization were not directly measured.

## Limitations

- Cloud regions, resource sizes, and service configurations were not identical across providers.
- The benchmark uses one dataset and a fixed workload, so these results are not universal database rankings.
- ArangoDB 3-hop traversal used 20 measured iterations because the original 100-query run became impractically slow.
- CognoDB and the other databases were measured with the scripts and configurations recorded in the repository.
