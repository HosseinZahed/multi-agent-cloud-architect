import unittest
from unittest.mock import MagicMock
import sys
sys.path.append('../')


class TestPersistentChromaDBClient(unittest.TestCase):

    def setUp(self):
        from src.vectordb_provider import PersistentChromaDBClient
        self.db_path = "test_db"
        self.client = PersistentChromaDBClient(db_path=self.db_path)
        #self.client.client = MagicMock()  # Mock the ChromaDB client

    def test_initialization(self):
        self.assertEqual(self.client.db_path, self.db_path)
        self.assertIsNotNone(self.client.client)
        self.assertIsNotNone(self.client.embedding_function)

    def test_create_collection(self):
        collection_name = "test_collection"
        description = "Test description"
        self.client.client.get_or_create_collection = MagicMock()

        self.client.create_collection(collection_name, description)

        self.client.client.get_or_create_collection.assert_called_once_with(
            name=collection_name,
            embedding_function=self.client.embedding_function,
            metadata={"description": description, "created": unittest.mock.ANY}
        )

    def test_get_collection(self):
        collection_name = "test_collection"
        self.client.client.get_collection = MagicMock()

        self.client.get_collection(collection_name)

        self.client.client.get_collection.assert_called_once_with(
            name=collection_name)

    def test_add_documents(self):
        collection_name = "test_collection"
        ids = ["id1", "id2"]
        documents = ["doc1", "doc2"]
        metadatas = [{"key": "value1"}, {"key": "value2"}]

        mock_collection = MagicMock()
        self.client.get_collection = MagicMock(return_value=mock_collection)

        self.client.add_documents(collection_name, ids, documents, metadatas)

        self.client.get_collection.assert_called_once_with(collection_name)
        mock_collection.add.assert_called_once_with(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )


if __name__ == "__main__":
    unittest.main()
