# AgenticAI

Esempio didattico di come costruire un **agente AI** con [LangChain](https://python.langchain.com/) collegato a un LLM tramite [OpenRouter](https://openrouter.ai/).

Il progetto mostra l'**architettura tipica** di un agent:

- un **modello** LLM configurato tramite provider,
- una **memoria** conversazionale,
- un insieme di **tool** (funzioni Python) che il modello può invocare per ottenere informazioni esterne,
- un **logger** centralizzato.

> ⚠️ I tool inclusi (meteo via OpenWeather) sono **solo un esempio**. Servono a illustrare come si dichiara, si tipizza e si registra un tool LangChain: in un progetto reale vanno sostituiti con quelli necessari al proprio dominio.

---

## Struttura del progetto

```
AgenticAI/
├── main.py                     # Entry point: loop di chat da terminale
├── requirements.txt
├── .env                        # Variabili d'ambiente (non versionato)
└── src/
    ├── log_config/             # Logger colorato condiviso
    │   ├── __init__.py
    │   └── logger.py
    ├── memory_config/
    │   └── memory.py           # Memoria conversazionale (in-memory, FIFO)
    ├── model_config/
    │   └── model.py            # Factory dell'agent LangChain
    ├── model_tool/
    │   ├── tool.py             # Tool di esempio (get_current_temperature, get_daily_forecast)
    │   ├── schema.py           # Schemi Pydantic di input/output dei tool
    │   └── util.py             # Helper (geocoding, lookup ISO)
    └── data/
        └── country_iso.csv     # Tabella di lookup nome paese → codice ISO
```

---

## Componenti principali

### 1. `AgentConfig` — [src/model_config/model.py](src/model_config/model.py)
Wrapper che incapsula la creazione dell'agent LangChain.
Riceve modello, system prompt e provider e produce un agent pronto all'uso tramite `langchain.agents.create_agent`, registrando automaticamente la lista di tool.

### 2. `MemoryConfig` — [src/memory_config/memory.py](src/memory_config/memory.py)
Memoria conversazionale basata su `InMemoryChatMessageHistory`. Mantiene fino a `max_message` messaggi (FIFO) per non far crescere indefinitamente il contesto inviato al modello.

### 3. Tool — [src/model_tool/tool.py](src/model_tool/tool.py)
Funzioni decorate con `@tool` di LangChain. Lo schema Pydantic passato come `args_schema` consente al modello di sapere **come** invocare il tool. Sono presenti due esempi:
- `get_current_temperature` — temperatura corrente di una città;
- `get_daily_forecast` — previsioni a step da 3h.

### 4. Logger — [src/log_config/logger.py](src/log_config/logger.py)
Logger colorato condiviso (basato su `colorlog`), con guardia per evitare la doppia inizializzazione degli handler.

---

## Flusso di una richiesta

1. L'utente scrive un messaggio in console.
2. `MemoryConfig` lo aggiunge allo storico.
3. L'intero storico viene passato all'agent (`agent.invoke({"messages": ...})`).
4. L'agent decide se rispondere direttamente o chiamare un tool; in tal caso il tool viene eseguito e il risultato torna al modello.
5. La risposta finale viene mostrata all'utente e aggiunta alla memoria.

---

## Setup

### Requisiti
- Python 3.11+ (testato su 3.13)
- Una API key di [OpenRouter](https://openrouter.ai/) per il modello
- (Solo per i tool d'esempio) una API key di [OpenWeather](https://openweathermap.org/api)

### Installazione

```bash
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Variabili d'ambiente

Crea un file `.env` nella root con:

```
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL_NAME=openai/gpt-4o-mini
OPENWEATHER_API_KEY=...
```

### Esecuzione

```bash
python main.py
```

Per uscire dalla chat: `exit`, `quit`, `esci` o `stop`.

---

## Personalizzare i tool

I tool in [src/model_tool/tool.py](src/model_tool/tool.py) sono solo un esempio.
Per aggiungerne uno nuovo:

1. Definire gli schemi di input/output in [src/model_tool/schema.py](src/model_tool/schema.py).
2. Creare la funzione decorata con `@tool(args_schema=...)`.
3. Aggiungerla alla lista `tools` esportata in fondo al file.

L'agent la rileverà automaticamente alla prossima esecuzione.
