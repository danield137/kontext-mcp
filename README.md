# Kontext MCP Server

[![Install with UVX in VS Code](https://img.shields.io/badge/VS_Code-Install_Kontext_MCP_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=kontext-mcp&config=%7B%22command%22%3A%20%22uvx%22%2C%22args%22%3A%20%5B%22kontext-mcp%22%5D%2C%22env%22%3A%20%7B%22KUSTO_CLUSTER%22%3A%20%22https%3A%2F%2Fyour-cluster.kusto.windows.net%2F%22%2C%22KUSTO_DATABASE%22%3A%20%22your-database%22%2C%22KUSTO_TABLE%22%3A%20%22Memory%22%2C%22EMBEDDING_URI%22%3A%20%22https%3A%2F%2Fyour-openai.azure.com%2Fopenai%2Fdeployments%2Ftext-embedding-3-large%2Fembeddings%3Fapi-version%3D2023-05-15%3Bmanaged_identity%3Dsystem%22%7D) [![PyPI Downloads](https://static.pepy.tech/badge/kontext-mcp)](https://pepy.tech/projects/kontext-mcp)

**Own your Kontext: portable, provider‑agnostic memory for AI agents. Never repeat yourself again.**

Kontext transforms Azure Data Explorer (Kusto) into a sophisticated context engine that goes beyond simple vector storage. While traditional vector DBs only store embeddings, Kontext provides layered memory with rich temporal and usage signals—combining recency, frequency, semantic similarity, pins, and decay scoring.

## Overview

Kontext provides two powerful MCP tools for intelligent memory management:

### `remember`
```python
remember(fact: str, type: str, scope: Optional[str] = "global") -> str
```
Stores a memory item in the Kusto-backed memory store with automatic embedding generation.

**Parameters:**
- `fact`: Text to remember
- `type`: Memory type (`"fact"`, `"context"`, or `"thought"`)
- `scope`: Memory scope (defaults to `"global"`)

**Returns:** Unique ID of the stored memory

### `recall`
```python
recall(query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 10) -> List[Dict[str, Any]]
```
Retrieves relevant memories using semantic similarity and KQL-powered ranking.

**Parameters:**
- `query`: Search query for semantic matching
- `filters`: Optional filters (e.g., `{"type": "fact", "scope": "global"}`)
- `top_k`: Maximum number of results to return

**Returns:** List of memory objects with metadata (`id`, `fact`, `type`, `scope`, `creation_time`, `sim`)

## Why Kontext?

**The Gap**: Agents need intelligent memory that considers not just semantic similarity, but also temporal patterns, usage frequency, and contextual relevance. Most vector databases fall short by ignoring these rich signals and locking you into a single cloud provider.

**The Solution**: Kontext leverages Kusto's powerful query language (KQL) to score and rank memories using multiple dimensions:

```kql
// Conceptual query for scoring memories
Memory 
| extend score = w_t * exp(-ago(ingest)/7d) * 
                 w_f * log(1+hits) * 
                 w_s * cosine_sim * 
                 w_p * pin 
| top 20 by score
```

## Key Benefits

- **Temporal Reasoning**: Native timestamp handling, retention policies, and time-decay scoring
- **Semantic Retrieval**: Built-in vector columns with cosine similarity search  
- **Expressive Ranking**: KQL enables complex scoring that weighs time, frequency, pins, and semantics
- **Cost Effective**: Free tier with instant provisioning and predictable scaling
- **True Portability**: Simple MCP API keeps your models and cloud providers interchangeable

## Architecture

```
Agent ⇆ Kontext MCP
         ├── remember(fact, meta)
         └── recall(query, meta)
                  ↓
           Azure Kusto
```

**Ingest**: Text splitting → embedding generation → vector + metadata storage  
**Retrieve**: KQL-powered scoring combines temporal, frequency, semantic, and pin signals

## Quick Setup

Add Kontext to your MCP settings with the following configuration:

```json
{
  "servers": {
    "kontext": {
      "type": "stdio",
      "command": "uvx",
      "args": ["kontext-mcp"],
      "env": {
        "KUSTO_CLUSTER": "https://your-cluster.kusto.windows.net/",
        "KUSTO_DATABASE": "your-database",
        "KUSTO_TABLE": "Memory",
        "EMBEDDING_URI": "https://your-openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15;managed_identity=system"
      }
    }
  }
}
```

**Environment Variables:**
- `KUSTO_CLUSTER`: Your Azure Data Explorer cluster URL
- `KUSTO_DATABASE`: Database name for storing memories
- `KUSTO_TABLE`: Table name for memory storage (default: "Memory")
- `EMBEDDING_URI`: Azure OpenAI endpoint for embedding generation

## Current Features

- **remember**: Store facts with automatic embedding generation using Kusto's `ai_embeddings()` plugin
- **recall**: Retrieve semantically similar facts using cosine similarity search
- **FastMCP Integration**: Built on the FastMCP framework for easy tool registration and schema generation
- **Kusto Backend**: Leverages Azure Data Explorer for scalable storage and querying

## Roadmap

- **Advanced Scoring**: Multi-dimensional ranking with temporal decay, frequency weighting, and pin support
- **Memory Tiers**: Short-term context, working memory, and long-term fact storage
- **Hosted Embeddings**: Optional E5 model hosting to reduce setup friction
- **Enhanced Caching**: Multi-tier memory management and query optimization



## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
