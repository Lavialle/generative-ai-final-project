"""
Script pour indexer les PDFs locaux vers Qdrant Cloud.

Permet de migrer votre base locale vers le cloud pour :
- Éviter les problèmes de RAM Docker
- Accès depuis n'importe où
- Performance optimale
"""

import os
from pathlib import Path
from tqdm import tqdm
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config import OPENAI_API_KEY, QDRANT_API_KEY, QDRANT_CLOUD_URL

# Configuration Qdrant Cloud
COLLECTION_NAME = "rag_documents"

# Configuration
PDF_FOLDER = "db_local_pdfs"
MAX_CHUNKS_PER_BATCH = 5000  # Limite par nombre de chunks au lieu de PDFs
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def index_pdfs_to_cloud():
    """
    Indexe tous les PDFs du dossier local vers Qdrant Cloud.
    """
    print("=" * 80)
    print("🚀 INDEXATION VERS QDRANT CLOUD")
    print("=" * 80)
    
    
    # 1. Créer le client Qdrant Cloud
    print(f"\n🌐 Connexion à Qdrant Cloud : {QDRANT_CLOUD_URL}")
    client = QdrantClient(
        url=QDRANT_CLOUD_URL,
        api_key=QDRANT_API_KEY,
    )
    
    # 2. Créer les embeddings
    print("🔧 Initialisation des embeddings OpenAI...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=OPENAI_API_KEY
    )
    
    # 3. Créer ou récupérer la collection
    try:
        client.get_collection(COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' existante trouvée")
    except Exception:
        print(f"📦 Création de la collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE
            )
        )
        print(f"✅ Collection créée")
    
    # 4. Créer le vectorstore
    vectorstore = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )
    
    # 5. Lister les PDFs
    pdf_folder = Path(PDF_FOLDER)
    if not pdf_folder.exists():
        print(f"❌ Le dossier '{PDF_FOLDER}' n'existe pas!")
        return
    
    pdf_files = list(pdf_folder.glob("*.pdf"))
    total_pdfs = len(pdf_files)
    
    if total_pdfs == 0:
        print(f"❌ Aucun PDF trouvé dans '{PDF_FOLDER}'")
        return
    
    print(f"\n📚 {total_pdfs} PDFs à indexer")
    
    # 6. Initialiser le text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # 7. Traiter PDF par PDF, grouper les chunks par batches
    total_chunks_indexed = 0
    failed_files = []
    current_batch_chunks = []
    batch_num = 1
    pdfs_processed = 0
    
    print(f"\n📊 Stratégie : batches de maximum {MAX_CHUNKS_PER_BATCH} chunks")
    
    for pdf_file in tqdm(pdf_files, desc="Indexation", unit="PDF"):
        try:
            # Charger le PDF
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            
            # Ajouter les métadonnées
            for doc in docs:
                doc.metadata["source"] = pdf_file.name
            
            # Découper en chunks
            pdf_chunks = text_splitter.split_documents(docs)
            
            # Ajouter les chunks au batch actuel
            current_batch_chunks.extend(pdf_chunks)
            pdfs_processed += 1
            
            # Si on dépasse la limite, uploader le batch
            if len(current_batch_chunks) >= MAX_CHUNKS_PER_BATCH:
                print(f"\n☁️ Upload batch {batch_num} : {len(current_batch_chunks)} chunks ({pdfs_processed} PDFs)")
                try:
                    vectorstore.add_documents(current_batch_chunks)
                    total_chunks_indexed += len(current_batch_chunks)
                    print(f"✅ Batch {batch_num} indexé avec succès")
                except Exception as e:
                    print(f"❌ Erreur lors de l'indexation du batch {batch_num}: {e}")
                
                # Réinitialiser pour le prochain batch
                current_batch_chunks = []
                batch_num += 1
                pdfs_processed = 0
                
        except Exception as e:
            print(f"\n⚠️ Erreur avec {pdf_file.name}: {e}")
            failed_files.append(str(pdf_file))
    
    # Uploader le dernier batch s'il reste des chunks
    if current_batch_chunks:
        print(f"\n☁️ Upload batch final {batch_num} : {len(current_batch_chunks)} chunks ({pdfs_processed} PDFs)")
        try:
            vectorstore.add_documents(current_batch_chunks)
            total_chunks_indexed += len(current_batch_chunks)
            print(f"✅ Batch {batch_num} indexé avec succès")
        except Exception as e:
            print(f"❌ Erreur lors de l'indexation du batch final {batch_num}: {e}")
    
    total_chunks = total_chunks_indexed
    
    # 8. Résumé final
    print("\n" + "=" * 80)
    print("✅ INDEXATION TERMINÉE")
    print("=" * 80)
    print(f"📄 PDFs traités : {total_pdfs - len(failed_files)}/{total_pdfs}")
    print(f"📦 Chunks indexés : {total_chunks}")
    print(f"☁️ Base vectorielle : Qdrant Cloud")
    print(f"🌐 URL : {QDRANT_CLOUD_URL}")
    
    if failed_files:
        print(f"\n⚠️ {len(failed_files)} fichiers ont échoué :")
        for failed in failed_files[:10]:
            print(f"   - {failed}")
        if len(failed_files) > 10:
            print(f"   ... et {len(failed_files) - 10} autres")
    
    print("\n🎉 Votre système RAG est maintenant dans le cloud !")
    print("=" * 80)

if __name__ == "__main__":
    index_pdfs_to_cloud()
