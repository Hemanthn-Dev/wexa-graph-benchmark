\# Wexa Graph Database Benchmark



Benchmark project for evaluating graph database workloads using the

soc-pokec dataset.



\## Objective



The goal of this project is to evaluate graph database performance across

data loading and common graph workloads.



The benchmark focuses on:



\- Data loading

\- Lookup latency

\- Traversal latency

\- Aggregation latency

\- Concurrent throughput

\- Resource usage

\- Reproducibility and documented test conditions



\## Dataset



Dataset: soc-pokec-200k



Prepared dataset:



\- Expected relationships: 200,000

\- Expected unique nodes: 91,489

\- Duplicate edges: 0

\- Self-loops: 0

\- Malformed lines: 0

\- Minimum node ID: 1

\- Maximum node ID: 1,632,578



The dataset was validated before benchmarking.



\## CognoDB Test Environment



Database:



\- CognoDB

\- Python Neo4j-compatible Bolt driver

\- Python 3.10.5



Benchmark dataset state:



\- Users loaded: 91,489

\- Relationships loaded: 50,000



Note: The full 200,000 relationship load was not completed because

the Bolt connection repeatedly became defunct during relationship

ingestion. Therefore, query results in this run are based on the

50,000 relationships successfully loaded.



\## Loading Method



The initial loader used Python and the Bolt driver with batched Cypher

transactions.



The final loading experiment used two phases:



1\. Create all unique User nodes.

2\. Create relationships between the existing User nodes.



Batch size:



\- 2,000 records



Node ingestion successfully completed:



\- 91,489 users



Relationship ingestion reached:



\- 50,000 / 200,000 relationships



During relationship ingestion, the driver reported repeated connection

errors:



&#x20;   Failed to read from defunct connection

&#x20;   OSError('No data')



The loading process was stopped after the connection failures.



This loading result is therefore reported as an observed limitation,

not as a completed 200,000-edge benchmark.



\## Lookup Benchmark



Configuration:



\- Iterations: 100

\- Warm-up queries: 10

\- Query type: User ID lookup



Results:



| Metric | Result |

|---|---:|

| Queries | 100 |

| Minimum | 285.416 ms |

| Average | 464.450 ms |

| p50 | 408.677 ms |

| p95 | 801.277 ms |

| Maximum | 1638.035 ms |



\## Traversal Benchmark



Configuration:



\- Starting user: 1

\- Iterations: 50

\- Warm-up queries: 5

\- Traversal depth: 1 hop



Results:



| Metric | Result |

|---|---:|

| Neighbors found | 14 |

| Queries | 50 |

| Minimum | 290.311 ms |

| Average | 503.721 ms |

| p50 | 362.610 ms |

| p95 | 788.685 ms |

| Maximum | 4191.022 ms |



\## Aggregation Benchmark



Configuration:



\- Iterations: 30

\- Warm-up queries: 5

\- Operation: Count CONNECTED\_TO relationships



Results:



| Metric | Result |

|---|---:|

| Relationships counted | 50,000 |

| Queries | 30 |

| Minimum | 240.671 ms |

| Average | 259.826 ms |

| p50 | 246.443 ms |

| p95 | 288.668 ms |

| Maximum | 541.415 ms |



\## Concurrent Throughput Benchmark



Configuration:



\- Concurrent workers: 10

\- Total requests: 100

\- Workload: User lookup



Results:



| Metric | Result |

|---|---:|

| Workers | 10 |

| Requests | 100 |

| Total time | 14.596 seconds |

| Throughput | 6.85 requests/sec |

| p50 | 1303.085 ms |

| p95 | 2587.818 ms |



\## Resource Usage



CPU and memory utilization were not directly captured through the

available CognoDB interface during this benchmark run.



No resource values are fabricated or estimated.



\## Limitations



1\. The full 200,000 relationship dataset was not successfully loaded.

2\. Query benchmarks were therefore executed against 91,489 users and

&#x20;  50,000 relationships.

3\. Relationship ingestion experienced repeated Bolt connection failures.

4\. Resource utilization was not directly measured.

5\. The reported results represent the tested CognoDB environment and

&#x20;  configuration and should not be interpreted as universal database

&#x20;  performance characteristics.



\## Benchmark Scripts



The project contains scripts for:



\- CognoDB connection testing

\- Cypher testing

\- Dataset validation

\- Dataset preparation

\- CognoDB loading

\- Lookup benchmarking

\- Traversal benchmarking

\- Aggregation benchmarking

\- Concurrent throughput benchmarking



\## Reproducibility



The benchmark should be reproduced using the same:



\- Dataset

\- Database configuration

\- Query definitions

\- Batch size

\- Warm-up procedure

\- Iteration counts

\- Concurrency level

\- Measurement methodology



Results should be recorded together with the environment and test

conditions.



\## Conclusion



The benchmark successfully measured lookup, traversal, aggregation,

and concurrent query behavior on the tested CognoDB environment.



The main ingestion limitation observed during the experiment was

repeated Bolt connection failure during relationship loading.



Further benchmarking with the complete 200,000-edge dataset would be

required for a full-dataset comparison.

