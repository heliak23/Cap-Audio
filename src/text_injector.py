import time
import ctypes
import threading
import pyperclip
from src.config import Config

user32 = ctypes.windll.user32

VK_CONTROL = 0x11
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002

class TextInjector:
    @staticmethod
    def _simulate_ctrl_v():
        # Ctrl Down
        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        # V Down
        user32.keybd_event(VK_V, 0, 0, 0)
        # V Up
        user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        # Ctrl Up
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    @classmethod
    def inject(cls, text: str):
        if not text:
            return

        # 1. Salvar clipboard original
        original_clipboard = ""
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            pass

        # 2. Inserir novo texto no clipboard
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"[Erro ao copiar para clipboard]: {e}")
            return

        # 3. Pequeno intervalo para o clipboard do Windows consolidar
        time.sleep(0.04)

        # 4. Disparar Ctrl+V nativo
        cls._simulate_ctrl_v()

        # 5. Restaurar clipboard original em background após o app consumidor ler
        if Config.RESTORE_CLIPBOARD:
            def _restore():
                time.sleep(0.2)
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass

            threading.Thread(target=_restore, daemon=True).start()
