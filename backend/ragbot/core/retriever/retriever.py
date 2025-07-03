from typing import List
from langchain_chroma import Chroma
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document

class ClassicRetriever(BaseRetriever):
    """
    This class implements a retriever that retrieves documents from a vector database.
    """
    k: int
    vectordb: Chroma

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:

        relevant_documents = self.vectordb.similarity_search(query=query, k=self.k)
        return relevant_documents
