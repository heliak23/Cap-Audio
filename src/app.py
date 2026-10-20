import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.config import Config
from src.audio_recorder import AudioRecorder
from src.stt_engine import STTEngine
from src.text_cleaner import TextCleaner
from src.text_injector import TextInjector
from src.overlay_hud import OverlayHUD
from src.hotkey_listener import HotkeyListener

class CapAudioApp:
    def __init__(self):
        print("=" * 55)
        print("       CapAudio - Ditado por Voz Inteligente")
        print("=" * 55)
        print(f"• Modo de Ativacao : {Config.MODE.upper()}")
        print(f"• Tecla de Atalho  : {Config.HOTKEY.upper()}")
        print(f"• Idioma           : {Config.LANGUAGE}")
        print(f"• Provedor STT     : {Config.STT_PROVIDER.upper()}")
        if Config.STT_PROVIDER in ("local", "auto"):
            print(f"• Modelo Local     : {Config.LOCAL_MODEL_SIZE} ({Config.LOCAL_DEVICE})")
        print("=" * 55)

        self.recorder = AudioRecorder()
        self.stt = STTEngine()
        self.cleaner = TextCleaner(
            groq_client=self.stt.groq_client,
            openai_client=self.stt.openai_client
        )
        self.hud = OverlayHUD()
        self.listener = HotkeyListener(
            on_start_callback=self._handle_recording_start,
            on_stop_callback=self._handle_recording_stop
        )

    def _handle_recording_start(self):
        print("\n[Gravando...] Fale no microfone...")
        self.hud.show_recording()
        self.recorder.start()

    def _handle_recording_stop(self):
        print("[Processando...] Finalizando audio capturado...")
        self.hud.show_transcribing()
        wav_bytes = self.recorder.stop()

        if not wav_bytes or len(wav_bytes) < 1500:
            print("[Aviso] Audio muito curto ou vazio.")
            self.hud.hide()
            return

        # 1. Transcrição (STT)
        start_time = time.time()
        raw_text = self.stt.transcribe(wav_bytes)
        stt_duration = time.time() - start_time

        if not raw_text:
            print("[Aviso] Nenhuma fala detectada.")
            self.hud.hide()
            return

        print(f"[Transcricao Bruta ({stt_duration:.2f}s)]: {raw_text}")

        # 2. Limpeza e Formatação Inteligente (LLM / Regras)
        self.hud.show_cleaning()
        clean_start = time.time()
        final_text = self.cleaner.clean(raw_text)
        clean_duration = time.time() - clean_start

        print(f"[Texto Polido ({clean_duration:.2f}s)]: {final_text}")

        # 3. Injeção no Cursor Ativo
        self.hud.show_done()
        TextInjector.inject(final_text)
        print(f"[Sucesso] Texto colado no aplicativo ativo!\n")

    def run(self):
        self.listener.start()
        print(f"\n[Pronto!] Pressione e segure [{Config.HOTKEY.upper()}] para ditar.")
        print("Para sair, feche este terminal ou pressione Ctrl + C.\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[Encerrando] Ate logo!")
            self.listener.stop()
            self.hud.hide()
