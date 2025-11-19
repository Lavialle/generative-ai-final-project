from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
# from PyPDF2 import PdfReader
# import os
# from dotenv import load_dotenv

# if os.path.exists(".env"):
#     load_dotenv()
#     print("Environment variables loaded from .env file.")


# # Access the API key
# api_key = os.getenv("OPENAI_API_KEY")

# if api_key:
#     print("API Key loaded successfully!")
# else:
#     print("API Key not found. Please check your .env file.")

llm = ChatOpenAI(model="gpt-4", temperature=0)

def summarize_law_text(law_text):
    """
    Résumer un texte de loi.

    Args:
        law_text (str): Texte brut de la loi.

    Returns:
        str: Résumé intelligible du texte de loi.
    """


    messages = [
        SystemMessage(content="Tu es un assistant juridique spécialisé dans les lois françaises."),
        HumanMessage(content=f"Voici un texte de loi :\n{law_text}\n\nRédige un résumé clair, concis et compréhensible pour un citoyen lambda.\n\nRésumé :")
    ]

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"law_text": law_text})

# law_text = PdfReader("data/l17b2108_proposition-loi.pdf")
# text = ""
# for page in law_text.pages:
#     text += page.extract_text()
# print(summarize_law_text(text))
