import tkinter as tk
from tkinter import ttk


class AdminView(ttk.Frame):
    def __init__(self, parent, app_controller, role):
        super().__init__(parent)
        self.app = app_controller
        self.role = role
        self._build_ui()

    # Contruccion de VISTA DE ADMINISTRADOR 

    def _build_ui(self):
        self.pack(fill="both", expand=True, padx=20, pady=20)

        top = ttk.Frame(self)
        top.pack(fill="x")

        ttk.Label(
            top,
            text=f"Panel Administrativo - Rol: {self.role}",
            font=("Segoe UI", 16, "bold")
        ).pack(side="left")

        ttk.Button(top, text="Cerrar sesión", command=self.app.show_login).pack(side="right")

        separator = ttk.Separator(self, orient="horizontal")
        separator.pack(fill="x", pady=10)

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)

        if self.role == "Doctor":
            self._doctor_view(content)
        else:
            self._admin_staff_view(content)

    def _doctor_view(self, frame):
        ttk.Label(frame, text="Funciones del Doctor", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        ttk.Button(frame, text="Ver diagnósticos realizados").pack(pady=5, anchor="w")
        ttk.Button(frame, text="Revisar historial clínico").pack(pady=5, anchor="w")
        ttk.Button(frame, text="Generar reporte médico").pack(pady=5, anchor="w")

    def _admin_staff_view(self, frame):
        ttk.Label(frame, text="Funciones Administrativas", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        ttk.Button(frame, text="Registrar nuevo paciente").pack(pady=5, anchor="w")
        ttk.Button(frame, text="Gestionar citas").pack(pady=5, anchor="w")
        ttk.Button(frame, text="Administrar usuarios").pack(pady=5, anchor="w")