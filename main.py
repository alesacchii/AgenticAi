# Importazione delle classi di configurazione del modello e della memoria,
# del logger condiviso e delle utilità per leggere le variabili d'ambiente.
from src.model_config.model import AgentConfig
from src.log_config import logger
import os
from dotenv import load_dotenv
from src.memory_config.memory import MemoryConfig

# Carica le variabili definite nel file .env (es. OPENROUTER_MODEL_NAME, API key)
load_dotenv()

# Inizializza la memoria conversazionale che terrà traccia dello scambio utente/AI
memory_config = MemoryConfig()

# Crea la configurazione dell'agent, specificando il modello (preso da .env)
# e il provider (in questo caso OpenRouter)
agent_config = AgentConfig(model=os.getenv("OPENROUTER_MODEL_NAME"), provider="openrouter:")

# Istanzia concretamente l'agent LangChain a partire dalla configurazione
agent = agent_config.create_agent()

# Loop principale della chat: legge l'input da terminale finché l'utente non esce
while True:
    user_input = input("User: ")

    # Comandi per terminare la conversazione
    if user_input in ["exit", "quit", "esci", "stop"]:
        logger.info("Uscita dal programma")
        break

    # Salva il messaggio dell'utente nella memoria della conversazione
    memory_config.add_user_message(user_input)

    # Invoca l'agent passandogli l'intero storico dei messaggi come contesto
    logger.info("Invio richiesta all'agent")
    response = agent.invoke({"messages": memory_config.get_messages()})
    logger.info(f"Response: {response}")

    # Mostra all'utente solo l'ultimo messaggio prodotto dall'agent
    print("Agent: " + response["messages"][-1].content)

    # Aggiunge la risposta dell'AI alla memoria così da mantenere il contesto
    memory_config.add_ai_message(response["messages"][-1].content)
    logger.info(f"Memory: {memory_config.get_messages()}")
