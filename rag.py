import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI
from qdrant_client.models import Distance, VectorParams
from pathlib import Path
from config import OPENAI_API_KEY

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
    
    Utilise Qdrant en mode PERSISTANT
    """
    global embeddings, llm, vectorstore

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY not found in environment variables!")

    # 1. Créer les embeddings OpenAI
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=OPENAI_API_KEY)
    
    # 2. Créer le LLM
    llm = ChatOpenAI(model="gpt-4", temperature=0.1, openai_api_key=OPENAI_API_KEY)

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

def rag_agent_with_sources_conversational(query: str, chat_history: list = None):
    """
    Agent RAG conversationnel avec mémoire de conversation.
    
    Gère les questions de suivi en tenant compte de l'historique.
    
    Args:
        query: Question actuelle de l'utilisateur
        chat_history: Liste des messages précédents [{"role": "user/assistant", "content": "..."}]
        
    Returns:
        str: Réponse avec sources
    """
    global vectorstore, llm

    if vectorstore is None or llm is None:
        return "⚠️ Components not initialized!"

    if chat_history is None:
        chat_history = []

    # 1. Reformuler la question en tenant compte du contexte conversationnel
    if chat_history:
        # Construire le contexte conversationnel
        conversation_context = "\n".join([
            f"{'Utilisateur' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in chat_history[-6:]  # Garder seulement les 6 derniers messages
        ])
        
        reformulation_prompt = f"""Contexte de conversation précédente :
{conversation_context}

Question actuelle : {query}

Si la question actuelle fait référence à un élément de la conversation précédente (ex: "Et pour les enfants ?", "Peux-tu préciser ?", "Qu'en est-il de...", etc.), 
reformule-la en une question autonome complète qui inclut le contexte nécessaire.

Si la question est déjà autonome, retourne-la telle quelle.

Retourne UNIQUEMENT la question reformulée, sans explication."""

        reformulation_messages = [
            SystemMessage(content="Tu es un assistant qui reformule les questions pour les rendre autonomes."),
            HumanMessage(content=reformulation_prompt)
        ]
        
        reformulated = llm.invoke(reformulation_messages)
        search_query = reformulated.content.strip()
    else:
        search_query = query

    # 2. Recherche vectorielle avec la question (reformulée ou originale)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    docs = retriever.invoke(search_query)

    if not docs:
        return "⚠️ Aucun document pertinent trouvé. Veuillez d'abord indexer des documents."

    # 3. Organiser les documents par source
    sources_dict = {}
    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        if source not in sources_dict:
            sources_dict[source] = []
        sources_dict[source].append(doc)

    # 4. Créer le contexte documentaire
    context_parts = []
    for source, source_docs in sources_dict.items():
        for idx, doc in enumerate(source_docs, 1):
            context_parts.append(
                f"[Document: {source} | Chunk {idx}]\n{doc.page_content[:500]}"
            )

    doc_context = "\n\n---\n\n".join(context_parts)

    # 5. Construire le prompt avec historique conversationnel
    system_prompt = """Tu es LuXas, un assistant juridique pédagogue spécialisé dans les propositions de loi de l'Assemblée Nationale française.

INSTRUCTIONS CRITIQUES - ANTI-HALLUCINATION :
1. **Tu ne réponds QUE si l'information est dans les documents fournis**
2. Si l'info n'est pas dans les documents, réponds : "Je n'ai pas trouvé cette information dans les documents indexés."
3. **JAMAIS d'invention** : ne crée pas de noms de loi, dates, ou articles qui ne sont pas dans les documents
4. Cite TOUJOURS les sources exactes (nom du document)
5. Si une question fait référence à la conversation précédente, utilise l'historique pour comprendre le contexte
6. Structure tes réponses clairement et utilise un langage pédagogique
7. Si tu utilises des termes juridiques complexes, propose une définition simple avec exemple

RÈGLE D'OR : En cas de doute, dis que tu n'as pas l'information plutôt que d'inventer."""

    # Construire l'historique conversationnel pour le contexte
    conversation_context = ""
    if chat_history:
        conversation_context = "Historique de conversation :\n"
        for msg in chat_history[-4:]:  # Garder les 4 derniers échanges
            role = "Utilisateur" if msg['role'] == 'user' else "Assistant"
            conversation_context += f"{role}: {msg['content'][:200]}...\n"
        conversation_context += "\n"

    user_prompt = f"""{conversation_context}Documents disponibles :

{doc_context}

Question actuelle : {query}

Réponds à la question en te basant UNIQUEMENT sur les documents fournis. Cite tes sources."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    # 6. Générer la réponse
    response = llm.invoke(messages)
    answer = response.content

    # 7. Ajouter les sources
    unique_sources = list(sources_dict.keys())
    source_count = len(unique_sources)
    chunk_count = len(docs)

    sources_section = f"\n\n{'='*60}\n📚 **Sources Consultées** ({source_count} document(s), {chunk_count} chunk(s))\n{'='*60}\n\n"

    for source, source_docs in sources_dict.items():
        sources_section += f"📄 **{source}** ({len(source_docs)} chunk(s))\n"
        for idx, doc in enumerate(source_docs[:2], 1):
            preview = doc.page_content[:120].replace("\n", " ").strip()
            if len(doc.page_content) > 120:
                preview += "..."
            sources_section += f"   • Extrait {idx}: _{preview}_\n"
        if len(source_docs) > 2:
            sources_section += f"   • ... et {len(source_docs) - 2} autre(s) extrait(s)\n"
        sources_section += "\n"

    return f"{answer}{sources_section}"


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

# initialize_components()
# train_rag_with_pdfs("data/")
