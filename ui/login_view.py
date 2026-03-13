from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

from auth import AuthService
from ui.styles import PALETTE


class AdminAuthDialog(tk.Toplevel):
    #Autenticacion de Administrador
    def __init__(self, parent, on_success_callback):
        super().__init__(parent)
        self.title("Acceso Administrativo")
        self.resizable(False, False)
        self.configure(bg=PALETTE["bg"])

        self.auth = AuthService()
        self.on_success = on_success_callback  # fn(role)

        # Modal behavior
        self.transient(parent)
        self.grab_set()

        self._build_ui()
        self._center_over_parent(parent)

        self.user_entry.focus_set()
        self.bind("<Return>", lambda e: self._login())
        self.bind("<Escape>", lambda e: self.destroy())

    def _build_ui(self):
        card = ttk.Frame(self, style="Surface.TFrame")
        card.pack(fill="both", expand=True, padx=14, pady=14)

        ttk.Label(card, text="Verificación de Credenciales", style="H2.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 2))
        ttk.Label(card, text="Ingresa el usuario admin y selecciona rol.", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 12))

        form = ttk.Frame(card, style="Surface.TFrame")
        form.pack(fill="x", padx=14, pady=(0, 14))

        ttk.Label(form, text="Usuario", background=PALETTE["surface"]).grid(row=0, column=0, sticky="w", pady=6)
        self.user_entry = ttk.Entry(form, width=28)
        self.user_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(form, text="Contraseña", background=PALETTE["surface"]).grid(row=1, column=0, sticky="w", pady=6)
        self.pass_entry = ttk.Entry(form, show="•", width=28)
        self.pass_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=6)

        ttk.Label(form, text="Rol", background=PALETTE["surface"]).grid(row=2, column=0, sticky="w", pady=6)
        self.role_combo = ttk.Combobox(
            form,
            values=["Doctor", "Personal Administrativo"],
            state="readonly",
            width=26
        )
        self.role_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=6)
        self.role_combo.current(0)

        form.grid_columnconfigure(1, weight=1)

        actions = ttk.Frame(card, style="Surface.TFrame")
        actions.pack(fill="x", padx=14, pady=(0, 14))

        ttk.Button(actions, text="Cancelar", style="Ghost.TButton", command=self.destroy).pack(side="right")
        ttk.Button(actions, text="Ingresar", style="Primary.TButton", command=self._login).pack(side="right", padx=(0, 10))

        tip = "Tip: usuario: admin | contraseña: 1234"
        ttk.Label(card, text=tip, style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 14))

    def _login(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        role = self.role_combo.get().strip()

        if self.auth.authenticate(user, pwd):
            self.destroy()
            self.on_success(role)
        else:
            messagebox.showerror("Acceso denegado", "Credenciales incorrectas.")

    def _center_over_parent(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()

        w = self.winfo_width()
        h = self.winfo_height()

        x = px + (pw // 2) - (w // 2)
        y = py + (ph // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")


class LoginView(ttk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Card centrada
        card = ttk.Frame(self, style="Surface.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center", width=560, height=360)

        header = ttk.Frame(card, style="Surface.TFrame")
        header.pack(fill="x", padx=22, pady=(18, 10))

        ttk.Label(header, text="MediLogic", style="Title.TLabel", background=PALETTE["surface"]).pack(anchor="w")
        ttk.Label(header, text="Sistema experto • Interfaz clínica", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", pady=(2, 0))

        body = ttk.Frame(card, style="Surface.TFrame")
        body.pack(fill="both", expand=True, padx=22, pady=10)

        ttk.Label(body, text="Selecciona el modo de ingreso:", style="H3.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", pady=(0, 10))

        ttk.Button(
            body,
            text=" Entrar como Paciente",
            style="Primary.TButton",
            command=self.app.show_patient
        ).pack(fill="x", pady=8)

        ttk.Button(
            body,
            text=" Entrar como Admin/Doctor",
            style="Ghost.TButton",
            command=self._open_admin_modal
        ).pack(fill="x", pady=8)

        footer = ttk.Frame(card, style="Surface.TFrame")
        footer.pack(fill="x", padx=22, pady=(0, 18))
        ttk.Label(
            footer,
            text="El acceso administrativo requiere credenciales.",
            style="Muted.TLabel",
            background=PALETTE["surface"]
        ).pack(anchor="w")
        if hasattr(self.app, 'show_home'):
            ttk.Button(footer, text="← Volver al inicio", style="Ghost.TButton",
                       command=self.app.show_home).pack(anchor="w", pady=(8, 0))

    def _open_admin_modal(self):
        AdminAuthDialog(self.app, on_success_callback=self.app.show_admin)