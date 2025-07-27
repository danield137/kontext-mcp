from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv, find_dotenv


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
        """Create configuration from environment variables, with .env file fallback."""
        required_vars = ["KUSTO_CLUSTER", "KUSTO_DATABASE", "EMBEDDING_URI"]
        
        # First attempt to read from environment
        env_values = {var: os.getenv(var) for var in required_vars}
        
        # If any required variables are missing, try loading from .env file
        if not all(env_values.values()):
            load_dotenv(find_dotenv())
            # Re-read after loading .env
            env_values = {var: os.getenv(var) for var in required_vars}
        
        # Check if we still have missing variables
        missing_vars = [var for var, value in env_values.items() if not value]
        if missing_vars:
            raise ValueError(f"{', '.join(missing_vars)} environment variable(s) are required")

        return cls(
            cluster_uri=env_values["KUSTO_CLUSTER"],
            database=env_values["KUSTO_DATABASE"],
            embedding_uri=env_values["EMBEDDING_URI"],
            memory_table=os.getenv("KUSTO_TABLE", "Memory"),
        )
