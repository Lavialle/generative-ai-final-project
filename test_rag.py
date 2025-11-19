"""
Script de test pour vérifier le bon fonctionnement du système RAG

Usage:
    python test_rag.py
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_1_imports():
    """Test 1: Vérifier que tous les imports fonctionnent"""
    print("\n🧪 Test 1: Imports...")
    try:
        from rag import initialize_components, train_rag_with_pdfs, rag_agent_with_sources
        from utils import initialize_component
        from config import OPENAI_API_KEY, SERP_API_KEY
        print("✅ Tous les imports OK")
        return True
    except Exception as e:
        print(f"❌ Erreur d'import : {e}")
        return False

def test_2_api_keys():
    """Test 2: Vérifier que les clés API sont configurées"""
    print("\n🧪 Test 2: Clés API...")
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        serp_key = os.getenv("SERP_API_KEY")
        
        if not openai_key:
            print("❌ OPENAI_API_KEY non trouvée")
            return False
        if not serp_key:
            print("❌ SERP_API_KEY non trouvée")
            return False
        
        print(f"✅ OPENAI_API_KEY: {openai_key[:15]}...")
        print(f"✅ SERP_API_KEY: {serp_key[:15]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def test_3_initialize():
    """Test 3: Initialiser les composants"""
    print("\n🧪 Test 3: Initialisation des composants...")
    try:
        from rag import initialize_components
        result = initialize_components()
        print(f"✅ {result}")
        return True
    except Exception as e:
        print(f"❌ Erreur d'initialisation : {e}")
        return False

def test_4_check_pdfs():
    """Test 4: Vérifier la présence de PDFs à indexer"""
    print("\n🧪 Test 4: Vérification des PDFs...")
    try:
        from pathlib import Path
        pdf_folder = Path("data")
        
        if not pdf_folder.exists():
            print("⚠️ Le dossier 'data/' n'existe pas. Création...")
            pdf_folder.mkdir()
        
        pdf_files = list(pdf_folder.glob("*.pdf"))
        
        if not pdf_files:
            print("⚠️ Aucun fichier PDF trouvé dans 'data/'")
            print("💡 Ajoutez des PDFs dans le dossier 'data/' pour les indexer")
            return True  # Ce n'est pas une erreur bloquante
        
        print(f"✅ {len(pdf_files)} PDF(s) trouvé(s) :")
        for pdf in pdf_files:
            print(f"   - {pdf.name}")
        return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def test_5_qdrant_path():
    """Test 5: Vérifier le chemin de Qdrant"""
    print("\n🧪 Test 5: Vérification du dossier Qdrant...")
    try:
        from pathlib import Path
        qdrant_path = Path("data/qdrant_db")
        
        if qdrant_path.exists():
            print(f"✅ Base de données Qdrant existante trouvée dans {qdrant_path}")
            # Compter les fichiers
            files = list(qdrant_path.rglob("*"))
            print(f"   → {len(files)} fichier(s) dans la base")
        else:
            print(f"ℹ️ Aucune base Qdrant existante (sera créée au premier lancement)")
        return True
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return False

def test_6_simple_query():
    """Test 6: Tester une requête simple (si des documents sont indexés)"""
    print("\n🧪 Test 6: Test de requête (optionnel)...")
    try:
        from rag import rag_agent_with_sources, vectorstore
        from pathlib import Path
        
        # Vérifier si la base existe
        qdrant_path = Path("data/qdrant_db")
        if not qdrant_path.exists():
            print("ℹ️ Aucune base indexée. Sautez ce test (normal au premier lancement)")
            return True
        
        # Tester une requête simple
        query = "Quel est le sujet principal des documents ?"
        print(f"📝 Question test : '{query}'")
        
        response = rag_agent_with_sources(query)
        
        if "⚠️" in response:
            print(f"⚠️ {response}")
            return True  # Pas d'erreur, juste pas de documents
        
        print(f"✅ Réponse générée ({len(response)} caractères)")
        print(f"📄 Aperçu : {response[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Erreur de requête : {e}")
        return False

def main():
    """Exécuter tous les tests"""
    print("="*60)
    print("🧪 TESTS DU SYSTÈME RAG")
    print("="*60)
    
    tests = [
        test_1_imports,
        test_2_api_keys,
        test_3_initialize,
        test_4_check_pdfs,
        test_5_qdrant_path,
        test_6_simple_query,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"💥 Exception non gérée : {e}")
            results.append(False)
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Tests réussis : {passed}/{total}")
    print(f"❌ Tests échoués : {total - passed}/{total}")
    
    if all(results):
        print("\n🎉 Tous les tests sont passés ! Le système est prêt.")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    print("\n💡 Prochaines étapes :")
    print("   1. Ajoutez des PDFs dans le dossier 'data/'")
    print("   2. Lancez l'app : streamlit run app.py")
    print("   3. Cliquez sur 'Initialiser les composants'")
    print("   4. Cliquez sur 'Indexer les PDFs'")
    print("   5. Posez vos questions !")
    print("="*60)

if __name__ == "__main__":
    main()
