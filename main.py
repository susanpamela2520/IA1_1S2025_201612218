import os
import tkinter as tk
from tkinter import ttk

from backend.prolog_engine import PrologEngine
from ui.styles import apply_hospital_theme
from ui.login_view import LoginView
from ui.patient_view import PatientView
from ui.admin_view import AdminView


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediLogic - Sistema Experto")
        self.geometry("1200x720")
        self.minsize(1100, 680)

        apply_hospital_theme(self)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        prolog_path = os.path.join(base_dir, "prolog", "medilogic.pl")
        self.engine = PrologEngine(prolog_path)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        LoginView(self.container, self)

    def show_patient(self):
        self.clear()
        PatientView(self.container, self.engine, app_controller=self)

    def show_admin(self, role):
        self.clear()
        AdminView(self.container, self, role)


        # Lista enfermedades para ver si al menos disease/4 existe
        diseases = list(self.prolog.query("current_predicate(disease/4)."))
        if not diseases:
            raise RuntimeError("No existe disease/4. Probablemente NO se cargó tu archivo medilogic.pl correcto.")


if __name__ == "__main__":
    App().mainloop()