import math
import time
import queue
import threading
import tkinter as tk
from src.config import Config

class OverlayHUD:
    """
    HUD Flutuante Moderno estilo 'Dynamic Island / Capsule Pill'
    com cantos arredondados sem bordas quadradas e visualizador de ondas sonoras animado.
    """
    def __init__(self):
        self.enabled = Config.SHOW_HUD
        self.queue = queue.Queue()
        self.state = "idle"  # idle, recording, transcribing, cleaning, done
        self.anim_t = 0.0

        self.root = None
        self.canvas = None
        self._thread = None

        if self.enabled:
            self._thread = threading.Thread(target=self._run_hud_loop, daemon=True)
            self._thread.start()

    def _draw_rounded_capsule(self, x1, y1, x2, y2, fill, outline, width=1.5):
        """Desenha uma cápsula com cantos perfeitamente arredondados."""
        r = (y2 - y1) / 2
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.canvas.create_polygon(points, fill=fill, outline=outline, width=width, smooth=True)

    def _run_hud_loop(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Cor mágica de transparência do Windows para formato de pílula perfeito
        transparent_key = "#000001"
        self.root.wm_attributes("-transparentcolor", transparent_key)

        width = 270
        height = 54

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - width) // 2
        y = screen_height - 110  # Acima da barra de tarefas

        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg=transparent_key,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # Inicialmente oculto
        self.root.withdraw()

        # Iniciar ciclo de animação a ~40 FPS (25ms)
        self._animation_tick()
        self.root.mainloop()

    def _animation_tick(self):
        try:
            while True:
                action, data = self.queue.get_nowait()
                if action == "state":
                    self.state = data
                    if self.state != "idle":
                        self.root.deiconify()
                    else:
                        self.root.withdraw()
        except queue.Empty:
            pass

        if self.state != "idle" and self.canvas:
            self.anim_t += 0.08
            self._render_frame()

        if self.root:
            self.root.after(25, self._animation_tick)

    def _render_frame(self):
        self.canvas.delete("all")

        # 1. Desenhar Cápsula de Fundo (Dark Glass)
        # Sombra sutil / contorno externo
        self._draw_rounded_capsule(2, 2, 268, 52, fill="#121316", outline="#2A2D37", width=1.8)

        cy = 27  # Centro vertical

        # 2. Renderizar de acordo com o Estado
        if self.state == "recording":
            # Visualizador de Ondas Sonoras Animadas (Equalizador de 5 barras pulsantes)
            bar_colors = ["#FF3B30", "#FF5E3A", "#FF9500", "#FF5E3A", "#FF3B30"]
            start_x = 32
            spacing = 7

            for i in range(5):
                # Altura senoidal orgânica para cada barra
                phase = i * 0.85
                h = 8 + 14 * (math.sin(self.anim_t * 3.5 + phase) ** 2) + 4 * (math.cos(self.anim_t * 2.1 + phase) ** 2)
                h = max(6, min(24, h))

                bx = start_x + i * spacing
                self.canvas.create_line(
                    bx, cy - h / 2, bx, cy + h / 2,
                    fill=bar_colors[i],
                    width=3.5,
                    capstyle=tk.ROUND
                )

            # Texto "Ouvindo..." com ponto pulsante
            self.canvas.create_text(
                82, cy,
                text="Ouvindo...",
                anchor="w",
                fill="#FFFFFF",
                font=("Segoe UI", 11, "bold")
            )

            # Dica visual do atalho no canto direito
            self._draw_rounded_capsule(195, 14, 252, 40, fill="#1E2027", outline="#2F333F", width=1)
            self.canvas.create_text(
                223, cy,
                text=Config.HOTKEY.upper(),
                anchor="center",
                fill="#8E95A5",
                font=("Segoe UI", 9, "bold")
            )

        elif self.state == "transcribing":
            # Indicador de Carregamento Pulsante (Ciano)
            pulse_radius = 5 + 3 * (math.sin(self.anim_t * 4.0) ** 2)
            self.canvas.create_oval(
                40 - pulse_radius, cy - pulse_radius,
                40 + pulse_radius, cy + pulse_radius,
                fill="#0A84FF",
                outline="#64D2FF",
                width=1.5
            )

            # 3 pontinhos em órbita
            for j in range(3):
                angle = self.anim_t * 3.0 + j * (2 * math.pi / 3)
                dx = 40 + 13 * math.cos(angle)
                dy = cy + 13 * math.sin(angle)
                self.canvas.create_oval(dx - 2, dy - 2, dx + 2, dy + 2, fill="#64D2FF", outline="")

            self.canvas.create_text(
                75, cy,
                text="Transcrevendo...",
                anchor="w",
                fill="#64D2FF",
                font=("Segoe UI", 11, "bold")
            )

        elif self.state == "cleaning":
            # Brilho IA / Sparkle Pulsante (Lilás/Roxo)
            pulse = 1 + 0.3 * math.sin(self.anim_t * 5.0)
            self.canvas.create_text(
                42, cy,
                text="✦",
                anchor="center",
                fill="#BF5AF2",
                font=("Segoe UI", int(16 * pulse), "bold")
            )

            self.canvas.create_text(
                75, cy,
                text="Formatando com IA...",
                anchor="w",
                fill="#D084F7",
                font=("Segoe UI", 11, "bold")
            )

        elif self.state == "done":
            # Checkmark Verde Neon Animado
            self.canvas.create_oval(
                30, cy - 11,
                52, cy + 11,
                fill="#153621",
                outline="#30D158",
                width=1.5
            )
            self.canvas.create_text(
                41, cy - 1,
                text="✓",
                anchor="center",
                fill="#30D158",
                font=("Segoe UI", 11, "bold")
            )

            self.canvas.create_text(
                75, cy,
                text="Texto Inserido!",
                anchor="w",
                fill="#30D158",
                font=("Segoe UI", 11, "bold")
            )

    def show_recording(self):
        if self.enabled:
            self.queue.put(("state", "recording"))

    def show_transcribing(self):
        if self.enabled:
            self.queue.put(("state", "transcribing"))

    def show_cleaning(self):
        if self.enabled:
            self.queue.put(("state", "cleaning"))

    def show_done(self):
        if self.enabled:
            self.queue.put(("state", "done"))
            threading.Timer(0.85, self.hide).start()

    def hide(self):
        if self.enabled:
            self.queue.put(("state", "idle"))
