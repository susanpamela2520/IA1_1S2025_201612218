from tkinter import ttk

PALETTE = {
    "bg":        "#F0F4F8",
    "surface":   "#FFFFFF",
    "primary":   "#2563EB",
    "primary_h": "#1D4ED8",
    "danger":    "#DC2626",
    "success":   "#16A34A",
    "warning":   "#D97706",
    "text":      "#1E293B",
    "muted":     "#64748B",
    "border":    "#E2E8F0",
    "alt_row":   "#F8FAFC",
    "urgent_a": "#EA4335",   # alta  → rojo
    "urgent_m": "#FBBC04",   # media → amarillo  
    "urgent_b": "#34A853",   # baja  → verde
}

COLOR_URGENCIA = {
    "alta":  "#DC2626",
    "media": "#D97706",
    "baja":  "#16A34A",
}

FRASE_URGENCIA = {
    "alta":  "Consulta medica inmediata sugerida",
    "media": "Observacion recomendada",
    "baja":  "Posible automanejo",
}


def aplicar_estilos(root):
    root.configure(bg=PALETTE["bg"])
    s = ttk.Style(root)
    s.theme_use("clam")

    s.configure("TFrame",         background=PALETTE["bg"])
    s.configure("Surface.TFrame", background=PALETTE["surface"])
    s.configure("Dark.TFrame",    background=PALETTE["primary"])

    s.configure("TLabel",
                background=PALETTE["bg"],
                foreground=PALETTE["text"],
                font=("Segoe UI", 10))
    s.configure("Title.TLabel",
                font=("Segoe UI", 24, "bold"),
                foreground=PALETTE["primary"],
                background=PALETTE["surface"])
    s.configure("H2.TLabel",
                font=("Segoe UI", 13, "bold"),
                foreground=PALETTE["text"],
                background=PALETTE["surface"])
    s.configure("H3.TLabel",
                font=("Segoe UI", 11, "bold"),
                foreground=PALETTE["text"],
                background=PALETTE["surface"])
    s.configure("Muted.TLabel",
                foreground=PALETTE["muted"],
                font=("Segoe UI", 9),
                background=PALETTE["surface"])
    s.configure("White.TLabel",
                foreground="white",
                font=("Segoe UI", 10),
                background=PALETTE["primary"])
    s.configure("WhiteBold.TLabel",
                foreground="white",
                font=("Segoe UI", 14, "bold"),
                background=PALETTE["primary"])

    s.configure("Primary.TButton",
                background=PALETTE["primary"],
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                padding=(14, 7), relief="flat")
    s.map("Primary.TButton", background=[("active", PALETTE["primary_h"])])

    s.configure("Ghost.TButton",
                background=PALETTE["surface"],
                foreground=PALETTE["primary"],
                font=("Segoe UI", 10),
                padding=(12, 6), relief="flat")
    s.map("Ghost.TButton", background=[("active", PALETTE["bg"])])

    s.configure("Danger.TButton",
                background=PALETTE["danger"],
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                padding=(10, 5), relief="flat")
    s.map("Danger.TButton", background=[("active", "#B91C1C")])

    s.configure("Success.TButton",
                background=PALETTE["success"],
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                padding=(10, 5), relief="flat")
    s.map("Success.TButton", background=[("active", "#15803D")])

    s.configure("Warning.TButton",
                background=PALETTE["warning"],
                foreground="white",
                font=("Segoe UI", 10, "bold"),
                padding=(10, 5), relief="flat")

    s.configure("Treeview",
                background=PALETTE["surface"],
                fieldbackground=PALETTE["surface"],
                foreground=PALETTE["text"],
                rowheight=30,
                font=("Segoe UI", 9))
    s.configure("Treeview.Heading",
                background=PALETTE["primary"],
                foreground="white",
                font=("Segoe UI", 9, "bold"),
                padding=6)
    s.map("Treeview",
          background=[("selected", PALETTE["primary"])],
          foreground=[("selected", "white")])

    s.configure("TNotebook",     background=PALETTE["bg"])
    s.configure("TNotebook.Tab", padding=(18, 9), font=("Segoe UI", 10))

    s.configure("Afinidad.Horizontal.TProgressbar",
                troughcolor=PALETTE["border"],
                background=PALETTE["primary"],
                thickness=16)
    s.configure("AfinidadAlta.Horizontal.TProgressbar",
                troughcolor=PALETTE["border"],
                background=PALETTE["danger"],
                thickness=16)
    s.configure("TEntry", padding=5)
    s.configure("TCombobox", padding=5)


apply_styles = aplicar_estilos