# Kontext MCP Server

[![Install with UVX in VS Code](https://img.shields.io/badge/VS_Code-Install_Kontext_MCP_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=kontext-mcp&config=%7B%22command%22%3A%20%22uvx%22%2C%22args%22%3A%20%5B%22kontext-mcp%22%5D%2C%22env%22%3A%20%7B%22KUSTO_CLUSTER%22%3A%20%22https%3A%2F%2Fyour-cluster.kusto.windows.net%2F%22%2C%22KUSTO_DATABASE%22%3A%20%22your-database%22%2C%22KUSTO_TABLE%22%3A%20%22Memory%22%2C%22EMBEDDING_URI%22%3A%20%22https%3A%2F%2Fyour-openai.azure.com%2Fopenai%2Fdeployments%2Ftext-embedding-3-large%2Fembeddings%3Fapi-version%3D2023-05-15%3Bmanaged_identity%3Dsystem%22%7D) [![PyPI Downloads](https://static.pepy.tech/badge/kontext-mcp)](https://pepy.tech/projects/kontext-mcp)

**Own your Kontext: portable, provider‑agnostic memory for AI agents. Never repeat yourself again.**

Kontext transforms Azure Data Explorer (Kusto) into a sophisticated context engine that goes beyond simple vector storage. While traditional vector DBs only store embeddings, Kontext provides layered memory with rich temporal and usage signals—combining recency, frequency, semantic similarity, pins, and decay scoring.

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

## Usage Example

Here's how to incorporate Kontext into your AI workflow by adding instructions to your `.instructions.md` file:

```markdown
# .instructions.md

- Use the memory mcp (Kontext-mcp) to remember useful information along the way, group the scope by {project_name} (e.g. `scope=my_cool_project`).
  Examples of memory entries:
  - **Context**: What is the current state of the project? There should always be one, most up to date. This should be a summarized and distilled snapshot of "up-to-date" information.
  - **Thoughts**: Things that the user mentions along the way, like: "This feature should be done better, using X or Y, but not right now, because I need to focus on Z first."
  - **Facts**: Things the use mentions along the way that might be useful later, like: "The project is using a specific package version because of some limitation on the target platform, or because of a bug in the package."
  Use the memory to enhance the context of the conversation, and to provide more relevant and useful design. 
- Load context from memory when starting a new conversation, or when the context is not clear.
- Use the memory when you asked to design or review non-trivial code, or when you are asked to provide a design for a new feature.
- When finished with a task / session, ask the user whether to store the current context, thoughts, and facts in memory. If so, summarize and distill key points, load previous context, merge them together in a meaningful way, and store them in memory (call `remember()` with the appropriate scope and `type=context`).
```

This approach ensures your AI agent:
- Maintains project continuity across conversations
- Captures and recalls important decisions and constraints
- Builds a rich knowledge base specific to each project scope

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
