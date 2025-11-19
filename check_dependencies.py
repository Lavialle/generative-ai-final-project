"""
Script d'installation et de vérification des dépendances

Ce script vérifie que toutes les dépendances nécessaires sont installées
et propose de les installer si nécessaire.
"""

import subprocess
import sys

def check_package(package_name, import_name=None):
    """Vérifie si un package est installé"""
    if import_name is None:
        import_name = package_name.replace("-", "_")
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Installe un package via pip"""
    print(f"📦 Installation de {package_name}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", package_name])
        print(f"✅ {package_name} installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Échec de l'installation de {package_name}")
        return False

def main():
    print("="*60)
    print("🔍 VÉRIFICATION DES DÉPENDANCES")
    print("="*60)
    
    # Liste des packages requis avec leur nom d'import
    required_packages = [
        ("langchain", "langchain"),
        ("langchain-openai", "langchain_openai"),
        ("langchain-community", "langchain_community"),
        ("langchain-qdrant", "langchain_qdrant"),  # ← Important !
        ("qdrant-client", "qdrant_client"),
        ("streamlit", "streamlit"),
        ("python-dotenv", "dotenv"),
        ("PyPDF2", "PyPDF2"),
        ("google-search-results", "serpapi"),
        ("python-docx", "docx"),
        ("python-pptx", "pptx"),
    ]
    
    missing_packages = []
    installed_packages = []
    
    print("\n📋 Vérification des packages...\n")
    
    for package_name, import_name in required_packages:
        if check_package(package_name, import_name):
            print(f"✅ {package_name} - OK")
            installed_packages.append(package_name)
        else:
            print(f"❌ {package_name} - MANQUANT")
            missing_packages.append(package_name)
    
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print(f"✅ Packages installés : {len(installed_packages)}/{len(required_packages)}")
    print(f"❌ Packages manquants : {len(missing_packages)}/{len(required_packages)}")
    
    if missing_packages:
        print("\n⚠️ Packages manquants :")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        
        print("\n💡 Pour installer tous les packages manquants :")
        print("   pip install -U " + " ".join(missing_packages))
        
        response = input("\n❓ Voulez-vous installer les packages manquants maintenant ? (o/n) : ")
        
        if response.lower() in ["o", "y", "oui", "yes"]:
            print("\n📦 Installation des packages manquants...\n")
            success_count = 0
            for pkg in missing_packages:
                if install_package(pkg):
                    success_count += 1
            
            print("\n" + "="*60)
            if success_count == len(missing_packages):
                print("🎉 Tous les packages ont été installés avec succès !")
            else:
                print(f"⚠️ {success_count}/{len(missing_packages)} packages installés")
                print("Certains packages n'ont pas pu être installés.")
        else:
            print("\n⏭️ Installation ignorée")
    else:
        print("\n🎉 Toutes les dépendances sont installées !")
    
    print("\n" + "="*60)
    print("💡 PROCHAINES ÉTAPES")
    print("="*60)
    
    if not missing_packages:
        print("1. Configurez vos clés API dans le fichier .env")
        print("2. Ajoutez vos PDFs dans le dossier data/")
        print("3. Lancez les tests : python test_rag.py")
        print("4. Lancez l'app : streamlit run app.py")
    else:
        print("1. Installez les packages manquants")
        print("2. Relancez ce script pour vérifier")
    
    print("="*60)

if __name__ == "__main__":
    main()
