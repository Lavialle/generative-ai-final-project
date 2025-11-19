import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from utils import initialize_component

# Global variables
embeddings = None
vectorstore = None
llm = None
collection_name = "rag_documents"
# Chemin pour la persistance de Qdrant sur disque
QDRANT_PATH = "./data/qdrant_db"

def initialize_components():
    """
    Initialise les composants : embeddings, LLM, et Qdrant.
    
    Utilise Qdrant en mode PERSISTANT (sauvegarde automatique sur disque).
    Plus besoin de save_index() manuel !
    """
    global embeddings, llm, vectorstore

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables!")

    # 1. Créer les embeddings OpenAI
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # 2. Créer le LLM
    llm = initialize_component("LLM", {"model": "gpt-4", "temperature": 0})

    # 3. Créer le client Qdrant en mode PERSISTANT (sur disque)
    os.makedirs(QDRANT_PATH, exist_ok=True)
    client = QdrantClient(path=QDRANT_PATH)  # Sauvegarde automatique !
    
    # 4. Créer la collection si elle n'existe pas
    try:
        client.get_collection(collection_name)
        print(f"✅ Collection '{collection_name}' existante chargée")
    except Exception:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # Dimension de text-embedding-3-small
                distance=Distance.COSINE
            )
        )
        print(f"✅ Nouvelle collection '{collection_name}' créée")

    # 5. Créer le vectorstore LangChain
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
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
    """
    Effectue une recherche RAG simple et génère une réponse.
    
    NOTE: Cette fonction est simplifiée. Utilisez rag_agent_with_sources() 
    pour des réponses plus détaillées avec citations.
    
    Args:
        query: Question de l'utilisateur
        
    Returns:
        str: Réponse générée
    """
    global vectorstore, llm

    if vectorstore is None or llm is None:
        return "⚠️ Components not initialized!"

    # 1. Récupérer les documents pertinents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)
    
    # 2. Créer le contexte
    context = "\n".join([doc.page_content for doc in docs])

    # 3. Appeler le LLM avec LangChain (pas de format dict)
    from langchain_core.messages import SystemMessage, HumanMessage
    messages = [
        SystemMessage(content="Use the context below to answer the question."),
        HumanMessage(content=f"Context: {context}\n\nQuestion: {query}")
    ]
    response = llm.invoke(messages)
    return response.content

