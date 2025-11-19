from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from serpapi import GoogleSearch

from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()
    print("Environment variables loaded from .env file.")


# Access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")
serpapi_api_key = os.getenv("SERP_API_KEY")

if openai_api_key:
    print("OpenAI API Key loaded successfully!")
else:
    print("OpenAI API Key not found. Please check your .env file.")


if serpapi_api_key:
    print("SerpAPI Key loaded successfully!")
else:
    print("SerpAPI Key not found. Please check your .env file.")


# Initialiser le modèle de langage
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

def analyze_tone_of_voice(law_text, law_title):
    """
    Analyser le tone of voice des médias sur un texte de loi.

    Args:
        law_text (str): Texte brut de la loi.
        law_title (str): Titre de la loi.

    Returns:
        str: Analyse du tone of voice des médias.
    """
    
    params = {
    "api_key": serpapi_api_key,
    "q": law_title,
    "engine": "google_news",
    "hl": "fr",
    "gl": "fr"
    }

    search = GoogleSearch(params)
    search_results = search.get_dict()
    articles = search_results.get("news_results", [])
    # Messages pour l'analyse du tone of voice
    messages = [
        SystemMessage(content="Tu es un assistant chargé d'analyser le tone of voice des médias."),
        HumanMessage(content=f"Voici un texte de loi :\n{law_text}\n\nVoici ce que disent les médias :\n{articles}\n\nAnalyse les réactions de chaque réaction media sous la forme de bullet points.\n\nAnalyse :")
    ]
    prompt = ChatPromptTemplate.from_messages(messages)

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"law_text": law_text, "articles": articles})

pdf = PdfReader("data/l17b2108_proposition-loi.pdf")
law_text = ""
for page in pdf.pages:
    law_text += page.extract_text()

law_title = pdf.metadata.title
print(law_text)
# print(analyze_tone_of_voice(law_text, law_title))
