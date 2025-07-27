"""End-to-end tests for KontextClient against a real Kusto cluster."""

import pytest
import uuid

from kontext_mcp.kontext import KontextClient
from kontext_mcp.config import KontextConfig

# Hard-coded test cluster and embedding URIs as specified
TEST_CLUSTER_URI = "https://danieldror1.swedencentral.dev.kusto.windows.net/"
TEST_EMBEDDING_URI = "https://dolevtest.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15;managed_identity=system"


@pytest.fixture
def kx_config():
    """Create configuration for E2E tests using real cluster."""
    database = "Kontext"
    memory_table = "Memory"

    return KontextConfig(
        cluster_uri=TEST_CLUSTER_URI, database=database, embedding_uri=TEST_EMBEDDING_URI, memory_table=memory_table
    )


@pytest.fixture
def kontext_client(kx_config: KontextConfig):
    """Create a real KontextClient for E2E testing."""
    return KontextClient(kx_config)


@pytest.fixture
def ready_kontext_client(kontext_client: KontextClient):
    """Ensure the KontextClient is ready for E2E tests."""
    if not kontext_client.is_ready():
        kontext_client.setup()
    else:
        # Clear the memory table to start fresh for E2E tests
        kontext_client.get_query_provider().execute(
            kontext_client.config.database, f".clear table {kontext_client.config.memory_table} data"
        )
    return kontext_client


class TestKontextClientE2E:
    @pytest.mark.e2e
    def test_e2e_setup_check(self, ready_kontext_client: KontextClient):
        """Test that E2E tests are properly configured and can be run."""

        # Verify the client is properly configured
        assert ready_kontext_client.config.cluster_uri == TEST_CLUSTER_URI
        assert ready_kontext_client.config.embedding_uri == TEST_EMBEDDING_URI
        assert ready_kontext_client.config.database is not None
        assert ready_kontext_client.config.memory_table is not None
        assert ready_kontext_client.is_ready(), "KontextClient is not ready for E2E tests"

    @pytest.mark.e2e
    def test_remember_and_recall_e2e(self, ready_kontext_client: KontextClient):
        """Test remember and recall functions against real cluster."""

        # Generate unique test data to avoid conflicts
        test_memory = f"I love Kusto! it's such a great database for E2E testing "
        test_type = "fact"

        try:
            # Test remember function
            ready_kontext_client.remember(test_memory, test_type)

            # Wait a moment for ingestion to complete (Kusto streaming ingestion)
            import time

            time.sleep(2)

            # Test recall function - search for our test memory
            results = ready_kontext_client.recall(query="Kusto", filters={}, top_k=1)

            # Verify results structure
            assert isinstance(results, list)

            # If we find our memory, verify its structure
            found_memory = results[0]

            if found_memory:
                # Verify the result has expected fields
                assert "item" in found_memory
                assert "type" in found_memory
                assert "sim" in found_memory

                # Verify content matches what we stored
                assert found_memory["item"] == test_memory
                assert found_memory["type"] == test_type
                assert isinstance(found_memory["sim"], (int, float))

        except Exception as e:
            pytest.fail(f"E2E test failed with exception: {e}")

    @pytest.mark.e2e
    def test_multiple_memories_e2e(self, ready_kontext_client: KontextClient):
        """Test storing and retrieving multiple memories."""
        try:
            # Create multiple test memories
            memories = [
                {"item": "I love dogs", "type": "fact"},
                {"item": "I hate snakes", "type": "fact"},
                {
                    "item": "We had a conversation about animals you like and dislike",
                    "type": "checkpoint",
                },
            ]

            # Store all memories
            for memory in memories:
                ready_kontext_client.remember(memory["item"], memory["type"])

            # Wait for ingestion
            import time

            time.sleep(3)

            # Search for animal-related memories
            animal_results = ready_kontext_client.recall(query="animals", top_k=10)

            assert isinstance(animal_results, list)
            assert len(animal_results) == 3

            animal_facts = ready_kontext_client.recall(query="animals", filters={"type": "fact"}, top_k=10)
            assert isinstance(animal_facts, list)
            assert len(animal_facts) == 2

        except Exception as e:
            pytest.fail(f"Multiple memories E2E test failed: {e}")

    @pytest.mark.e2e
    def test_empty_recall_e2e(self, ready_kontext_client: KontextClient):
        """Test recall with query that should return no results."""
        try:
            # Search for something very unlikely to exist
            results = ready_kontext_client.recall(
                query=f"very_unique_nonexistent_query_{uuid.uuid4()}", filters={}, top_k=5
            )

            # Should return empty list, not raise exception
            assert isinstance(results, list)

        except Exception as e:
            pytest.fail(f"Empty recall E2E test failed: {e}")
