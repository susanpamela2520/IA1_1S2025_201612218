from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple

from backend.prolog_engine import PrologEngine
from ui.styles import PALETTE


SYMPTOMS = [
    "fiebre", "tos", "dolor_garganta", "congestion_nasal",
    "dolor_cabeza", "dolor_pecho", "fatiga", "nausea",
]
SEVERITIES = ["leve", "moderado", "severo"]

ALLERGIES = ["alergia_aines", "alergia_antihistaminicos"]
CONDITIONS = ["insuficiencia_renal", "gastritis_cronica"]


class PatientView(ttk.Frame):
    def __init__(self, parent: tk.Misc, engine: PrologEngine, app_controller=None):
        super().__init__(parent)
        self.engine = engine
        self.app = app_controller  # opcional para botón volver
        self.sym_vars = {}
        self.sev_vars = {}

        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Topbar
        top = ttk.Frame(self, style="Surface.TFrame")
        top.pack(fill="x", padx=14, pady=14)

        left = ttk.Frame(top, style="Surface.TFrame")
        left.pack(side="left", fill="x", expand=True)

        ttk.Label(left, text="Consulta • Paciente", style="Title.TLabel", background=PALETTE["surface"]).pack(anchor="w")
        ttk.Label(left, text="Selecciona síntomas, severidad y presiona Analizar.", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", pady=(2, 0))

        right = ttk.Frame(top, style="Surface.TFrame")
        right.pack(side="right")

        if self.app is not None:
            ttk.Button(right, text="← Volver", style="Ghost.TButton", command=self.app.show_login).pack()

        # Body grid
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        body.grid_columnconfigure(0, weight=2)
        body.grid_columnconfigure(1, weight=1)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(1, weight=1)

        # Symptoms panel (card)
        sym_card = ttk.Frame(body, style="Surface.TFrame")
        sym_card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10), pady=(0, 10))

        ttk.Label(sym_card, text="Síntomas", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(sym_card, text="Marca y define severidad.", style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        sym_table = ttk.Frame(sym_card, style="Surface.TFrame")
        sym_table.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        for i, s in enumerate(SYMPTOMS):
            v = tk.BooleanVar(value=False)
            self.sym_vars[s] = v

            cb = ttk.Checkbutton(sym_table, text=s, variable=v)
            cb.grid(row=i, column=0, sticky="w", pady=4)

            sev = tk.StringVar(value="leve")
            self.sev_vars[s] = sev
            combo = ttk.Combobox(sym_table, values=SEVERITIES, textvariable=sev, state="readonly", width=12)
            combo.grid(row=i, column=1, sticky="e", padx=(10, 0), pady=4)

        sym_table.grid_columnconfigure(0, weight=1)

        # Allergies card
        all_card = ttk.Frame(body, style="Surface.TFrame")
        all_card.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))
        ttk.Label(all_card, text="Alergias", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(all_card, text="Opcional", style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        self.allergy_list = tk.Listbox(all_card, selectmode=tk.MULTIPLE, height=8, bd=1, highlightthickness=0)
        for a in ALLERGIES:
            self.allergy_list.insert(tk.END, a)
        self.allergy_list.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # Conditions card
        con_card = ttk.Frame(body, style="Surface.TFrame")
        con_card.grid(row=0, column=2, sticky="nsew", pady=(0, 10))
        ttk.Label(con_card, text="Condiciones", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(con_card, text="Opcional", style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        self.cond_list = tk.Listbox(con_card, selectmode=tk.MULTIPLE, height=8, bd=1, highlightthickness=0)
        for c in CONDITIONS:
            self.cond_list.insert(tk.END, c)
        self.cond_list.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # Action bar
        action = ttk.Frame(body, style="Surface.TFrame")
        action.grid(row=1, column=1, columnspan=2, sticky="nsew", pady=(0, 10))
        action.grid_columnconfigure(0, weight=1)

        ttk.Label(action, text="Acción", style="H2.TLabel", background=PALETTE["surface"]).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))
        ttk.Button(action, text="Analizar (Python → Prolog)", style="Primary.TButton", command=self.on_analyze)\
            .grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

        # Results card
        res_card = ttk.Frame(body, style="Surface.TFrame")
        res_card.grid(row=2, column=0, columnspan=3, sticky="nsew")
        body.grid_rowconfigure(2, weight=2)

        ttk.Label(res_card, text="Resultados", style="H2.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 6))
        ttk.Label(res_card, text="Diagnóstico preliminar + explicación.", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        cols = ("enfermedad", "afinidad", "urgencia", "medicamentos", "explicacion")
        self.tree = ttk.Treeview(res_card, columns=cols, show="headings", height=10)
        for c, t in [
            ("enfermedad", "Enfermedad"),
            ("afinidad", "% Afinidad"),
            ("urgencia", "Urgencia"),
            ("medicamentos", "Medicamentos seguros"),
            ("explicacion", "Síntomas que coincidieron"),
        ]:
            self.tree.heading(c, text=t)

        self.tree.column("enfermedad", width=140)
        self.tree.column("afinidad", width=90)
        self.tree.column("urgencia", width=90)
        self.tree.column("medicamentos", width=260)
        self.tree.column("explicacion", width=260)

        self.tree.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def _get_selected(self, lb: tk.Listbox) -> List[str]:
        return [lb.get(i) for i in lb.curselection()]

    def on_analyze(self):
        selected_symptoms: List[Tuple[str, str]] = []
        for s in SYMPTOMS:
            if self.sym_vars[s].get():
                selected_symptoms.append((s, self.sev_vars[s].get()))

        if not selected_symptoms:
            messagebox.showwarning("Faltan datos", "Selecciona al menos un síntoma.")
            return

        allergies = self._get_selected(self.allergy_list)
        conditions = self._get_selected(self.cond_list)

        self.engine.set_patient_profile(selected_symptoms, allergies, conditions)
        results = self.engine.full_diagnosis()

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not results:
            messagebox.showinfo("Sin diagnóstico", "No se encontró afinidad con enfermedades registradas.")
            return

        for r in results:
            meds = ", ".join(r.safe_meds) if r.safe_meds else "Ninguno seguro"
            expl = ", ".join(r.matched_symptoms) if r.matched_symptoms else "-"
            self.tree.insert("", tk.END, values=(r.disease, r.affinity, r.urgency, meds, expl))