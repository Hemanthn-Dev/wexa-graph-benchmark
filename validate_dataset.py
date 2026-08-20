from pathlib import Path

DATASET = Path("data/soc-pokec-200k.txt")

relationships = 0
unique_nodes = set()
unique_edges = set()
duplicate_edges = 0
self_loops = 0
malformed_lines = 0

with DATASET.open("r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) != 2:
            malformed_lines += 1
            continue

        source, target = parts

        relationships += 1
        unique_nodes.add(source)
        unique_nodes.add(target)

        edge = (source, target)

        if edge in unique_edges:
            duplicate_edges += 1
        else:
            unique_edges.add(edge)

        if source == target:
            self_loops += 1

print("Dataset validation")
print("------------------")
print(f"Relationships: {relationships}")
print(f"Unique nodes: {len(unique_nodes)}")
print(f"Unique edges: {len(unique_edges)}")
print(f"Duplicate edges: {duplicate_edges}")
print(f"Self-loops: {self_loops}")
print(f"Malformed lines: {malformed_lines}")

if unique_nodes:
    numeric_nodes = [int(node) for node in unique_nodes]
    print(f"Minimum node ID: {min(numeric_nodes)}")
    print(f"Maximum node ID: {max(numeric_nodes)}")

if (
    relationships == 200_000
    and malformed_lines == 0
):
    print("\n✅ Basic dataset validation passed")
else:
    print("\n⚠️ Dataset needs review")