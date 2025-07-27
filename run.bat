@echo off
set KUSTO_CLUSTER=https://danieldror1.swedencentral.dev.kusto.windows.net/
set KUSTO_DATABASE=Kontext
set EMBEDDING_URI=https://dolevtest.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15;managed_identity=system
set KUSTO_TABLE=Memory
uvx .