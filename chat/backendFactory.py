from .session import Backend

try:
    from chat.backendOllama import BackendOllama
    OLLAMA_AVAILABLE = True
except:
    BackendOllama = Backend
    OLLAMA_AVAILABLE = False
try:
    from chat.backendOpenAI import BackendOpenAI
    OPENAI_AVAILABLE = True
except:
    BackendOpenAI = Backend
    OPENAI_AVAILABLE = False

def availableBackends():
    res = []
    res += ["ollama"] if OLLAMA_AVAILABLE else []
    res += ["openai"] if OPENAI_AVAILABLE else []
    return res

def createBackend(backend:str = "ollama", model:str = "qwen3:8b", think:bool=False, **kwargs) -> Backend:
    if backend == "ollama":
        if not OLLAMA_AVAILABLE:
            raise Exception("Backend ollama not available!")
        return BackendOllama(model, think=think)
    elif backend == "openai":
        if not OPENAI_AVAILABLE:
            raise Exception("Backend openai not available!")
        return BackendOpenAI(model)
    raise Exception(f"Unknown backend: {backend}!")