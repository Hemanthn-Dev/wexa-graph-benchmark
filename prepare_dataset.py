from pathlib import Path

SOURCE_FILE = Path("soc-pokec-relationships.txt")
OUTPUT_FILE = Path("data/soc-pokec-200k.txt")

TARGET_RELATIONSHIPS = 200_000

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

relationship_count = 0
node_ids = set()

with SOURCE_FILE.open("r", encoding="utf-8") as source, \
     OUTPUT_FILE.open("w", encoding="utf-8") as output:

    for line in source:
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) != 2:
            continue

        source_id, target_id = parts

        output.write(f"{source_id}\t{target_id}\n")

        node_ids.add(source_id)
        node_ids.add(target_id)

        relationship_count += 1

        if relationship_count >= TARGET_RELATIONSHIPS:
            break

print("Dataset preparation complete")
print(f"Relationships: {relationship_count}")
print(f"Unique nodes: {len(node_ids)}")
print(f"Output: {OUTPUT_FILE}")