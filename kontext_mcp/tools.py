"""
MCP tools for remembering and recalling facts.
"""

from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from kontext_mcp.config import KontextConfig
from kontext_mcp.kontext import KontextClient
from kontext_mcp.logging_util import get_logger

logger = get_logger(__name__)


kontext_client = KontextClient(KontextConfig.from_env())


class MemoryType:
    FACT: Literal["fact"] = "fact"
    CONTEXT: Literal["context"] = "context"
    THOUGHT: Literal["thought"] = "thought"


def remember(fact: str, type: str, scope: Optional[str] = "global") -> Dict[str, str]:
    """
    Stores a memory item in the Kusto-backed memory store.

    :param item: Text to remember.
    :param type: Type of the memory item. Options are:
        "fact" - General knowledge. Can be as many facts as needed.
        "context" - One per scope. State or context information. For example, summarized context of a conversation on a topic.
        "thought" - Mental note. Could be something useful to remember, but not a fact, like a plan or idea.
    :param scope: Scope of the memory item. Defaults to "global".
        Useful scopes are project names, object names (e.g. people) or mental groupings (e.g. "work", "personal").
    :return: {"id": str}
    """
    fact_id = str(uuid4())
    return kontext_client.remember(fact, type, scope)


def recall(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Retrieves relevant memories.

    :param query: Search query.
    :param filters: Optional filters to apply to the results, e.g. {"type": "fact", "scope": "global"}.
    :param top_k: Max rows.
    :return: List of {id, fact, type, scope, creation_time, sim}
    """
    logger.info(f"Recalling facts for query: {query[:50]}...")
    results = kontext_client.recall(query, filters, top_k)

    return results
