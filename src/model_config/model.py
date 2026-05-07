from langchain.agents import create_agent
from dotenv import load_dotenv
from src.model_tool.tool import tools
from src.log_config import logger


class AgentConfig:
    """Classe di configurazione e factory per l'agent LangChain.

    Raccoglie in un unico posto i parametri (modello, provider, system prompt,
    tool disponibili) e si occupa di costruire l'agent vero e proprio.
    """

    def __init__(
        self,
        model: str = "gpt-5-nano-2025-08-07",
        system_prompt: str = "You are a helpful assistant.",
        provider: str = "openrouter:",
    ):
        # Nome del modello LLM da utilizzare (es. "gpt-5-nano-2025-08-07")
        self.model = model
        # System prompt che definisce la "personalità" e le istruzioni base dell'agent
        self.system_prompt = system_prompt
        # Timeout massimo (in secondi) di una singola chiamata
        self.timeout = 300
        # Prefisso del provider richiesto da LangChain (es. "openrouter:", "openai:")
        self.provider = provider
        # Lista dei tool che l'agent potrà invocare durante il ragionamento
        self.tools = tools
        logger.info(f"AgentConfig inizializzato (provider={self.provider}, model={self.model})")

    def create_agent(self):
        """Costruisce e restituisce l'agent LangChain pronto all'uso."""
        logger.info("Creazione agent in corso")
        # create_agent richiede l'identificativo del modello nel formato "provider:model"
        return create_agent(
            model=self.provider + self.model,
            system_prompt=self.system_prompt,
            tools=self.tools,
        )
