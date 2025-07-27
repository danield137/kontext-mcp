"""Functional tests for KontextClient with mocked KustoClient."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any
import uuid

from kontext_mcp.kontext import KontextClient
from kontext_mcp.config import KontextConfig


@pytest.fixture
def mock_config():
    """Create a test configuration with dummy values."""
    return KontextConfig(
        cluster_uri="https://test.kusto.windows.net",
        database="TestDB",
        embedding_uri="https://test.openai.azure.com/openai/deployments/test-model/embeddings",
        memory_table="TestMemory",
    )


@pytest.fixture
def mock_kontext_client(mock_config: KontextConfig):
    """Create a KontextClient with mocked _connect method."""
    client = KontextClient(mock_config)

    # Mock the _connect method to avoid actual Kusto connection
    with patch.object(client, "_connect") as mock_connect:
        # Set up mock clients
        mock_query_client = MagicMock()
        mock_ingest_client = MagicMock()

        def mock_connect_side_effect():
            client.query_client = mock_query_client
            client.ingestion_client = mock_ingest_client

        mock_connect.side_effect = mock_connect_side_effect

        # Attach mock clients to the fixture for test access
        client._test_mock_query_client = mock_query_client
        client._test_mock_ingest_client = mock_ingest_client

        yield client


class TestKontextClientFunctional:
    """Functional tests for KontextClient methods."""

    def test_remember_calls_execute_with_correct_kql(self, mock_kontext_client: KontextClient):
        """Test that remember() constructs and executes correct KQL."""
        # Mock the _execute method
        with patch.object(mock_kontext_client, "_execute") as mock_execute:
            mock_execute.return_value = []

            # Test data
            test_id = str(uuid.uuid4())
            test_memory = "This is a test memory"
            test_type = "note"

            # Call remember
            mock_kontext_client.remember(test_id, test_memory, test_type)

            # Verify _execute was called once
            assert mock_execute.call_count == 1

            # Get the KQL command that was passed
            executed_kql = mock_execute.call_args[0][0]

            # Verify the KQL contains expected components
            assert f'"{test_id}"' in executed_kql
            assert f'"{test_memory}"' in executed_kql
            assert f'"{test_type}"' in executed_kql
            assert ".set-or-append" in executed_kql
            assert "TestMemory" in executed_kql  # table name from config
            assert "ai_embeddings(memory," in executed_kql
            assert mock_kontext_client.config.embedding_uri in executed_kql

    def test_remember_handles_special_characters(self, mock_kontext_client: KontextClient):
        """Test that remember() handles special characters in memory text."""
        with patch.object(mock_kontext_client, "_execute") as mock_execute:
            mock_execute.return_value = []

            # Test data with special characters
            test_id = "test-id"
            test_memory = 'Memory with "quotes" and \n newlines'
            test_type = "note"

            # Call remember - should not raise exception
            mock_kontext_client.remember(test_id, test_memory, test_type)

            # Verify _execute was called
            assert mock_execute.call_count == 1

    def test_recall_calls_execute_with_correct_kql(self, mock_kontext_client: KontextClient):
        """Test that recall() constructs and executes correct KQL."""
        # Mock the _execute method to return test data
        mock_results = [
            {"id": "1", "memory": "Test memory 1", "type": "note", "score": 0.95},
            {"id": "2", "memory": "Test memory 2", "type": "fact", "score": 0.88},
        ]

        with patch.object(mock_kontext_client, "_execute") as mock_execute:
            mock_execute.return_value = mock_results

            # Test data
            test_query = "test query"
            test_filters = {"type": "note", "category": "personal"}
            test_top_k = 5

            # Call recall
            results = mock_kontext_client.recall(test_query, test_filters, test_top_k)

            # Verify _execute was called once
            assert mock_execute.call_count == 1

            # Get the KQL query that was passed
            executed_kql = mock_execute.call_args[0][0]

            # Verify the KQL contains expected components
            assert f'ai_embeddings("{test_query}"' in executed_kql
            assert mock_kontext_client.config.embedding_uri in executed_kql
            assert "TestMemory" in executed_kql  # table name from config
            assert "series_cosine_similarity" in executed_kql
            assert f"top {test_top_k}" in executed_kql
            assert "project id, memory, type, score=sim" in executed_kql

            # Verify metadata filters are included
            assert 'tostring(meta.type) == "note"' in executed_kql
            assert 'tostring(meta.category) == "personal"' in executed_kql

            # Verify results are returned unchanged
            assert results == mock_results

    def test_recall_with_no_filters(self, mock_kontext_client: KontextClient):
        """Test that recall() works with empty metadata filters."""
        mock_results = [{"id": "1", "memory": "Test", "type": "note", "score": 0.9}]

        with patch.object(mock_kontext_client, "_execute") as mock_execute:
            mock_execute.return_value = mock_results

            # Call recall with no filters
            results = mock_kontext_client.recall("test query", {}, 3)

            # Verify _execute was called
            assert mock_execute.call_count == 1

            # Get the KQL query
            executed_kql = mock_execute.call_args[0][0]

            # Should not contain any metadata filter clauses
            assert "meta." not in executed_kql

            # Verify results
            assert results == mock_results

    def test_recall_with_numeric_filter(self, mock_kontext_client: KontextClient):
        """Test that recall() handles numeric metadata filters correctly."""
        mock_results = []

        with patch.object(mock_kontext_client, "_execute") as mock_execute:
            mock_execute.return_value = mock_results

            # Call recall with numeric filter
            test_filters = {"priority": 1, "status": "active"}
            mock_kontext_client.recall("test", test_filters, 5)

            # Get the KQL query
            executed_kql = mock_execute.call_args[0][0]

            # Verify numeric filter doesn't have quotes
            assert "meta.priority == 1" in executed_kql
            # Verify string filter has quotes
            assert 'tostring(meta.status) == "active"' in executed_kql

    def test_connect_is_called_on_query_access(self, mock_config):
        """Test that _connect is called when accessing query provider."""
        client = KontextClient(mock_config)

        with patch.object(client, "_connect") as mock_connect:
            mock_connect.return_value = None

            # Access query provider
            client.get_query_provider()

            # Verify _connect was called
            mock_connect.assert_called_once()

    def test_connect_is_called_on_ingest_access(self, mock_config):
        """Test that _connect is called when accessing ingest provider."""
        client = KontextClient(mock_config)

        with patch.object(client, "_connect") as mock_connect:
            mock_connect.return_value = None

            # Access ingest provider
            client.get_ingest_provider()

            # Verify _connect was called
            mock_connect.assert_called_once()
