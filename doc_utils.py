import os
from typing import List, Dict
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def load_and_split_document(
    file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[Dict]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    file_extension = Path(file_path).suffix.lower()
    if file_extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {file_extension}. ")

    try:
        # Load documents
        if file_extension == ".pdf":
            loader = PyPDFLoader(file_path)
        else:  # .txt or .md
            loader = TextLoader(file_path, encoding="utf-8")

        documents = loader.load()

        if not documents:
            raise ValueError(f"File failed to load: {file_path}")

        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
        )

        chunks = text_splitter.split_documents(documents)

        # Convert to our format of choice (chunk + metadata)
        filename = os.path.basename(file_path)
        chunk_dicts = []

        for index, chunk in enumerate(chunks):
            # Custom metadata
            metadata = {
                "source": filename,
                "chunk_index": index,
                "total_chunks": len(chunks),
            }
            # Add (merge) the original document metadata
            metadata.update(chunk.metadata)

            chunk_dicts.append({"text": chunk.page_content, "metadata": metadata})

        return chunk_dicts

    except Exception as e:
        raise ValueError(f"Error loading document: {str(e)}")
