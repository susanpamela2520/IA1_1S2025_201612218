#Punto de entrada de MediLogic
#Controlador principal de vistas: Home -> Paciente | Home -> Login -> Admin

import os, sys, tkinter as tk
from tkinter import messagebox

#Aqui se obtiene la ruta base del proyecto para construir rutas absolutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from backend.prolog_engine import PrologEngine
from ui.styles import apply_styles, PALETTE


class MediLogicApp(tk.Tk):

    #Ruta al archivo de conocimiento Prolog
    #La carpeta se llama "prolog" dentro del proyecto
    PL_PATH = os.path.join(BASE_DIR, "prolog", "medilogic.pl")

    def __init__(self):
        super().__init__()
        self.title("MediLogic — Sistema Experto Médico · USAC IA1 2026")
        self.geometry("1150x730")
        self.minsize(900, 600)
        self.configure(bg=PALETTE["bg"])
        apply_styles(self)

        #Cargar motor Prolog al iniciar la aplicacion
        try:
            self.engine = PrologEngine(self.PL_PATH)
        except Exception as e:
            messagebox.showerror("Error al iniciar",
                f"No se pudo cargar la base Prolog:\n{e}\n\nRuta: {self.PL_PATH}")
            self.destroy()
            return

        self._vista_actual = None
        self.show_home()  # Mostrar pantalla de inicio

    def _limpiar_vista(self):
        #Destruye la vista actual antes de mostrar una nueva
        if self._vista_actual:
            self._vista_actual.destroy()
            self._vista_actual = None

    def show_home(self):
        #Pantalla de inicio sin autenticacion - descripcion del sistema
        from ui.home_view import HomeView
        self._limpiar_vista()
        self._vista_actual = HomeView(self, app_controller=self)

    def show_login(self):
        #Pantalla de login para acceso al modulo Admin
        from ui.login_view import LoginView
        self._limpiar_vista()
        self._vista_actual = LoginView(self, app_controller=self)

    def show_patient(self):
        #Modulo del paciente: formulario de sintomas y diagnostico
        from ui.patient_view import PatientView
        self._limpiar_vista()
        self._vista_actual = PatientView(self, engine=self.engine,
                                          app_controller=self)

    def show_admin(self, role: str = "Admin"):
        #Modulo del administrador: CRUD de enfermedades y medicamentos
        from ui.admin_view import AdminView
        self._limpiar_vista()
        self._vista_actual = AdminView(self, engine=self.engine,
                                       pl_ruta=self.PL_PATH,
                                       app_controller=self)


if __name__ == "__main__":
    MediLogicApp().mainloop()