from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from ui.styles import PALETTE

# Chart (matplotlib embebido en Tkinter)
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AdminView(ttk.Frame):
    def __init__(self, parent, app_controller, role: str):
        super().__init__(parent)
        self.app = app_controller
        self.role = role
        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Layout principal: Sidebar + Content
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True, padx=14, pady=14)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        sidebar = ttk.Frame(root, style="Surface.TFrame")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        sidebar.configure(width=260)
        sidebar.grid_propagate(False)

        content = ttk.Frame(root)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        self._build_sidebar(sidebar)
        self._build_content(content)

    def _build_sidebar(self, sidebar: ttk.Frame):
        header = ttk.Frame(sidebar, style="Surface.TFrame")
        header.pack(fill="x", padx=14, pady=14)

        ttk.Label(header, text="MediLogic", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w")
        ttk.Label(header, text=f"Panel {self.role}", style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", pady=(2, 0))

        ttk.Separator(sidebar).pack(fill="x", padx=14, pady=10)

        nav = ttk.Frame(sidebar, style="Surface.TFrame")
        nav.pack(fill="both", expand=True, padx=14)

        def nav_btn(txt, cmd=None):
            b = ttk.Button(nav, text=txt, style="Ghost.TButton", command=cmd)
            b.pack(fill="x", pady=6)
            return b

        nav_btn("📊 Dashboard", cmd=lambda: None)

        if self.role == "Doctor":
            nav_btn("🩺 Diagnósticos")
            nav_btn("📁 Historial clínico")
            nav_btn("🧾 Reportes")
        else:
            nav_btn("👤 Registrar paciente")
            nav_btn("📅 Citas")
            nav_btn("🧑‍💼 Usuarios")

        ttk.Separator(sidebar).pack(fill="x", padx=14, pady=10)

        footer = ttk.Frame(sidebar, style="Surface.TFrame")
        footer.pack(fill="x", padx=14, pady=14)

        ttk.Button(footer, text="Cerrar sesión", style="Primary.TButton", command=self.app.show_login).pack(fill="x")

    def _build_content(self, content: ttk.Frame):
        # Top header
        top = ttk.Frame(content, style="Surface.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        left = ttk.Frame(top, style="Surface.TFrame")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=14)

        ttk.Label(left, text="Dashboard", style="Title.TLabel", background=PALETTE["surface"]).pack(anchor="w")
        ttk.Label(left, text=f"Resumen operativo • {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                  style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", pady=(2, 0))

        # KPI Cards row
        kpi_row = ttk.Frame(content)
        kpi_row.grid(row=1, column=0, sticky="ew", pady=12)
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Datos demo (luego los conectas a tus registros)
        demo = self._get_demo_metrics()

        self._kpi_card(kpi_row, 0, "Pacientes hoy", str(demo["patients_today"]), "success")
        self._kpi_card(kpi_row, 1, "Diagnósticos", str(demo["diagnoses_today"]), "primary")
        self._kpi_card(kpi_row, 2, "Urgencia alta", str(demo["high_urgency"]), "danger")
        self._kpi_card(kpi_row, 3, "Citas pendientes", str(demo["pending_appointments"]), "warning")

        # Main grid: Chart + Activity
        main = ttk.Frame(content)
        main.grid(row=2, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        chart_card = ttk.Frame(main, style="Surface.TFrame")
        chart_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        right_card = ttk.Frame(main, style="Surface.TFrame")
        right_card.grid(row=0, column=1, sticky="nsew")

        self._build_chart(chart_card, demo["weekly_series"])
        self._build_activity(right_card, demo["recent_activity"])

    def _kpi_card(self, parent, col, title, value, tone: str):
        tones = {
            "primary": PALETTE["primary"],
            "success": PALETTE["success"],
            "warning": PALETTE["warning"],
            "danger": PALETTE["danger"],
        }
        accent = tones.get(tone, PALETTE["primary"])

        card = ttk.Frame(parent, style="Surface.TFrame")
        card.grid(row=0, column=col, sticky="ew", padx=6)
        card.grid_columnconfigure(0, weight=1)

        # “Accent bar” (frame de color)
        bar = tk.Frame(card, bg=accent, height=5)
        bar.grid(row=0, column=0, sticky="ew")

        inner = ttk.Frame(card, style="Surface.TFrame")
        inner.grid(row=1, column=0, sticky="nsew", padx=14, pady=14)

        ttk.Label(inner, text=title, style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w")
        ttk.Label(inner, text=value, font=("Segoe UI", 20, "bold"),
                  background=PALETTE["surface"], foreground=PALETTE["text"]).pack(anchor="w", pady=(6, 0))

    def _build_chart(self, parent: ttk.Frame, series):
        ttk.Label(parent, text="Tendencia semanal", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(parent, text="Volumen de atenciones (demo)", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)
        x = list(range(1, len(series) + 1))
        ax.plot(x, series, marker="o")  # Sin colores forzados
        ax.set_xlabel("Día")
        ax.set_ylabel("Atenciones")
        ax.grid(True, alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _build_activity(self, parent: ttk.Frame, rows):
        ttk.Label(parent, text="Actividad reciente", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(parent, text="Últimos eventos (demo)", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        cols = ("hora", "evento", "estado")
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=10)
        tree.heading("hora", text="Hora")
        tree.heading("evento", text="Evento")
        tree.heading("estado", text="Estado")

        tree.column("hora", width=70)
        tree.column("evento", width=220)
        tree.column("estado", width=90)

        for r in rows:
            tree.insert("", tk.END, values=r)

        tree.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _get_demo_metrics(self):
        """
        Datos demo del dashboard.
        Luego puedes reemplazar con datos reales guardados (JSON/DB).
        """
        return {
            "patients_today": 18,
            "diagnoses_today": 25,
            "high_urgency": 3,
            "pending_appointments": 7,
            "weekly_series": [12, 14, 11, 18, 20, 17, 22],
            "recent_activity": [
                ("08:10", "Paciente registrado", "OK"),
                ("09:05", "Diagnóstico generado", "OK"),
                ("10:22", "Cita creada", "OK"),
                ("11:40", "Urgencia alta detectada", "ALERTA"),
                ("13:15", "Reporte exportado", "OK"),
            ],
        }