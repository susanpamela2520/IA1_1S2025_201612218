import tkinter as tk
from tkinter import ttk, messagebox
from auth import AuthService


class LoginView(ttk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.auth = AuthService()

        self._build_ui()


    # Contruccion de VISTA DE LOGIN
    
    def _build_ui(self):
        self.pack(fill="both", expand=True)

        container = ttk.Frame(self, padding=40)
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(container, text="MediLogic", font=("Segoe UI", 20, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(container, text="Usuario:").grid(row=1, column=0, sticky="w")
        self.username = ttk.Entry(container)
        self.username.grid(row=1, column=1, pady=5)

        ttk.Label(container, text="Contraseña:").grid(row=2, column=0, sticky="w")
        self.password = ttk.Entry(container, show="*")
        self.password.grid(row=2, column=1, pady=5)

        ttk.Label(container, text="Rol:").grid(row=3, column=0, sticky="w")
        self.role = ttk.Combobox(
            container,
            values=["Doctor", "Personal Administrativo"],
            state="readonly"
        )
        self.role.grid(row=3, column=1, pady=5)
        self.role.current(0)

        login_btn = ttk.Button(container, text="Ingresar como Admin", command=self.login)
        login_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        patient_btn = ttk.Button(container, text="Ingresar como Paciente", command=self.app.show_patient)
        patient_btn.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")

    def login(self):
        user = self.username.get()
        pwd = self.password.get()
        role = self.role.get()

        if self.auth.authenticate(user, pwd):
            self.app.show_admin(role)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")