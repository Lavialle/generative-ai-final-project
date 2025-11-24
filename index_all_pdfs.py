"""
Script pour indexer les 3201 PDFs de db_local_pdfs dans Qdrant.

OPTIMISATIONS :
- Traitement par batch pour éviter les timeouts
- Affichage de la progression
- Gestion d'erreurs robuste
- Reprise en cas d'échec
"""

from pathlib import Path
from tqdm import tqdm
from rag import initialize_components, vectorstore
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
PDF_FOLDER = "db_local_pdfs"
BATCH_SIZE = 50  # Traiter 50 PDFs à la fois
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def index_all_pdfs_in_batches():
    """
    Indexe tous les PDFs du dossier db_local_pdfs par batches.
    """
    print("=" * 80)
    print("🚀 INDEXATION MASSIVE DES PDFS")
    print("=" * 80)
    
    # 1. Vérifier l'initialisation
    print("\n📦 Initialisation des composants...")
    initialize_components()
    
    # 2. Lister tous les PDFs
    pdf_folder = Path(PDF_FOLDER)
    if not pdf_folder.exists():
        print(f"❌ Le dossier '{PDF_FOLDER}' n'existe pas!")
        return
    
    pdf_files = list(pdf_folder.glob("*.pdf"))
    total_pdfs = len(pdf_files)
    
    if total_pdfs == 0:
        print(f"❌ Aucun PDF trouvé dans '{PDF_FOLDER}'")
        return
    
    print(f"✅ {total_pdfs} PDFs trouvés")
    
    # 3. Initialiser le text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # 4. Traiter par batches
    total_chunks = 0
    failed_files = []
    
    print(f"\n📚 Indexation par batches de {BATCH_SIZE} PDFs...")
    print(f"⏱️ Temps estimé : ~10-30 minutes")
    print("=" * 80 + "\n")
    
    # Diviser en batches
    for batch_idx in range(0, total_pdfs, BATCH_SIZE):
        batch_files = pdf_files[batch_idx:batch_idx + BATCH_SIZE]
        batch_num = (batch_idx // BATCH_SIZE) + 1
        total_batches = (total_pdfs + BATCH_SIZE - 1) // BATCH_SIZE
        
        print(f"\n🔄 Batch {batch_num}/{total_batches} ({len(batch_files)} PDFs)")
        
        batch_documents = []
        
        # Charger les PDFs du batch
        for pdf_file in tqdm(batch_files, desc="Chargement", unit="PDF"):
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                
                # Ajouter les métadonnées
                for doc in docs:
                    doc.metadata["source"] = pdf_file.name
                    doc.metadata["batch"] = batch_num
                
                batch_documents.extend(docs)
                
            except Exception as e:
                print(f"⚠️ Erreur avec {pdf_file.name}: {e}")
                failed_files.append(str(pdf_file))
        
        # Découper en chunks
        print(f"✂️ Découpage en chunks...")
        chunks = text_splitter.split_documents(batch_documents)
        print(f"   → {len(chunks)} chunks créés")
        
        # Ajouter au vectorstore
        if chunks:
            print(f"💾 Indexation dans Qdrant...")
            try:
                vectorstore.add_documents(chunks)
                total_chunks += len(chunks)
                print(f"✅ Batch {batch_num} indexé : {len(chunks)} chunks")
            except Exception as e:
                print(f"❌ Erreur lors de l'indexation du batch {batch_num}: {e}")
                failed_files.extend([str(f) for f in batch_files])
        
        print(f"📊 Progression totale : {total_chunks} chunks indexés")
    
    # 5. Résumé final
    print("\n" + "=" * 80)
    print("✅ INDEXATION TERMINÉE")
    print("=" * 80)
    print(f"📄 PDFs traités : {total_pdfs - len(failed_files)}/{total_pdfs}")
    print(f"📦 Chunks indexés : {total_chunks}")
    print(f"💾 Base vectorielle : data/qdrant_db/")
    
    if failed_files:
        print(f"\n⚠️ {len(failed_files)} fichiers ont échoué :")
        for failed in failed_files[:10]:
            print(f"   - {failed}")
        if len(failed_files) > 10:
            print(f"   ... et {len(failed_files) - 10} autres")
    
    print("\n🎉 Le système RAG est prêt à répondre aux questions!")
    print("=" * 80)

if __name__ == "__main__":
    index_all_pdfs_in_batches()
