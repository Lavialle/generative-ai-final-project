from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from serpapi import GoogleSearch
from utils import initialize_component
from config import SERP_API_KEY

from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv




# Initialiser un LLM via la fonction centralisée
llm = initialize_component("LLM", {"model": "gpt-4", "temperature": 0})

def analyze_tone_of_voice(law_title: str):
    """
    Analyser le tone of voice des médias sur un titre de loi.

    Args:
        law_title (str): Titre de la loi.

    Returns:
        str: Analyse du tone of voice des médias.
    """
    params = {
        "api_key": SERP_API_KEY,
        "q": law_title,
        "engine": "google_news",
        "hl": "fr"
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "error" in results:
        return f"Erreur lors de la recherche : {results['error']}"
    # Extraire les titres des articles pour l'analyse
    articles = results.get("articles", [])
    analysis = []
    for article in articles:
        analysis.append(f"Titre : {article['title']}\nSource : {article['source']['name']}\nLien : {article['link']}\n")

    return "\n".join(analysis)

pdf = PdfReader("data/l17b2108_proposition-loi.pdf")
law_text = ""
for page in pdf.pages:
    law_text += page.extract_text()

law_title = pdf.metadata.title
print(law_text)
print(analyze_tone_of_voice(law_title))
