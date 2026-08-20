# Wexa Graph Database Benchmark

A reproducible benchmark comparing graph database performance using the `soc-pokec-200k` dataset.

## Databases

- CognoDB
- Neo4j
- Memgraph
- ArangoDB

## Dataset

| Metric | Value |
|---|---:|
| Dataset | `soc-pokec-200k` |
| Unique users | 91,489 |
| Relationships | 200,000 |

The same prepared dataset was used for the four database experiments.

## Benchmarks

The project measures:

1. Indexed/filtered lookup latency
2. Graph traversal latency: 1-hop, 2-hop, and 3-hop
3. Relationship aggregation latency
4. Mixed concurrency: 10 workers, 100 requests, 80% reads and 20% writes
5. Data loading time and throughput

Latency is reported primarily using p50 and p95. See [`results.md`](results.md) for the detailed benchmark record and methodology.

## Key Results

### Indexed lookup

| Database | p50 | p95 |
|---|---:|---:|
| Neo4j | **86.243 ms** | **89.941 ms** |
| Memgraph | 148.747 ms | 159.014 ms |
| CognoDB | 240.174 ms | 258.890 ms |
| ArangoDB | 291.125 ms | 507.610 ms |

### Traversal p50

| Database | 1-hop | 2-hop | 3-hop |
|---|---:|---:|---:|
| Neo4j | **86.884 ms** | **88.918 ms** | **91.127 ms** |
| Memgraph | 158.713 ms | 152.368 ms | 154.710 ms |
| CognoDB | 249.049 ms | 249.045 ms | 281.402 ms |
| ArangoDB | 264.419 ms | 270.963 ms | 3990.935 ms* |

*ArangoDB 3-hop was completed with 20 measured iterations after the original 100-iteration run became impractically slow.

### Aggregation p50

| Database | p50 | p95 |
|---|---:|---:|
| Neo4j | **86.243 ms** | 269.195 ms |
| Memgraph | 180.567 ms | **192.762 ms** |
| CognoDB | 238.008 ms | 248.295 ms |
| ArangoDB | 301.049 ms | 666.442 ms |

### Mixed concurrency

| Database | Throughput | p50 | p95 |
|---|---:|---:|---:|
| Memgraph | **32.78 req/s** | 151.922 ms | 875.560 ms |
| Neo4j | 27.08 req/s | **88.657 ms** | 463.317 ms |
| CognoDB | 15.50 req/s | 247.779 ms | 1594.500 ms |
| ArangoDB | 6.64 req/s | 1314.967 ms | 2214.070 ms |

## Data Loading

| Database | Users | Relationships | Load time |
|---|---:|---:|---:|
| Neo4j | 91,489 | 200,000 | **25.85 s** |
| Memgraph | 91,489 | 200,000 | 106.25 s* |
| CognoDB | 91,489 | 200,000 | Recorded in benchmark output |
| ArangoDB | 91,489 | 200,000 | 214.36 s |

*Memgraph relationship loading was 100.66 seconds; total observed loading time was 106.25 seconds.

## Summary

Based on these benchmark runs:

- **Neo4j** delivered the lowest measured latency across the main lookup, traversal, and aggregation workloads.
- **Memgraph** achieved the highest throughput in the mixed read/write concurrency test at 32.78 requests/sec.
- **CognoDB** completed the final observed 200,000-relationship benchmark and showed higher latency than Neo4j and Memgraph in the measured workloads.
- **ArangoDB** showed substantially higher latency for 3-hop traversal and mixed concurrency in this test environment.

These results are specific to the tested dataset, client implementations, cloud configurations, network conditions, and workload definitions. They are not universal database rankings.

## Repository Structure

```text
.
├── data/
├── benchmark_aggregation.py
├── benchmark_concurrency.py
├── benchmark_lookup.py
├── benchmark_traversal.py
├── benchmark_neo4j_*.py
├── benchmark_memgraph_*.py
├── benchmark_arango_*.py
├── load_cognodb.py
├── load_neo4j.py
├── load_memgraph.py
├── load_memgraph_relationships.py
├── load_arango.py
├── results.md
└── README.md
```

## Reproduction

Create a Python virtual environment and install the dependencies used by the benchmark scripts. Configure database credentials through environment variables or a local `.env` file. Never commit credentials, passwords, or private certificates.

Load the target database first, then run its benchmark scripts. For example:

```bash
python load_neo4j.py
python benchmark_neo4j_indexed.py
python benchmark_neo4j_traversal.py
python benchmark_neo4j_aggregation.py
python benchmark_neo4j_concurrency.py
```

Equivalent scripts are provided for Memgraph and ArangoDB. CognoDB uses the original `benchmark_*.py` scripts.

## Limitations

- Cloud-hosted database configurations and regions were not identical.
- Network latency is included in request measurements.
- CPU and memory utilization were not directly measured.
- ArangoDB 3-hop traversal used 20 measured iterations because the original 100-query run became impractically slow.
- The benchmark uses a relatively small dataset and a fixed workload, so results should be interpreted in that context.

## Detailed Results

See [`results.md`](results.md) for the detailed results, configurations, observations, and limitations.
