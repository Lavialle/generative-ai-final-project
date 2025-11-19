import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Global variables
embeddings = None
vectorstore = None
llm = None
collection_name = "rag_documents"

def initialize_components():
    """Initialize embeddings, LLM, and Qdrant connection"""
    global embeddings, llm, vectorstore

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables!")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    client = QdrantClient(location=":memory:")
    try:
        client.get_collection(collection_name)
    except Exception:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )

    vectorstore = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings
    )
    return "✅ Components initialized successfully!"

def load_document(file_path: str) -> List[Document]:
    """Load a document based on its file extension"""
    file_ext = Path(file_path).suffix.lower()
    if file_ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        return loader.load()
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

def index_documents(files: List[str]) -> str:
    """Index uploaded documents to Qdrant"""
    global vectorstore

    if vectorstore is None:
        return "⚠️ Components not initialized!"

    all_documents = []
    for file_path in files:
        docs = load_document(file_path)
        for doc in docs:
            doc.metadata["source"] = Path(file_path).name
        all_documents.extend(docs)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(all_documents)
    vectorstore.add_documents(chunks)
    return f"✅ Indexed {len(chunks)} chunks from {len(files)} files."

def rag_agent(query: str):
    """Perform RAG-based retrieval and answer generation"""
    global vectorstore, llm

    if vectorstore is None or llm is None:
        return "⚠️ Components not initialized!"

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(query)
    context = "\n".join([doc.page_content for doc in docs])

    messages = [
        {"role": "system", "content": "Use the context below to answer the question."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
    ]
    response = llm(messages)
    return response["choices"][0]["message"]["content"]

def rag_agent_with_sources(query: str):
    """
    Perform RAG-based retrieval and answer generation with source citation.

    Args:
        query (str): User's question.

    Returns:
        str: Generated answer with source citations.
    """
    global vectorstore, llm

    if vectorstore is None or llm is None:
        return "⚠️ Components not initialized!"

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(query)

    if not docs:
        return "⚠️ No relevant documents found. Please index some documents first."

    # Group documents by source for better organization
    sources_dict = {}
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        if source not in sources_dict:
            sources_dict[source] = []
        sources_dict[source].append(doc)

    # Create context with clear source attribution
    context_parts = []
    for source, source_docs in sources_dict.items():
        for idx, doc in enumerate(source_docs, 1):
            chunk_preview = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            context_parts.append(
                f"[Document: {source} | Chunk {idx}]\n{chunk_preview}"
            )

    context = "\n\n---\n\n".join(context_parts)

    # Enhanced prompt with better instructions for source citation
    messages = [
        {"role": "system", "content": """
        You are a helpful assistant that answers questions based on the provided context from multiple documents.

        IMPORTANT INSTRUCTIONS:
        1. Synthesize information from ALL relevant documents provided in the context.
        2. If information appears in multiple documents, mention all relevant sources.
        3. Always cite the specific document name when referencing information.
        4. If the answer cannot be found in the context, explicitly state this.
        5. Be comprehensive and draw connections between information from different documents when relevant.
        6. Format your answer clearly with proper structure.
        """},
        {"role": "user", "content": f"""
        Context from indexed documents:

        {context}

        Question: {query}

        Provide a comprehensive answer based on the context above. Cite specific documents when referencing information.
        """}
    ]

    # Generate answer
    response = llm(messages)
    answer = response["choices"][0]["message"]["content"]

    # Create detailed source information
    unique_sources = list(sources_dict.keys())
    source_count = len(unique_sources)
    chunk_count = len(docs)

    # Build source details with chunk previews
    sources_section = f"\n\n{'='*60}\n📚 **Sources Used** ({source_count} document(s), {chunk_count} chunk(s))\n{'='*60}\n\n"

    for source, source_docs in sources_dict.items():
        sources_section += f"📄 **{source}** ({len(source_docs)} chunk(s))\n"
        for idx, doc in enumerate(source_docs[:3], 1):
            preview = doc.page_content[:150].replace("\n", " ").strip()
            if len(doc.page_content) > 150:
                preview += "..."
            sources_section += f"   • Chunk {idx}: _{preview}_\n"
        if len(source_docs) > 3:
            sources_section += f"   • ... and {len(source_docs) - 3} more chunk(s)\n"
        sources_section += "\n"

    return f"{answer}{sources_section}"
