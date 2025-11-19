from langchain.tools import tool
from langchain.agents import create_agent
from langchain.chat_models import ChatOpenAI
from rag import rag_agent_with_sources
from summarizer_agent import summarize_law_text
from tone_analysis_agent import analyze_tone_of_voice

# Tool : Recherche dans Qdrant avec attribution des sources
@tool("search_rag_tool", description="Effectue une recherche dans l'index vectoriel pour trouver des documents pertinents avec attribution des sources.")
def search_tool(query: str):
    response = rag_agent_with_sources(query)
    return response

# Tool : Résumé des textes de loi
@tool("summarize_tool", description="Produit un résumé clair et compréhensible d'un texte de loi.")
def summarize_tool(law_text: str):
    return summarize_law_text(law_text)


# Tool : Analyse du tone of voice
@tool("tone_analysis_tool", description="Analyse le tone of voice des médias à propos d'un texte de loi.")
def tone_analysis_tool(law_text: str):
    return analyze_tone_of_voice(law_text)

# Initialiser le modèle de langage
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Créer l'agent
agent = create_agent(
    tools=[search_tool, summarize_tool, tone_analysis_tool],
    llm=llm,
    agent_type="zero-shot-react-description"
)

# Pipeline principale
def pipeline(question: str):
    """
    Orchestration de la question utilisateur avec un agent.

    Args:
        question (str): Question utilisateur.

    Returns:
        dict: Résultats combinés.
    """
    # Appeler l'agent pour traiter la question
    response = agent.run({"query": question})
    return response
