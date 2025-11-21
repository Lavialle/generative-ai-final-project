from typing import TypedDict, List, Dict
from rag import rag_agent_with_sources_conversational

# Définir l'état du chatbot avec mémoire conversationnelle
class ChatbotState(TypedDict):
    user_message: str
    bot_response: str
    chat_history: List[Dict[str, str]]  # Historique de conversation

def interact_with_chatbot(user_message: str, chat_history: List[Dict[str, str]] = None):
    """
    Interagit avec le chatbot RAG conversationnel.
    
    Args:
        user_message: Question de l'utilisateur
        chat_history: Historique des messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        str: Réponse du chatbot avec sources
    """
    if chat_history is None:
        chat_history = []
    
    # Appeler le RAG conversationnel qui gère tout
    response = rag_agent_with_sources_conversational(user_message, chat_history)
    
    return response