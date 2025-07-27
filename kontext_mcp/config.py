from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, frozen=True)
class KontextConfig:
    cluster_uri: str
    database: str
    embedding_uri: str
    memory_table: Optional[str] = "Memory"

    @property
    def query_endpoint(self) -> str:
        """Get the query endpoint URL."""
        return self.cluster_uri

    @classmethod
    def from_env(cls) -> KontextConfig:
        """Create configuration from environment variables."""
        kusto_cluster = os.getenv("KUSTO_CLUSTER")
        if not kusto_cluster:
            raise ValueError("KUSTO_CLUSTER environment variable is required")

        kusto_database = os.getenv("KUSTO_DATABASE")
        if not kusto_database:
            raise ValueError("KUSTO_DATABASE environment variable is required")

        embedding_uri = os.getenv("EMBEDDING_URI")
        if not embedding_uri:
            raise ValueError("EMBEDDING_URI environment variable is required")

        return cls(
            cluster_uri=kusto_cluster,
            database=kusto_database,
            embedding_uri=embedding_uri,
            memory_table=os.getenv("KUSTO_TABLE", "Memory"),
        )
