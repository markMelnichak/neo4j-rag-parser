from __future__ import annotations

import os
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Dict, Iterable

from neo4j import GraphDatabase
from dotenv import load_dotenv


@dataclass
class Neo4jConfig:
    uri: str
    user: str
    password: str
    database: str


def load_neo4j_config() -> Neo4jConfig:
    load_dotenv()
    return Neo4jConfig(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        user=os.getenv("NEO4J_USER", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password123"),
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
    )


class Neo4jImporter(AbstractContextManager):
    def __init__(self, config: Neo4jConfig) -> None:
        self.config = config
        self.driver = GraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password),
        )

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.driver.close()

    def upsert_node(self, node: Dict[str, Any]) -> None:
        label = node["label"]
        query = f"""
        MERGE (n:{label} {{name: $name}})
        SET n.normalized_name = $normalized_name,
            n.aliases = $aliases,
            n.source = $source
        """
        if label == "Concept":
            query += "\nSET n.description = coalesce(n.description, $description)"

        self.driver.execute_query(
            query,
            name=node["name"],
            normalized_name=node["normalized_name"],
            aliases=node["aliases"],
            source=node["source"],
            description=node.get("description"),
            database_=self.config.database,
        )

    def upsert_relation(self, rel: Dict[str, Any]) -> None:
        query = f"""
        MATCH (a:{rel['from_label']} {{name: $from_name}})
        MATCH (b:{rel['to_label']} {{name: $to_name}})
        MERGE (a)-[r:{rel['type']}]->(b)
        SET r.source = $source,
            r.evidence = $evidence,
            r.confidence = $confidence,
            r.rule = $rule
        """
        self.driver.execute_query(
            query,
            from_name=rel["from_name"],
            to_name=rel["to_name"],
            source=rel["source"],
            evidence=rel["evidence"],
            confidence=rel["confidence"],
            rule=rel["rule"],
            database_=self.config.database,
        )

    def import_payload(self, payload: Dict[str, Any]) -> None:
        for node in payload["nodes"]:
            self.upsert_node(node)

        for rel in payload["relations"]:
            self.upsert_relation(rel)

def main() -> None:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Import graph JSON payload to Neo4j")
    parser.add_argument("--input", required=True, help="Path to graph JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    payload = json.loads(input_path.read_text(encoding="utf-8"))

    config = load_neo4j_config()

    with Neo4jImporter(config) as importer:
        importer.import_payload(payload)

    print(
        f"Imported graph payload: "
        f"nodes={len(payload.get('nodes', []))}, "
        f"relations={len(payload.get('relations', []))}, "
        f"source={payload.get('source')}"
    )


if __name__ == "__main__":
    main()