def rag_agent_with_sources(query: str):
    """
    Effectue une recherche RAG avec citations détaillées des sources.
    
    ÉTAPES :
    1. Recherche les documents pertinents dans Qdrant
    2. Organise les documents par source
    3. Génère une réponse avec le LLM
    4. Ajoute les citations de sources
    
    Args:
        query: Question de l'utilisateur
        
    Returns:
        str: Réponse avec citations des sources
    """
    global vectorstore, llm

    if vectorstore is None or llm is None:
        return "⚠️ Components not initialized!"

    # 1. Récupérer les documents pertinents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)

    if not docs:
        return "⚠️ No relevant documents found. Please index some documents first."

    # 2. Organiser les documents par source
    sources_dict = {}
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        if source not in sources_dict:
            sources_dict[source] = []
        sources_dict[source].append(doc)

    # 3. Créer le contexte avec attribution des sources
    context_parts = []
    for source, source_docs in sources_dict.items():
        for idx, doc in enumerate(source_docs, 1):
            context_parts.append(
                f"[Document: {source} | Chunk {idx}]\n{doc.page_content[:300]}"
            )

    context = "\n\n---\n\n".join(context_parts)

    # 4. Appeler le LLM avec LangChain
    from langchain_core.messages import SystemMessage, HumanMessage
    
    system_prompt = """Tu es un assistant qui répond aux questions en te basant sur les documents fournis.

INSTRUCTIONS IMPORTANTES :
1. Synthétise les informations de TOUS les documents pertinents
2. Cite toujours le nom et la référence de la loi source si présente
3. Si la réponse n'est pas dans le contexte, dis-le clairement
4. Sois clair et structuré dans ta réponse"""

    user_prompt = f"""Contexte des documents indexés :

{context}

Question : {query}

Fournis une réponse complète en citant les documents sources."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    # 5. Générer la réponse
    response = llm.invoke(messages)
    answer = response.content

    # 6. Ajouter les détails des sources
    unique_sources = list(sources_dict.keys())
    source_count = len(unique_sources)
    chunk_count = len(docs)

    sources_section = f"\n\n{'='*60}\n📚 **Sources Utilisées** ({source_count} document(s), {chunk_count} chunk(s))\n{'='*60}\n\n"

    for source, source_docs in sources_dict.items():
        sources_section += f"📄 **{source}** ({len(source_docs)} chunk(s))\n"
        for idx, doc in enumerate(source_docs[:3], 1):
            preview = doc.page_content[:150].replace("\n", " ").strip()
            if len(doc.page_content) > 150:
                preview += "..."
            sources_section += f"   • Chunk {idx}: _{preview}_\n"
        if len(source_docs) > 3:
            sources_section += f"   • ... et {len(source_docs) - 3} chunk(s) de plus\n"
        sources_section += "\n"

    return f"{answer}{sources_section}"

def rag_agent_with_metadata(query: str):
    """
    Reformule une question et génère des métadonnées enrichies, y compris un titre basé sur 'Proposition de loi'.

    Args:
        query (str): Question utilisateur.

    Returns:
        dict: Contexte reformulé et métadonnées enrichies.
    """
    global vectorstore, llm

    if vectorstore is None or llm is None:
        return {"error": "⚠️ Components not initialized!"}

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)

    if not docs:
        return {"error": "⚠️ No relevant documents found. Please index some documents first."}

    # Générer un titre basé sur le contenu des documents
    title = "Proposition de loi : " + (docs[0].metadata.get("title") or "Titre inconnu")

    # Créer un contexte à partir des documents
    context = "\n".join([doc.page_content for doc in docs])

    return {
        "title": title,
        "context": context,
        "documents": docs
    }

def train_rag_with_pdfs(pdf_folder: str):
    """
    Entraîner le RAG avec les fichiers PDF d'un dossier donné.

    Args:
        pdf_folder (str): Chemin vers le dossier contenant les fichiers PDF.

    Returns:
        str: Résultat de l'indexation.
    """
    global vectorstore

    if vectorstore is None:
        return "⚠️ Components not initialized!"

    from pathlib import Path

    pdf_files = list(Path(pdf_folder).glob("*.pdf"))
    if not pdf_files:
        return "⚠️ Aucun fichier PDF trouvé dans le dossier spécifié."

    all_documents = []
    for pdf_file in pdf_files:
        docs = load_document(str(pdf_file))
        for doc in docs:
            doc.metadata["source"] = pdf_file.name
        all_documents.extend(docs)

    # Découper les documents en chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(all_documents)

    # Ajouter les chunks au magasin vectoriel
    vectorstore.add_documents(chunks)
    return f"✅ Indexation terminée : {len(chunks)} chunks ajoutés à partir de {len(pdf_files)} fichiers PDF."

def save_index(index_path: str = None):
    """
    FONCTION OBSOLÈTE - Plus nécessaire !
    
    Avec Qdrant en mode persistant (path=QDRANT_PATH), 
    l'index est AUTOMATIQUEMENT sauvegardé sur disque.
    
    Cette fonction ne fait rien mais reste pour la compatibilité.
    """
    global vectorstore
    if vectorstore is None:
        return "⚠️ Vectorstore not initialized!"
    
    # Qdrant sauvegarde automatiquement, rien à faire !
    return f"✅ Index déjà sauvegardé automatiquement dans {QDRANT_PATH}"

def load_index(index_path: str = None):
    """
    FONCTION OBSOLÈTE - Plus nécessaire !
    
    Avec Qdrant en mode persistant, l'index est AUTOMATIQUEMENT chargé
    au démarrage via initialize_components().
    
    Cette fonction ne fait rien mais reste pour la compatibilité.
    """
    return f"✅ Index déjà chargé automatiquement depuis {QDRANT_PATH}"

def clear_index() -> str:
    """
    Réinitialise complètement l'index vectoriel.
    
    ATTENTION : Cela supprime TOUS les documents indexés !
    """
    global vectorstore, embeddings

    if vectorstore is None:
        return "⚠️ Vectorstore not initialized!"

    try:
        # 1. Récupérer le client Qdrant
        client = vectorstore.client
        
        # 2. Supprimer la collection existante
        try:
            client.delete_collection(collection_name)
            print(f"🗑️ Collection '{collection_name}' supprimée")
        except Exception as e:
            print(f"⚠️ Erreur lors de la suppression : {e}")

        # 3. Recréer une collection vide
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Nouvelle collection '{collection_name}' créée")

        # 4. Recréer le vectorstore
        vectorstore = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings
        )

        return "✅ Index réinitialisé avec succès !"
    except Exception as e:
        return f"❌ Erreur lors de la réinitialisation : {str(e)}"

