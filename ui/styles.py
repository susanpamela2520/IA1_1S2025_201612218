from __future__ import annotations
from tkinter import ttk

# Paleta hospital (limpia + moderna)
PALETTE = {
    "bg": "#F6F9FF",
    "surface": "#FFFFFF",
    "surface2": "#F1F5FF",
    "text": "#0F172A",
    "muted": "#475569",
    "primary": "#1D4ED8",
    "primary2": "#2563EB",
    "success": "#16A34A",
    "warning": "#F59E0B",
    "danger": "#DC2626",
    "border": "#E2E8F0",
}

def apply_hospital_theme(root):
    """
    Aplica estilos ttk. Funciona bien en Windows/macOS/Linux.
    """
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=PALETTE["bg"])

    # Base
    style.configure(".", font=("Segoe UI", 10), background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("TFrame", background=PALETTE["bg"])
    style.configure("Surface.TFrame", background=PALETTE["surface"])
    style.configure("Surface2.TFrame", background=PALETTE["surface2"])

    style.configure("TLabel", background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("Muted.TLabel", foreground=PALETTE["muted"])
    style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
    style.configure("H2.TLabel", font=("Segoe UI", 12, "bold"))
    style.configure("H3.TLabel", font=("Segoe UI", 11, "bold"))

    # Inputs
    style.configure("TEntry", padding=8, relief="flat")
    style.configure("TCombobox", padding=6)
    style.map("TCombobox", fieldbackground=[("readonly", PALETTE["surface"])])

    # Buttons
    style.configure("Primary.TButton", padding=(12, 10), relief="flat",
                    background=PALETTE["primary"], foreground="white")
    style.map("Primary.TButton",
              background=[("active", PALETTE["primary2"]), ("disabled", PALETTE["border"])],
              foreground=[("disabled", PALETTE["muted"])])

    style.configure("Ghost.TButton", padding=(12, 10), relief="flat",
                    background=PALETTE["surface"], foreground=PALETTE["primary"])
    style.map("Ghost.TButton",
              background=[("active", PALETTE["surface2"])])

    # Labelframe
    style.configure("TLabelframe", background=PALETTE["bg"], foreground=PALETTE["text"])
    style.configure("TLabelframe.Label", background=PALETTE["bg"], font=("Segoe UI", 10, "bold"))

    # Treeview
    style.configure("Treeview",
                    background=PALETTE["surface"],
                    fieldbackground=PALETTE["surface"],
                    foreground=PALETTE["text"],
                    bordercolor=PALETTE["border"],
                    borderwidth=1,
                    rowheight=28)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.map("Treeview", background=[("selected", PALETTE["surface2"])])