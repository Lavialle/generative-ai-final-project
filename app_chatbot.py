import streamlit as st
from chatbot import interact_with_chatbot

st.set_page_config(
    page_title="LuXas - Assistant Juridique",
    page_icon="🏛️",
    layout="wide"
)

st.title("🏛️ LuXas : Assistant Juridique pour l'Assemblée Nationale")

# Zone principale
st.markdown("""
### 💬 Posez vos questions sur les propositions de loi
**Conversation intelligente** : Vous pouvez poser des questions de suivi comme "Et pour les enfants ?" ou "Peux-tu préciser ?"
""")

# Initialiser l'historique de conversation (format pour le RAG)
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Afficher l'historique des messages avec un style amélioré
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Champ de saisie utilisateur
if prompt := st.chat_input("Ex: Quelle est la dernière proposition de loi sur la protection des enfants ?"):
    # Ajouter le message utilisateur à l'affichage
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Préparer l'historique pour le RAG (exclure le message actuel)
    chat_history = st.session_state["messages"][:-1]

    # Obtenir la réponse du chatbot avec spinner
    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche dans les documents..."):
            response = interact_with_chatbot(prompt, chat_history)
        st.markdown(response)

    # Ajouter la réponse à l'historique
    st.session_state["messages"].append({"role": "assistant", "content": response})

# Sidebar avec informations et options
with st.sidebar:
    st.header("📊 Informations")
    st.info(f"💬 Messages dans la conversation : {len(st.session_state['messages'])}")
    
    if st.button("🗑️ Réinitialiser la conversation"):
        st.session_state["messages"] = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 Conseils d'utilisation
    - Posez des questions précises sur les propositions de loi
    - Vous pouvez demander des clarifications sur les termes juridiques
    - Les réponses sont basées uniquement sur les documents indexés
    - Vous pouvez poser des questions de suivi dans la conversation
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ Système RAG")
    st.caption("Retrieval-Augmented Generation avec Qdrant + OpenAI")