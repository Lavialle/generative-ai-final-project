import streamlit as st
from pipeline import pipeline

st.title("Chatbot pour les propositions de loi")

# Entrée utilisateur
question = st.text_input("Posez votre question :")

# Chemin vers les index FAISS
index_path = "indexes/PL_3912"  # Exemple, à adapter dynamiquement

if st.button("Envoyer"):
    if question:
        with st.spinner("Analyse en cours..."):
            response = pipeline(question, index_path)
        st.success("Réponse générée :")
        st.write(response)
    else:
        st.error("Veuillez entrer une question.")