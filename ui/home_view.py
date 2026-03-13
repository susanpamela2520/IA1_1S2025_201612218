import tkinter as tk
from tkinter import ttk
from ui.styles import PALETTE


class HomeView(ttk.Frame):
    """Pantalla principal accesible sin credenciales."""

    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Fondo degradado simulado con dos frames
        bg_top = tk.Frame(self, bg=PALETTE["primary"], height=220)
        bg_top.pack(fill="x")
        bg_top.pack_propagate(False)

        # Logo + título en el área azul
        hero = ttk.Frame(bg_top, style="TFrame")
        hero.configure(style="TFrame")
        hero.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(bg_top, text="⚕  MediLogic",
                 bg=PALETTE["primary"], fg="white",
                 font=("Segoe UI", 32, "bold")).pack(pady=(40, 6))
        tk.Label(bg_top,
                 text="Sistema Experto de Diagnóstico Médico Preliminar",
                 bg=PALETTE["primary"], fg="#BDC3FF",
                 font=("Segoe UI", 13)).pack()
        tk.Label(bg_top,
                 text="Universidad San Carlos de Guatemala · Facultad de Ingeniería · IA1 2026",
                 bg=PALETTE["primary"], fg="#9BAAFF",
                 font=("Segoe UI", 9)).pack(pady=(4, 0))

        # Cuerpo central
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)

        center = ttk.Frame(body, style="Surface.TFrame")
        center.place(relx=0.5, rely=0.5, anchor="center", width=700, height=340)

        ttk.Label(center, text="¿Qué es MediLogic?", style="H2.TLabel",
                  background=PALETTE["surface"]).pack(pady=(20, 8))

        desc = (
            "MediLogic es una herramienta de orientación médica basada en inteligencia artificial simbólica.\n"
            "Utiliza un motor lógico implementado en Prolog para analizar los síntomas,\n"
            "alergias y enfermedades crónicas que ingreses, y te proporciona:\n\n"
            "  • Lista de enfermedades posibles ordenadas por % de afinidad\n"
            "  • Medicamentos seguros considerando tus contraindicaciones\n"
            "  • Nivel de urgencia y recomendación de acción\n"
            "  • Explicación de las reglas lógicas activadas\n\n"
            "⚕ Este sistema NO sustituye la consulta médica profesional."
        )
        ttk.Label(center, text=desc, style="Muted.TLabel",
                  background=PALETTE["surface"],
                  justify="left", font=("Segoe UI", 10)).pack(padx=24, pady=(0, 16))

        btn_frame = ttk.Frame(center, style="Surface.TFrame")
        btn_frame.pack(pady=(0, 20))

        ttk.Button(btn_frame, text=" Ingresar como Paciente",
                   style="Primary.TButton",
                   command=self.app.show_patient).pack(side="left", padx=8, ipadx=10, ipady=4)

        ttk.Button(btn_frame, text=" Acceso Administrativo",
                   style="Ghost.TButton",
                   command=self.app.show_login).pack(side="left", padx=8, ipadx=10, ipady=4)
