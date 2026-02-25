from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

from backend.prolog_engine import PrologEngine, DiagnosisResult


SYMPTOMS = [
    "fiebre",
    "tos",
    "dolor_garganta",
    "congestion_nasal",
    "dolor_cabeza",
    "dolor_pecho",
    "fatiga",
    "nausea",
]

SEVERITIES = ["leve", "moderado", "severo"]

ALLERGIES = [
    "alergia_aines",
    "alergia_antihistaminicos",
]

CONDITIONS = [
    "insuficiencia_renal",
    "gastritis_cronica",
]


class PatientView(ttk.Frame):
    def __init__(self, parent: tk.Misc, engine: PrologEngine):
        super().__init__(parent)
        self.engine = engine

        self.sym_vars = {}
        self.sev_vars = {}

        self._build_ui()

    def _build_ui(self):

        back = ttk.Button(self, text="← Volver al Inicio", command=self.master.master.show_login)
        back.grid(row=0, column=3, padx=10)
        title = ttk.Label(self,
         text="Consulta Médica - Paciente",
        font=("Segoe UI", 16, "bold"))
        

        # --- Síntomas ---
        box_sym = ttk.LabelFrame(self, text="Síntomas (selecciona y asigna severidad)")
        box_sym.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        for i, s in enumerate(SYMPTOMS):
            v = tk.BooleanVar(value=False)
            self.sym_vars[s] = v
            cb = ttk.Checkbutton(box_sym, text=s, variable=v)
            cb.grid(row=i, column=0, sticky="w", padx=8, pady=2)

            sev = tk.StringVar(value="leve")
            self.sev_vars[s] = sev
            combo = ttk.Combobox(box_sym, values=SEVERITIES, textvariable=sev, state="readonly", width=10)
            combo.grid(row=i, column=1, sticky="w", padx=8, pady=2)

        # --- Alergias ---
        box_all = ttk.LabelFrame(self, text="Alergias a medicamentos (opcional)")
        box_all.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.allergy_list = tk.Listbox(box_all, selectmode=tk.MULTIPLE, height=8)
        for a in ALLERGIES:
            self.allergy_list.insert(tk.END, a)
        self.allergy_list.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        # --- Condiciones crónicas ---
        box_con = ttk.LabelFrame(self, text="Enfermedades crónicas (opcional)")
        box_con.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        self.cond_list = tk.Listbox(box_con, selectmode=tk.MULTIPLE, height=8)
        for c in CONDITIONS:
            self.cond_list.insert(tk.END, c)
        self.cond_list.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        # --- Botón analizar ---
        btn = ttk.Button(self, text="Analizar (Python -> Prolog)", command=self.on_analyze)
        btn.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")

        # --- Resultados ---
        box_res = ttk.LabelFrame(self, text="Resultados")
        box_res.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))

        cols = ("enfermedad", "afinidad", "urgencia", "medicamentos", "explicacion")
        self.tree = ttk.Treeview(box_res, columns=cols, show="headings", height=10)
        self.tree.heading("enfermedad", text="Enfermedad")
        self.tree.heading("afinidad", text="% Afinidad")
        self.tree.heading("urgencia", text="Urgencia")
        self.tree.heading("medicamentos", text="Medicamentos seguros")
        self.tree.heading("explicacion", text="Síntomas que coincidieron")

        self.tree.column("enfermedad", width=120)
        self.tree.column("afinidad", width=80)
        self.tree.column("urgencia", width=80)
        self.tree.column("medicamentos", width=220)
        self.tree.column("explicacion", width=220)

        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Layout weights
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def _get_selected_listbox(self, lb: tk.Listbox) -> List[str]:
        out = []
        for idx in lb.curselection():
            out.append(lb.get(idx))
        return out

    def on_analyze(self):
        # Sintomas seleccionados
        selected_symptoms: List[Tuple[str, str]] = []
        for s in SYMPTOMS:
            if self.sym_vars[s].get():
                selected_symptoms.append((s, self.sev_vars[s].get()))

        if not selected_symptoms:
            messagebox.showwarning("Faltan datos", "Selecciona al menos un síntoma.")
            return

        allergies = self._get_selected_listbox(self.allergy_list)
        conditions = self._get_selected_listbox(self.cond_list)

        # Enviar perfil a Prolog (asserts temporales)
        self.engine.set_patient_profile(selected_symptoms, allergies, conditions)

        # Ejecutar diagnóstico completo (usa 5 queries por debajo)
        results = self.engine.full_diagnosis()

        # Pintar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not results:
            messagebox.showinfo("Sin diagnóstico", "No se encontró afinidad con enfermedades registradas.")
            return

        for r in results:
            meds = ", ".join(r.safe_meds) if r.safe_meds else "Ninguno seguro"
            expl = ", ".join(r.matched_symptoms) if r.matched_symptoms else "-"
            self.tree.insert("", tk.END, values=(r.disease, r.affinity, r.urgency, meds, expl))