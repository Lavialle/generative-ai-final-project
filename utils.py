from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

def initialize_component(component_name: str, config: dict):
    """
    Initialise un composant avec une configuration donnée.

    Args:
        component_name (str): Le nom du composant à initialiser.
        config (dict): La configuration pour le composant.

    Returns:
        object: Le composant initialisé.
    """
    if component_name == "LLM":
        print(f"Initializing LLM with config: {config}")
        return ChatOpenAI(model=config.get("model", "gpt-4"),
                          temperature=config.get("temperature", 0),
                          openai_api_key=OPENAI_API_KEY)

    print(f"Initializing component: {component_name} with config: {config}")
    # Exemple d'initialisation, à adapter selon vos besoins
    component = {
        "name": component_name,
        "config": config
    }
    return component