from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from rag import rag_agent_with_sources
from summarizer_agent import summarize_law_text
from tone_analysis_agent import analyze_tone_of_voice
from config import OPENAI_API_KEY, SERP_API_KEY

# Tool : Reformuler la question et générer des métadonnées
@tool("reformulate_and_metadata_tool", description="Reformule une question et génère des métadonnées enrichies, y compris un titre basé sur 'Proposition de loi'.")
def reformulate_and_metadata_tool(query: str):
    response = rag_agent_with_sources(query)
    return response

# Tool : Résumé des textes de loi
@tool("summarize_tool", description="Produit un résumé clair et compréhensible d'un texte de loi.")
def summarize_tool(law_text: str):
    return summarize_law_text(law_text)

# Tool : Analyse du tone of voice
@tool("tone_analysis_tool", description="Analyse le tone of voice des médias à propos d'un texte de loi.")
def tone_analysis_tool(law_title: str):
    return analyze_tone_of_voice(law_title)

# Initialiser le modèle
model = ChatOpenAI(
    model="gpt-5",
    temperature=0.1,
)

# Créer l'agent avec le modèle et les outils
agent = create_agent(model, tools=[reformulate_and_metadata_tool, summarize_tool, tone_analysis_tool])

# Pipeline principale
def pipeline(question: str):
    """
    Orchestration de la question utilisateur avec un agent.

    Args:
        question (str): Question utilisateur.

    Returns:
        dict: Résultats combinés.
    """

    # Étape 1 : Reformuler la question et générer des métadonnées
    metadata_response = agent.run({"query": question})

    # Extraire le titre généré
    law_title = metadata_response.get("title", "Proposition de loi inconnue")

    # Étape 2 : Résumer le texte de loi
    summary = summarize_tool(metadata_response.get("context", ""))

    # Étape 3 : Analyser le tone of voice
    tone_analysis = tone_analysis_tool(law_title)

    return {
        "metadata": metadata_response,
        "summary": summary,
        "tone_analysis": tone_analysis
    }
