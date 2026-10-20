import sys
from pathlib import Path

# Garantir UTF-8 na saída do console do Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Adicionar pasta raiz ao path do Python
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.app import CapAudioApp

if __name__ == "__main__":
    app = CapAudioApp()
    app.run()
