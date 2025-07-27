import time
from typing import Any, Dict, List, Optional, Protocol
from azure.identity import DefaultAzureCredential, ChainedTokenCredential
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.response import KustoResponseDataSet
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.ingest import QueuedIngestClient, KustoStreamingIngestClient

from kontext_mcp.config import KontextConfig
from kontext_mcp.logging_util import get_logger

logger = get_logger(__name__)


class KontextProtocol(Protocol):
    @property
    def config(self) -> KontextConfig:
        """Return the configuration for the Kontext client."""
        ...

    def is_ready(self) -> bool:
        """Check if the Kusto database is ready for queries."""
        ...

    def setup(self) -> None:
        """Set up the working tables."""
        ...

    def remember(self, item: str, type: str, scope: Optional[str] = "global") -> str:
        """Ingest a memory item into the Kusto database. Returns the ID of the ingested fact."""

    def recall(
        self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Recall facts from the Kusto database based on a query and metadata filters."""


MEMORY_TABLE_SCHEMA = "id:string,item:string,type:string,scope:string,creation_time:datetime,embedding:dynamic"


class KontextClient(KontextProtocol):
    _config: KontextConfig
    _kusto_client: KustoClient | None = None
    _ingest_client: QueuedIngestClient | None = None
    # Cache the value of is_ready to avoid repeated checks.
    _ready: bool = False

    def __init__(self, config: KontextConfig):
        """
        Initialize the Kusto client with the cluster URI.
        """
        self._config = config

    def _get_credential(self) -> ChainedTokenCredential:
        return DefaultAzureCredential(
            exclude_shared_token_cache_credential=True,
            exclude_interactive_browser_credential=False,
        )

    def _connect(self) -> None:
        if not self._kusto_client:
            credential = self._get_credential()
            kcsb = KustoConnectionStringBuilder.with_azure_token_credential(
                connection_string=self.config.cluster_uri, credential=credential
            )
            self._kusto_client = KustoClient(kcsb)
            self._ingest_client = KustoStreamingIngestClient(kcsb)

    def _execute(self, kql: str, database: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            # Build connection string using device authentication
            client = self.get_query_provider()
            # Execute query
            db_name = database or self.config.database
            response = client.execute(db_name, kql)

            # Convert response to list of dictionaries
            results = []
            if response.primary_results:
                primary_result = response.primary_results[0]
                for row in primary_result:
                    results.append(dict(zip([col.column_name for col in primary_result.columns], row)))

            return results

        except KustoServiceError as e:
            logger.error(f"Kusto service error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise

    def get_query_provider(self) -> KustoClient:
        self._connect()
        return self._kusto_client

    def get_ingest_provider(self) -> KustoStreamingIngestClient:
        self._connect()
        return self._ingest_client

    @property
    def config(self) -> KontextConfig:
        """Return the configuration for the Kontext client."""
        return self._config

    def setup(self) -> None:
        """Set up the working tables. If already set up, this is a no-op."""
        try:
            if self.is_ready():
                return
            self._connect()
            # Create the memory table (kusto creation command just skips if it exists)
            create_table_kql = f"""
            .create table {self.config.memory_table} ({MEMORY_TABLE_SCHEMA})
            """
            self._execute(create_table_kql, self.config.database)
            logger.info(f"Memory table '{self.config.memory_table}' is ready.")
        except KustoServiceError as e:
            logger.error(f"Kusto service error during setup: {e}")
            raise

    def is_ready(self) -> bool:
        """Check if the Kusto database is ready for queries."""
        # no need to check again if already ready (unless we called a destructive command, which we don't have yet)
        if self._ready:
            return True

        try:
            self._connect()
            # Perform a simple query to check readiness
            resp: KustoResponseDataSet = self._execute(".show database cslschema", self.config.database)
            if resp and len(resp) > 0:
                memory_table = next(filter(lambda x: x["TableName"] == self.config.memory_table, resp), None)
                if memory_table:
                    self._ready = memory_table["Schema"] == MEMORY_TABLE_SCHEMA
        except KustoServiceError as e:
            logger.error(f"Kusto service error: {e}")

        except Exception as e:
            logger.error(f"Error checking database readiness: {e}")

        return self._ready

    def remember(self, item: str, type: str, scope: Optional[str] = "global") -> str:
        try:
            self.setup()
            id = f"fact_{int(time.time())}"
            command = f""".set-or-append {self.config.memory_table} <|
            print
                id="{id}",
                item="{item}",
                type="{type}",
                scope="{scope}",
                creation_time=now(),
                embeddings=toscalar(evaluate ai_embeddings("{item}", "{self.config.embedding_uri}"))
            """

            self._execute(command, self.config.database)
            return id
        except Exception as e:
            logger.error(f"Error ingesting memory {id}: {e}")
            raise

    def recall(
        self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: Optional[int] = 10
    ) -> List[Dict[str, Any]]:
        try:
            self.setup()
            # Build the query with inline embedding generation
            kql_query = f"""
            let q_vec = toscalar(evaluate ai_embeddings("{query}", "{self.config.embedding_uri}"));
            {self.config.memory_table}
            | extend sim = series_cosine_similarity(embedding, q_vec)
            | where sim > 0
            """

            if filters:
                if "type" in filters:
                    kql_query += f" | where type == '{filters['type']}'"
                if "scope" in filters:
                    kql_query += f" | where scope == '{filters['scope']}'"
            results = self._execute(kql_query, self.config.database)

            return results

        except Exception as e:
            logger.error(f"Error recalling facts for query '{query}': {e}")
            raise
