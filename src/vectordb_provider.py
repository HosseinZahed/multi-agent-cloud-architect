import os
from datetime import datetime
from chromadb import PersistentClient, ClientAPI, Collection
from chromadb.utils import embedding_functions
import logging


class PersistentChromaDBClient:
    def __init__(self):
        self.client = PersistentClient("db")
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def get_client(self) -> ClientAPI:
        return self.client

    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a collection from the database.
        """
        return self.client.get_collection(name=collection_name)

    def get_default_embedding_function(self):
        """
        Get the default embedding function.
        """
        return self.embedding_function

    def create_collection(self,
                          collection_name: str,
                          description: str = None,
                          embedding_function: embedding_functions.EmbeddingFunction = None
                          ) -> Collection:
        """
        Create a collection in the database.
        """
        return self.client.get_or_create_collection(name=collection_name,
                                                    embedding_function=embedding_function or
                                                    self.embedding_function,
                                                    metadata={
                                                        "description": description,
                                                        "created": str(datetime.now())
                                                    })

    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection from the database.
        """
        self.client.delete_collection(name=collection_name)

    def add_documents(self,
                      collection_name: str,
                      ids: list,
                      documents: list,
                      metadatas: list = None
                      ) -> None:
        """
        Add documents to a collection.
        """
        collection = self.get_collection(collection_name)
        collection.add(ids=ids,
                       documents=documents,
                       metadatas=metadatas,
                       )

    def get_all_documents(self, collection_name: str) -> list:
        """
        Get all documents from a collection.
        """
        collection = self.get_collection(collection_name)
        return collection.get_all_documents()
