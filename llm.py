from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Définir l'objet LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

def answer_question(query, context):
    """
    Générer une réponse à une question utilisateur en utilisant un contexte pertinent.

    Args:
        query (str): Question utilisateur.
        context (str): Contexte pertinent extrait des documents.

    Returns:
        str: Réponse générée par le modèle.
    """
    prompt = ChatPromptTemplate.from_template("""
    Tu es un assistant expert en droit parlementaire français.

    Voici la question de l'utilisateur :
    "{query}"

    Voici les extraits pertinents issus des documents :
    {context}

    Rédige une réponse :
    - claire
    - complète
    - fondée uniquement sur les extraits fournis
    - sans inventer de contenu

    Réponse :
    """)

    chain = prompt | llm | StrOutputParser()
    return chain.run({"query": query, "context": context})

