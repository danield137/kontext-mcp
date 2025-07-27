"""
MCP tools for remembering and recalling facts.
"""

from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from kontext_mcp.config import KontextConfig
from kontext_mcp.kontext import KontextClient
from kontext_mcp.logging_util import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class MemoryMetadata:
    category: str = "fact"
    root: Optional[str] = None


kontext_client = KontextClient(KontextConfig.from_env())


def remember(fact: str, meta: Optional[MemoryMetadata] = None) -> Dict[str, str]:
    """
    Stores a fact in the Kusto-backed memory table.

    :param fact: Text to remember.
    :param meta: Optional metadata object.
    :return: {"id": <uuid>}
    """
    fact_id = str(uuid4())
    metadata = meta or MemoryMetadata()

    kontext_client.ingest(fact_id, fact, metadata)

    return {"id": fact_id}


def recall(
    query: str,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Retrieves relevant memories.

    :param query: Search query.
    :param top_k: Max rows.
    :return: List of {id, fact, meta, score}
    """
    logger.info(f"Recalling facts for query: {query[:50]}...")
    results = kontext_client.recall(query, top_k)

    return results
