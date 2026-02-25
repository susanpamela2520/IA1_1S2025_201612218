import os
import tkinter as tk
from tkinter import ttk


#Inialiacion de prolog engine
from backend.prolog_engine import PrologEngine
from ui.login_view import LoginView
from ui.patient_view import PatientView
from ui.admin_view import AdminView

#controla la navegacion entre vistas 

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("MediLogic - Sistema Experto")
        self.geometry("1100x700")

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
        PatientView(self.container, self.engine)

    def show_admin(self, role):
        self.clear()
        AdminView(self.container, self, role)


if __name__ == "__main__":
    app = App()
    app.mainloop()