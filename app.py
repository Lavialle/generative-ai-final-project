import streamlit as st
from rag import initialize_components, train_rag_with_pdfs, clear_index, rag_agent_with_sources
from utils import initialize_component
import os

st.title("🏛️ LuXas : apporter la lumière sur les décisions de l'Assemblée")

# Sidebar pour la configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Initialiser les composants
    if st.button("🚀 Initialiser les composants", use_container_width=True):
        with st.spinner("Initialisation en cours..."):
            result = initialize_components()
        st.success(result)
    
    st.divider()
    
    # Entraîner le RAG avec les PDF
    st.subheader("📚 Indexation des documents")
    if st.button("📥 Indexer les PDFs du dossier data/", use_container_width=True):
        with st.spinner("Indexation des fichiers PDF en cours..."):
            result = train_rag_with_pdfs("data/")
        st.success(result)
    
    st.info("💡 Les documents sont automatiquement sauvegardés dans `data/qdrant_db/`")
    
    st.divider()
    
    # Réinitialiser l'index
    st.subheader("🗑️ Réinitialisation")
    if st.button("🔄 Vider l'index", use_container_width=True, type="secondary"):
        if st.checkbox("⚠️ Confirmer la suppression"):
            with st.spinner("Réinitialisation en cours..."):
                result = clear_index()
            st.warning(result)

# Zone principale
st.markdown("""
### 💬 Posez vos questions sur les propositions de loi

1. **Initialisez** les composants (bouton dans la barre latérale)
2. **Indexez** vos PDF de propositions de loi
3. **Posez** vos questions ci-dessous
""")

# Entrée utilisateur
question = st.text_input("❓ Votre question :", placeholder="Ex: Quels sont les objectifs de cette proposition de loi ?")

if st.button("🔍 Envoyer", type="primary"):
    if question:
        with st.spinner("🤔 Analyse en cours..."):
            try:
                # Utiliser directement rag_agent_with_sources au lieu du pipeline complet
                response = rag_agent_with_sources(question)
                st.success("✅ Réponse générée !")
                st.markdown(response)
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
    else:
        st.error("⚠️ Veuillez entrer une question.")