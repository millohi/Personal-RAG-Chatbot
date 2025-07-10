import os

from langchain_core.vectorstores import VectorStoreRetriever
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_chroma import Chroma

from typing import Iterator

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.runnables.utils import Output
from ragbot.core import build_chain, ClassicRetriever as Retriever


def load_and_split_markdown(docs_paths: str | list[str]):
    documents = []
    if isinstance(docs_paths, str):
        docs_paths = [docs_paths,]
    for docs_path in docs_paths:
        for path in os.listdir(docs_path):
            if path.endswith(".md"):
                with open(os.path.join(docs_path, path), "r", encoding="utf-8") as f:
                    documents.append(f.read())

    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "Dokument"),
        ("##", "Überschrift"),
        ("###", "Thema"),
    ])

    split_docs = []
    for doc in documents:
        structured_docs = splitter.split_text(doc)
        for chunk in structured_docs:
            metadata_string = " -> ".join(chunk.metadata.values())
            chunk.page_content = metadata_string + "\n" + chunk.page_content
            split_docs.append(chunk)

    return split_docs


class E5QueryWrapperRetriever(VectorStoreRetriever):
    def get_relevant_documents(self, query, **kwargs):
        return super().get_relevant_documents(f"query: {query}")


def _load_or_create_vectorstore(documents, embedding_function, db_dir):
    return Chroma.from_documents(documents, embedding_function, persist_directory=db_dir, collection_name="bewerbung",
                                 collection_metadata={"hnsw:space": "cosine"})


class RAGBot:
    """
    RAGBot is a class that implements a Retrieval-Augmented Generation (RAG) system.
    """
    stream_config = {"configurable": {"session_id": "any"}}

    def __init__(self,
                 # Basic RAG settings
                 docs_path: str | list[str] = "./docs", # path to directory of knowledge-files or list of paths to directories
                 db_dir="./../database"):
        """
        Initializes the RAGBot with the given parameters.
        """
        self.embedding_function = HuggingFaceEmbeddings(model_name="mixedbread-ai/deepset-mxbai-embed-de-large-v1")
        # self.embedding_function = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self.documents = load_and_split_markdown(docs_path)
        self.vectorstore = _load_or_create_vectorstore(self.documents, self.embedding_function, db_dir)
        self.retriever = Retriever(k=3, vectordb=self.vectorstore)
        self.llm = self._llm = ChatOpenAI(
            streaming=True,
            temperature=1,
            model="gpt-4o-mini")

        self._chain = build_chain(self.llm, self.retriever)

    def call_chat(self, query: str, salutation: str, user_name: str, first_time_message:bool=False) -> str:
        """Calls a chatmessage from LLM"""
        if user_name:
            user_name = f"Der Name vom Fragesteller lautet: {user_name}"
        if first_time_message:
            greetings = "Begrüße den Fragensteller und formuliere dann die Antwort."
        else:
            greetings = "Begrüße den Fragesteller nicht, sondern schreibe direkt die Antwort."
        input_message = {"question": query, "salutation": salutation, "user_name": user_name, "greetings": greetings}
        return self._chain.invoke(input_message, RAGBot.stream_config).content

    def stream_chat(self, query: str, salutation: str, user_name: str, first_time_message:bool=False) -> Iterator[Output]:
        """Streams a chatmessage from an LLM"""
        if user_name:
            user_name = f"Der Name vom Fragesteller lautet: {user_name}"
        if first_time_message:
            greetings = "Begrüße den Fragensteller und formuliere dann die Antwort."
        else:
            greetings = "Begrüße den Fragesteller nicht, sondern schreibe direkt die Antwort."
        input_message = {"question": query, "salutation": salutation, "user_name": user_name, "greetings": greetings}
        return self._chain.stream(input_message, RAGBot.stream_config)

    def get_relevant_documents(self, query: str) -> list[dict]:
        result = []
        relevant_docs = self.retriever._get_relevant_documents(query=query, run_manager=None)
        for doc in relevant_docs:
            result.append({'id': doc.id, 'text': doc.page_content, 'metadata': doc.metadata})
        return result
