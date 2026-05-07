from langchain_core.chat_history import InMemoryChatMessageHistory
from src.log_config import logger


class MemoryConfig:
    """Gestore della memoria conversazionale dell'agent.

    Mantiene in RAM lo storico dei messaggi (utente + AI) e si occupa di
    troncarlo quando supera la dimensione massima consentita, in modo da
    non far crescere indefinitamente il contesto inviato al modello.
    """

    def __init__(self):
        # Storico messaggi mantenuto in memoria (non persistente su disco)
        self.history = InMemoryChatMessageHistory()
        # Numero massimo di messaggi da conservare nello storico
        self.max_message = 10
        logger.info("MemoryConfig inizializzato")

    def add_user_message(self, message: str):
        """Aggiunge un messaggio dell'utente allo storico."""
        logger.info(f"Aggiunta messaggio utente: {message}")
        self.history.add_user_message(message)

    def add_ai_message(self, message: str):
        """Aggiunge un messaggio prodotto dall'AI allo storico."""
        logger.info(f"Aggiunta messaggio AI: {message}")
        self.history.add_ai_message(message)

    def _trim_history(self):
        """Rimuove il messaggio più vecchio se si supera la soglia massima.

        Strategia FIFO: si scarta sempre il primo elemento (il più datato)
        per mantenere il contesto recente più rilevante.
        """
        logger.info(f"Rimozione messaggi superflui")
        if len(self.history.messages) > self.max_message:
            self.history.messages.pop(0)

    def get_messages(self):
        """Restituisce lo storico, eseguendo prima il trimming se necessario."""
        self._trim_history()
        return self.history.messages
