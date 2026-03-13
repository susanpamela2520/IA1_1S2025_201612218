from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple
import datetime

from backend.prolog_engine import PrologEngine, ResultadoDiagnostico
from ui.styles import PALETTE

# Catálogo completo de síntomas disponibles
SYMPTOMS = [
    "fiebre", "tos", "dolor_garganta", "congestion_nasal",
    "dolor_cabeza", "dolor_pecho", "fatiga", "nausea",
    "vomito", "diarrea",
]
SEVERITIES = ["leve", "moderado", "severo"]

ALLERGIES = [
    "alergia_aines",
    "alergia_antihistaminicos",
    "alergia_penicilina",
]
CONDITIONS = [
    "insuficiencia_renal",
    "gastritis_cronica",
    "insuficiencia_hepatica",
    "diabetes",
    "hipertension",
]

# Mapa urgencia interna → frase oficial del enunciado
URGENCIA_FRASE = {
    "alta":  "Consulta médica inmediata sugerida",
    "media": "Observación recomendada",
    "baja":  "Posible automanejo",
}
URGENCIA_COLOR = {
    "alta":  PALETTE["urgent_a"],
    "media": PALETTE["urgent_m"],
    "baja":  PALETTE["urgent_b"],
}


class PatientView(ttk.Frame):
    def __init__(self, parent: tk.Misc, engine: PrologEngine, app_controller=None):
        super().__init__(parent)
        self.engine = engine
        self.app = app_controller
        self.sym_vars: dict[str, tk.BooleanVar] = {}
        self.sev_vars: dict[str, tk.StringVar] = {}
        self._historial: list[dict] = []   # diagnósticos de la sesión
        self._ultimo_resultados: list[ResultadoDiagnostico] = []

        self._build_ui()

    # ------------------------------------------------------------------
    #  Construcción de la UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Topbar
        top = ttk.Frame(self, style="Surface.TFrame")
        top.pack(fill="x", padx=14, pady=10)

        left = ttk.Frame(top, style="Surface.TFrame")
        left.pack(side="left", fill="x", expand=True)
        ttk.Label(left, text="MediLogic  •  Consulta del Paciente",
                  style="Title.TLabel", background=PALETTE["surface"]).pack(anchor="w")
        ttk.Label(left,
                  text="Ingresa tus síntomas con severidad, alergias y condiciones crónicas.",
                  style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", pady=(2, 0))

        right = ttk.Frame(top, style="Surface.TFrame")
        right.pack(side="right")
        if self.app:
            ttk.Button(right, text="← Volver", style="Ghost.TButton",
                       command=self.app.show_login).pack(side="right", padx=4)
        ttk.Button(right, text="📋 Historial de sesión", style="Ghost.TButton",
                   command=self._mostrar_historial).pack(side="right", padx=4)

        # Notebook principal
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._tab_formulario(nb)
        self._tab_resultados(nb)

    # ---- Tab 1: Formulario ------------------------------------------------
    def _tab_formulario(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="📝 Formulario de síntomas")
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # --- Síntomas ---
        sym_card = ttk.Frame(frame, style="Surface.TFrame")
        sym_card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(8, 5), pady=8)

        ttk.Label(sym_card, text="Síntomas", style="H2.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(14, 2))
        ttk.Label(sym_card, text="Marca los que presentas e indica severidad.",
                  style="Muted.TLabel", background=PALETTE["surface"]).pack(anchor="w", padx=14, pady=(0, 10))

        sym_table = ttk.Frame(sym_card, style="Surface.TFrame")
        sym_table.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        for i, s in enumerate(SYMPTOMS):
            v = tk.BooleanVar(value=False)
            self.sym_vars[s] = v
            ttk.Checkbutton(sym_table, text=s.replace("_", " ").capitalize(),
                             variable=v).grid(row=i, column=0, sticky="w", pady=3)
            sev = tk.StringVar(value="leve")
            self.sev_vars[s] = sev
            ttk.Combobox(sym_table, values=SEVERITIES, textvariable=sev,
                          state="readonly", width=11).grid(row=i, column=1,
                          sticky="e", padx=(10, 0), pady=3)

        sym_table.grid_columnconfigure(0, weight=1)

        # --- Alergias ---
        all_card = ttk.Frame(frame, style="Surface.TFrame")
        all_card.grid(row=0, column=1, sticky="nsew", padx=(0, 5), pady=8)
        ttk.Label(all_card, text="Alergias", style="H2.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=12, pady=(12, 4))
        ttk.Label(all_card, text="Selecciona las que tengas.", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=12, pady=(0, 8))
        self.allergy_list = tk.Listbox(all_card, selectmode=tk.MULTIPLE, height=7,
                                        bd=1, highlightthickness=0)
        for a in ALLERGIES:
            self.allergy_list.insert(tk.END, a.replace("_", " "))
        self.allergy_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # --- Condiciones ---
        con_card = ttk.Frame(frame, style="Surface.TFrame")
        con_card.grid(row=0, column=2, sticky="nsew", padx=(0, 8), pady=8)
        ttk.Label(con_card, text="Condiciones crónicas", style="H2.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=12, pady=(12, 4))
        ttk.Label(con_card, text="Enfermedades preexistentes.", style="Muted.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=12, pady=(0, 8))
        self.cond_list = tk.Listbox(con_card, selectmode=tk.MULTIPLE, height=7,
                                     bd=1, highlightthickness=0)
        for c in CONDITIONS:
            self.cond_list.insert(tk.END, c.replace("_", " "))
        self.cond_list.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # --- Botón analizar ---
        action = ttk.Frame(frame, style="Surface.TFrame")
        action.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=(0, 8), pady=8)
        ttk.Label(action, text="Cuando estés listo:", style="H3.TLabel",
                  background=PALETTE["surface"]).pack(padx=12, pady=(12, 6))
        ttk.Button(action, text="🔍  Analizar síntomas  →  Prolog",
                   style="Primary.TButton", command=self.on_analyze).pack(
                   fill="x", padx=12, pady=(0, 14), ipady=6)
        ttk.Label(action,
                  text="⚕ Este sistema es de orientación médica\ny no sustituye al médico.",
                  style="Muted.TLabel", background=PALETTE["surface"],
                  justify="center").pack(padx=12)

    # ---- Tab 2: Resultados ------------------------------------------------
    def _tab_resultados(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="📊 Diagnóstico y resultados")
        self._resultados_frame = frame
        self._nb = nb

        # Cabecera de resultados
        top = ttk.Frame(frame, style="Surface.TFrame")
        top.pack(fill="x", padx=10, pady=(10, 4))
        ttk.Label(top, text="Informe de Diagnóstico Preliminar",
                  style="H2.TLabel", background=PALETTE["surface"]).pack(side="left", padx=10)
        ttk.Button(top, text="📄 Exportar PDF", style="Ghost.TButton",
                   command=self._exportar_pdf).pack(side="right", padx=10)

        # Canvas scrolleable para tarjetas de resultados
        container = ttk.Frame(frame)
        container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._canvas_res = tk.Canvas(container, bg=PALETTE["bg"],
                                      highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                   command=self._canvas_res.yview)
        self._canvas_res.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._canvas_res.pack(side="left", fill="both", expand=True)

        self._res_inner = ttk.Frame(self._canvas_res)
        self._canvas_win = self._canvas_res.create_window(
            (0, 0), window=self._res_inner, anchor="nw"
        )
        self._res_inner.bind("<Configure>", self._on_inner_configure)
        self._canvas_res.bind("<Configure>", self._on_canvas_configure)

        # Mensaje inicial
        ttk.Label(self._res_inner,
                  text="Completa el formulario y presiona 'Analizar' para ver el diagnóstico.",
                  style="Muted.TLabel").pack(pady=40)

    def _on_inner_configure(self, _event):
        self._canvas_res.configure(
            scrollregion=self._canvas_res.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas_res.itemconfig(self._canvas_win, width=event.width)

    
    #Aqui inicia la logica del analisis principal 
   
    def on_analyze(self):
        selected_symptoms: List[Tuple[str, str]] = [
            (s, self.sev_vars[s].get())
            for s in SYMPTOMS if self.sym_vars[s].get()
        ]
        if not selected_symptoms:
            messagebox.showwarning("Faltan datos",
                                   "Selecciona al menos un síntoma.")
            return

        # Alergias y condiciones con nombres internos (con guión bajo)
        allergies = [ALLERGIES[i] for i in self.allergy_list.curselection()]
        conditions = [CONDITIONS[i] for i in self.cond_list.curselection()]

        try:
            self.engine.cargar_perfil_paciente(
                selected_symptoms, allergies, conditions)
            resultados = self.engine.diagnostico_completo()
        except Exception as ex:
            messagebox.showerror("Error Prolog",
                                  f"No se pudo ejecutar el análisis:\n{ex}")
            return

        if not resultados:
            messagebox.showinfo(
                "Sin resultados",
                "No se encontró afinidad con enfermedades registradas.\n"
                "Intenta agregar más síntomas.")
            return

        self._ultimo_resultados = resultados

        # Guardar en historial de sesión
        self._historial.append({
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
            "sintomas":  [(s, sv) for s, sv in selected_symptoms],
            "alergias":  allergies,
            "condiciones": conditions,
            "resultados": resultados,
        })

        self._render_resultados(resultados)
        # Ir al tab de resultados
        self._nb.select(1)

    # ------------------------------------------------------------------
    #  Renderizado visual de resultados
    # ------------------------------------------------------------------
    def _render_resultados(self, resultados: list[ResultadoDiagnostico]):
        # Limpiar inner frame
        for w in self._res_inner.winfo_children():
            w.destroy()

        for idx, r in enumerate(resultados):
            self._render_tarjeta(r, idx)

    def _render_tarjeta(self, r: ResultadoDiagnostico, idx: int):
        """Renderiza una tarjeta visual para cada enfermedad."""
        urgencia_key = r.urgencia
        color_urg   = URGENCIA_COLOR.get(urgencia_key, PALETTE["muted"])
        frase_urg   = URGENCIA_FRASE.get(urgencia_key, r.urgencia)

        # Marco de la tarjeta con borde de color según urgencia
        outer = tk.Frame(self._res_inner, bg=color_urg, pady=2)
        outer.pack(fill="x", padx=10, pady=(8, 0))

        card = ttk.Frame(outer, style="Surface.TFrame")
        card.pack(fill="x", padx=2, pady=(0, 2))

        # Fila superior: nombre + urgencia
        header = ttk.Frame(card, style="Surface.TFrame")
        header.pack(fill="x", padx=14, pady=(12, 4))

        ttk.Label(header,
                  text=f"#{idx+1}  {r.enfermedad.upper().replace('_', ' ')}",
                  style="H2.TLabel",
                  background=PALETTE["surface"]).pack(side="left")

        # Badge urgencia
        tk.Label(header, text=frase_urg,
                 bg=color_urg, fg="white",
                 font=("Segoe UI", 9, "bold"),
                 padx=10, pady=3).pack(side="right")

        # Barra de afinidad
        bar_frame = ttk.Frame(card, style="Surface.TFrame")
        bar_frame.pack(fill="x", padx=14, pady=(4, 8))

        ttk.Label(bar_frame, text="Afinidad:",
                  background=PALETTE["surface"],
                  font=("Segoe UI", 9)).pack(side="left")

        # Canvas barra de progreso
        bar_w = 340
        bar_h = 18
        cvs = tk.Canvas(bar_frame, width=bar_w, height=bar_h,
                         bg=PALETTE["border"], highlightthickness=0)
        cvs.pack(side="left", padx=(8, 4))
        fill_w = int(bar_w * r.afinidad / 100)
        cvs.create_rectangle(0, 0, fill_w, bar_h,
                               fill=color_urg, outline="")

        ttk.Label(bar_frame,
                  text=f"{r.afinidad}%",
                  background=PALETTE["surface"],
                  font=("Segoe UI", 10, "bold")).pack(side="left")

        # Separador
        ttk.Separator(card, orient="horizontal").pack(fill="x", padx=14)

        # Fila de detalles
        details = ttk.Frame(card, style="Surface.TFrame")
        details.pack(fill="x", padx=14, pady=8)

        # Medicamentos seguros
        meds_txt = ", ".join(r.medicamentos) if r.medicamentos else "Ninguno disponible"
        self._detail_row(details, " Medicamentos seguros:", meds_txt)

        # Síntomas que coincidieron
        sint_txt = ", ".join(r.sintomas_coincidentes) if r.sintomas_coincidentes else "-"
        self._detail_row(details, " Reglas Prolog activadas (síntomas):", sint_txt)

        # Descripción de las reglas activadas
        reglas = self._explicar_reglas(r)
        self._detail_row(details, " Inferencia lógica aplicada:", reglas)

    def _detail_row(self, parent, label: str, value: str):
        row = ttk.Frame(parent, style="Surface.TFrame")
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label,
                  background=PALETTE["surface"],
                  font=("Segoe UI", 9, "bold")).pack(side="left", anchor="n")
        ttk.Label(row, text="  " + value,
                  background=PALETTE["surface"],
                  font=("Segoe UI", 9),
                  wraplength=600, justify="left").pack(side="left", anchor="n")

    def _explicar_reglas(self, r: ResultadoDiagnostico) -> str:
        """Genera una explicación textual de las reglas Prolog que se activaron."""
        partes = []
        if r.sintomas_coincidentes:
            partes.append(
                f"sintomas_coincidentes/2 activado para: "
                f"{', '.join(r.sintomas_coincidentes)}"
            )
        partes.append(
            f"porcentaje_afinidad/2 → {r.afinidad}%  |  "
            f"nivel_urgencia/2 → {r.urgencia}"
        )
        if r.medicamentos:
            partes.append(
                f"medicamento_seguro_para/2 → {', '.join(r.medicamentos)}"
            )
        else:
            partes.append("medicamento_inseguro/1 activado (todas contraindicadas)")
        return "  /  ".join(partes)

    # ------------------------------------------------------------------
    #  Historial de sesión
    # ------------------------------------------------------------------
    def _mostrar_historial(self):
        if not self._historial:
            messagebox.showinfo("Historial", "No hay diagnósticos en esta sesión todavía.")
            return

        win = tk.Toplevel(self)
        win.title("Historial de diagnósticos — sesión actual")
        win.geometry("720x500")
        win.configure(bg=PALETTE["bg"])

        ttk.Label(win, text="Historial de la sesión",
                  style="H2.TLabel").pack(anchor="w", padx=14, pady=(14, 4))
        ttk.Label(win,
                  text="Los diagnósticos se borran al cerrar la aplicación.",
                  style="Muted.TLabel").pack(anchor="w", padx=14, pady=(0, 10))

        cols = ("hora", "sintomas", "top_dx", "afinidad")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=18)
        tree.heading("hora",     text="Hora")
        tree.heading("sintomas", text="Síntomas ingresados")
        tree.heading("top_dx",   text="Diagnóstico principal")
        tree.heading("afinidad", text="Afinidad")
        tree.column("hora",     width=70)
        tree.column("sintomas", width=280)
        tree.column("top_dx",   width=160)
        tree.column("afinidad", width=80)
        tree.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        for entrada in reversed(self._historial):
            top = entrada["resultados"][0] if entrada["resultados"] else None
            sint_str = ", ".join(f"{s}({sv})" for s, sv in entrada["sintomas"])
            tree.insert("", tk.END, values=(
                entrada["timestamp"],
                sint_str,
                top.enfermedad if top else "-",
                f"{top.afinidad}%" if top else "-",
            ))

    # ------------------------------------------------------------------
    #  Exportar PDF
    # ------------------------------------------------------------------
    def _exportar_pdf(self):
        if not self._ultimo_resultados:
            messagebox.showwarning("Sin datos", "Ejecuta un análisis primero.")
            return
        try:
            from backend.pdf_generator import generar_informe_pdf
            from tkinter.filedialog import asksaveasfilename
            ruta = asksaveasfilename(
                title="Guardar informe PDF",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile=f"MediLogic_Informe_{datetime.date.today()}.pdf",
            )
            if not ruta:
                return
            generar_informe_pdf(self._ultimo_resultados, ruta)
            messagebox.showinfo("PDF generado", f"Informe guardado en:\n{ruta}")
        except ImportError:
            messagebox.showerror(
                "Dependencia faltante",
                "Instala reportlab para generar PDF:\n  pip install reportlab"
            )
        except Exception as ex:
            messagebox.showerror("Error PDF", str(ex))

    def _get_selected(self, lb: tk.Listbox) -> List[str]:
        return [lb.get(i) for i in lb.curselection()]
