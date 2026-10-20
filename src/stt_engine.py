import io
import speech_recognition as sr
from src.config import Config

class STTEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.groq_client = None
        self.openai_client = None
        self.local_model = None
        
        # Inicializar Groq se disponível
        if Config.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
            except Exception as e:
                print(f"[Aviso] Falha ao inicializar Groq: {e}")

        # Inicializar OpenAI se disponível
        if Config.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            except Exception as e:
                print(f"[Aviso] Falha ao inicializar OpenAI: {e}")

        # Inicializar modelo Whisper local se configurado para 'local' ou 'auto' (quando não houver chaves de API)
        needs_local = Config.STT_PROVIDER == "local" or (
            Config.STT_PROVIDER == "auto" and not Config.GROQ_API_KEY and not Config.OPENAI_API_KEY
        )
        if needs_local:
            self._load_local_model()

    def _load_local_model(self):
        try:
            from faster_whisper import WhisperModel
            print(f"[Offline STT] Carregando modelo Whisper local ('{Config.LOCAL_MODEL_SIZE}')...")
            self.local_model = WhisperModel(
                Config.LOCAL_MODEL_SIZE,
                device=Config.LOCAL_DEVICE,
                compute_type="int8"
            )
            print("[Offline STT] Modelo local pronto para uso (100% offline)!")
        except Exception as e:
            print(f"[Aviso] Falha ao carregar faster-whisper local: {e}")

    def transcribe(self, wav_bytes: bytes) -> str:
        if not wav_bytes or len(wav_bytes) < 1000:
            return ""

        provider = Config.STT_PROVIDER

        # 1. Groq Whisper (Online - Baixíssima latência ~200ms)
        if (provider in ("groq", "auto")) and self.groq_client:
            try:
                audio_file = ("speech.wav", wav_bytes, "audio/wav")
                lang = Config.LANGUAGE.split("-")[0]
                res = self.groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                    language=lang,
                    response_format="text"
                )
                return str(res).strip()
            except Exception as e:
                print(f"[STT Groq Erro]: {e}. Tentando fallback...")

        # 2. OpenAI Whisper (Online)
        if (provider in ("openai", "auto")) and self.openai_client:
            try:
                audio_file = ("speech.wav", wav_bytes, "audio/wav")
                lang = Config.LANGUAGE.split("-")[0]
                res = self.openai_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language=lang
                )
                return res.text.strip()
            except Exception as e:
                print(f"[STT OpenAI Erro]: {e}. Tentando fallback...")

        # 3. Whisper Local (100% Offline - Privacidade Total, Custo Zero)
        if self.local_model is None:
            self._load_local_model()

        if self.local_model is not None:
            try:
                wav_io = io.BytesIO(wav_bytes)
                lang = Config.LANGUAGE.split("-")[0]
                segments, info = self.local_model.transcribe(
                    wav_io,
                    language=lang,
                    beam_size=5,
                    vad_filter=True  # Filtra silêncio automaticamente
                )
                text = " ".join([segment.text for segment in segments]).strip()
                return text
            except Exception as e:
                print(f"[STT Local Erro]: {e}. Tentando fallback...")

        # 4. Fallback: Google Speech Recognition (Online gratuito)
        try:
            wav_file = io.BytesIO(wav_bytes)
            with sr.AudioFile(wav_file) as source:
                audio_data = self.recognizer.record(source)
            text = self.recognizer.recognize_google(audio_data, language=Config.LANGUAGE)
            return text.strip()
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[STT Google Erro]: {e}")
            return ""
