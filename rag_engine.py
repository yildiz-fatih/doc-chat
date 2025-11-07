import os
from typing import List, Dict, Tuple
from pydantic import SecretStr
import lancedb
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from doc_utils import load_and_split_document


class RAGEngine:
    def __init__(self, openai_api_key: str, db_path: str = "./db"):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", api_key=SecretStr(openai_api_key)
        )
        self.chat_model = ChatOpenAI(
            model="gpt-4o-mini", api_key=SecretStr(openai_api_key)
        )
        # Initialize database and state
        self.db = lancedb.connect(db_path)
        self.table_name = "documents"
        self.chat_history: List[BaseMessage] = []
        self.loaded_files: set = set()

        # Initialize table if it doesn't exist
        self._initialize_table()

    def _initialize_table(self):
        """Initialize or get the documents table."""
        try:
            self.table = self.db.open_table(self.table_name)
        except Exception:
            # Table doesn't exist, will be created on first add
            self.table = None

    def _get_embedding(self, text: str) -> List[float]:
        return self.embeddings.embed_query(text)

    def add_document(self, file_path: str) -> bool:
        # Load and split document
        chunks = load_and_split_document(file_path)
        if not chunks:
            raise ValueError("No content could be extracted from the document")

        # Create embeddings
        texts_to_embed = []
        for chunk in chunks:
            texts_to_embed.append(chunk["text"])

        embeddings_list = self.embeddings.embed_documents(texts_to_embed)

        # Store in LanceDB
        data = []

        filename = os.path.basename(file_path)

        for i in range(len(chunks)):
            entry = {
                "text": chunks[i]["text"],
                "vector": embeddings_list[i],
                "source": filename,
                "chunk_index": chunks[i]["metadata"]["chunk_index"],
            }

            data.append(entry)

        if self.table is None:
            self.table = self.db.create_table(self.table_name, data)
        else:
            self.table.add(data)

        # Track loaded file
        self.loaded_files.add(filename)

        return True

    def remove_document(self, filename: str) -> bool:
        if not self.table:
            raise ValueError("No documents loaded")

        if filename not in self.loaded_files:
            raise ValueError(f"Document '{filename}' not found in loaded files")

        # Delete all chunks from this document
        self.table.delete(f"source = '{filename}'")
        self.loaded_files.remove(filename)

        return True

    def list_files(self) -> List[str]:
        return sorted(list(self.loaded_files))

    def reset_all(self) -> bool:
        if self.table:
            self.db.drop_table(self.table_name)
            self.table = None

        self.loaded_files.clear()
        self.chat_history.clear()

        return True

    def chat(self, user_prompt: str, top_k: int = 3) -> Tuple[str, List[Dict]]:
        if not self.loaded_files or not self.table:
            return (
                "⚠️  No documents loaded yet. Use /add <path> to load a document first",
                [],
            )

        # Get prompt's embedding
        prompt_embedding = self._get_embedding(user_prompt)

        # Search for relevant chunks
        results = self.table.search(prompt_embedding).limit(top_k).to_list()

        if not results:
            context = "No relevant information found in the documents."
            sources = []
        else:
            # Build context from results
            context_parts = []
            sources = []

            for idx, result in enumerate(results, 1):
                context_parts.append(
                    f"[Source {idx} - {result['source']}, chunk {result['chunk_index']}]:\n{result['text']}"
                )
                sources.append(
                    {
                        "source": result["source"],
                        "chunk_index": result["chunk_index"],
                    }
                )

            context = "\n\n".join(context_parts)

        # Build the messages array (system prompt + chat history + current user prompt)
        messages: list[BaseMessage] = []

        system_prompt = """You are a helpful assistant that answers questions based on the provided document context. 
Use the context to answer questions accurately. If the context doesn't contain relevant information, say so.
Always cite which source number you're referencing when making claims."""
        messages.append(SystemMessage(content=system_prompt))

        messages.extend(self.chat_history)

        user_message = f"""
        Context from documents: {context}
        
        Question: {user_prompt}
        """
        messages.append(HumanMessage(content=user_message))

        # Get response from chat model
        response = self.chat_model.invoke(messages)
        response_text = str(response.content)

        # Update chat history
        self.chat_history.append(HumanMessage(content=user_prompt))
        self.chat_history.append(AIMessage(content=response_text))

        return response_text, sources
