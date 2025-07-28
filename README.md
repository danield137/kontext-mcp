# Kontext MCP Server

Kontext is a thin Python MCP server that provides portable, provider-agnostic memory on top of Azure Data Explorer (Kusto). It exposes two core tools—`remember` and `recall`—to bridge the gap between simple vector stores and a true "context engine."

## Features

- **remember**: Store facts with automatic embedding generation using Kusto's `ai_embeddings()` plugin
- **recall**: Retrieve semantically similar facts using cosine similarity search
- **FastMCP Integration**: Built on the FastMCP framework for easy tool registration and schema generation
- **Kusto Backend**: Leverages Azure Data Explorer for scalable storage and querying
- **Minimal Design**: Start simple with embeddings + cosine similarity (advanced scoring features to be added later)



## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
