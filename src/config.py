import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis do .env se existir
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    # Provedores de STT:
    # 'local' -> 100% Offline via faster-whisper (sem internet, privacidade total)
    # 'auto'  -> Usa Groq se tiver chave, senão local offline
    # 'groq'  -> Whisper turbo ultrarrápido na nuvem (~200ms)
    # 'openai'-> Whisper oficial OpenAI
    # 'google_free' -> Google Speech Recognition online
    STT_PROVIDER = os.getenv("STT_PROVIDER", "auto").lower()

    # Tamanho do modelo Whisper local (para modo offline):
    # 'tiny' (~75MB, ultrarrápido)
    # 'base' (~145MB, recomendado, excelente precisão em pt-BR)
    # 'small' (~480MB, mais preciso)
    LOCAL_MODEL_SIZE = os.getenv("LOCAL_MODEL_SIZE", "base")
    LOCAL_DEVICE = os.getenv("LOCAL_DEVICE", "cpu")  # 'cpu' ou 'cuda'

    # Chaves de API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Idioma padrão da fala
    LANGUAGE = os.getenv("LANGUAGE", "pt-BR")

    # Atalho do teclado (F8 é seguro e universal no Windows)
    HOTKEY = os.getenv("HOTKEY", "f8").lower()

    # Modo de ativação:
    # 'push_to_talk' (segura para falar, solta para colar)
    # 'toggle' (aperta uma vez para falar, aperta de novo para colar)
    MODE = os.getenv("MODE", "push_to_talk").lower()

    # Taxa de amostragem do microfone (16000Hz mono é o padrão do Whisper)
    SAMPLE_RATE = 16000
    CHANNELS = 1

    # Sons de feedback ao iniciar/parar (Winsound)
    AUDIO_FEEDBACK = os.getenv("AUDIO_FEEDBACK", "true").lower() == "true"

    # Restaurar clipboard anterior após digitar
    RESTORE_CLIPBOARD = os.getenv("RESTORE_CLIPBOARD", "true").lower() == "true"

    # Exibir HUD flutuante (Dynamic Island pill)
    SHOW_HUD = os.getenv("SHOW_HUD", "true").lower() == "true"
