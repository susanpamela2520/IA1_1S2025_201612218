from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os

from backend.pl_manager import PLManager, Enfermedad, Medicamento, SISTEMAS, TIPOS
from ui.styles import PALETTE


class AdminView(ttk.Frame):
    def __init__(self, parent, engine, pl_ruta: str, app_controller=None):
        super().__init__(parent)
        self.engine = engine
        self.pl_ruta = pl_ruta
        self.app = app_controller
        self.mgr = PLManager(pl_ruta)
        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Topbar
        top = ttk.Frame(self, style="Surface.TFrame")
        top.pack(fill="x", padx=14, pady=14)

        ttk.Label(top, text="Panel Administrativo", style="Title.TLabel",
                  background=PALETTE["surface"]).pack(side="left", anchor="w")
        ttk.Label(top, text="  •  Gestión de base de conocimiento médica",
                  style="Muted.TLabel", background=PALETTE["surface"]).pack(side="left", anchor="w")

        btn_frame = ttk.Frame(top, style="Surface.TFrame")
        btn_frame.pack(side="right")
        if self.app:
            ttk.Button(btn_frame, text="← Volver", style="Ghost.TButton",
                       command=self.app.show_login).pack(side="right", padx=4)
        ttk.Button(btn_frame, text="💾 Guardar y Recargar", style="Primary.TButton",
                   command=self._guardar_y_recargar).pack(side="right", padx=4)

        # Notebook
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._tab_enfermedades(nb)
        self._tab_medicamentos(nb)
        self._tab_sintomas(nb)
        self._tab_archivo(nb)

    # ----------------------------------------------------------------
    #  TAB 1 — Enfermedades
    # ----------------------------------------------------------------
    def _tab_enfermedades(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="🦠 Enfermedades")
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=3)
        frame.grid_rowconfigure(0, weight=1)

        # Lista izquierda
        left = ttk.Frame(frame, style="Surface.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

        ttk.Label(left, text="Enfermedades registradas", style="H3.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=10, pady=(10,4))

        self.tree_enf = ttk.Treeview(left,
                                      columns=("nombre","sistema","tipo"),
                                      show="headings", height=16)
        for c, t, w in [("nombre","Nombre",130),("sistema","Sistema",110),("tipo","Tipo",90)]:
            self.tree_enf.heading(c, text=t)
            self.tree_enf.column(c, width=w)
        self.tree_enf.pack(fill="both", expand=True, padx=10, pady=(0,6))
        self.tree_enf.bind("<<TreeviewSelect>>", self._on_select_enf)

        btn_row = ttk.Frame(left, style="Surface.TFrame")
        btn_row.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(btn_row, text="+ Nueva", style="Primary.TButton",
                   command=self._nueva_enfermedad).pack(side="left", padx=(0,4))
        ttk.Button(btn_row, text="✏ Editar", style="Ghost.TButton",
                   command=self._editar_enfermedad).pack(side="left", padx=(0,4))
        ttk.Button(btn_row, text="🗑 Eliminar", style="Danger.TButton",
                   command=self._eliminar_enfermedad).pack(side="left")

        # Formulario derecha
        right = ttk.Frame(frame, style="Surface.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)

        ttk.Label(right, text="Detalle / Edición", style="H3.TLabel",
                  background=PALETTE["surface"]).grid(row=0, column=0, columnspan=2,
                  sticky="w", padx=12, pady=(12,8))

        campos = [("Nombre:", "enf_nombre"), ("Descripción:", "enf_desc"),
                  ("Sistema:", None),       ("Tipo:", None)]
        self._enf_vars = {}
        for i, (lbl, key) in enumerate(campos):
            ttk.Label(right, text=lbl, background=PALETTE["surface"])\
                .grid(row=i+1, column=0, sticky="w", padx=12, pady=4)
            if key:
                v = tk.StringVar()
                self._enf_vars[key] = v
                ttk.Entry(right, textvariable=v, width=30)\
                    .grid(row=i+1, column=1, sticky="ew", padx=(0,12), pady=4)
            elif lbl == "Sistema:":
                v = tk.StringVar(value=SISTEMAS[0])
                self._enf_vars["enf_sistema"] = v
                ttk.Combobox(right, textvariable=v, values=SISTEMAS,
                             state="readonly", width=28)\
                    .grid(row=i+1, column=1, sticky="ew", padx=(0,12), pady=4)
            else:
                v = tk.StringVar(value=TIPOS[0])
                self._enf_vars["enf_tipo"] = v
                ttk.Combobox(right, textvariable=v, values=TIPOS,
                             state="readonly", width=28)\
                    .grid(row=i+1, column=1, sticky="ew", padx=(0,12), pady=4)

        right.grid_columnconfigure(1, weight=1)

        # Sub-tabla síntomas de la enfermedad
        ttk.Label(right, text="Síntomas asociados (peso 1-5):", style="H3.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=6, column=0, columnspan=2, sticky="w", padx=12, pady=(16,4))

        self.tree_sint_enf = ttk.Treeview(right, columns=("sintoma","peso"),
                                           show="headings", height=6)
        self.tree_sint_enf.heading("sintoma", text="Síntoma")
        self.tree_sint_enf.heading("peso",    text="Peso")
        self.tree_sint_enf.column("sintoma", width=160)
        self.tree_sint_enf.column("peso",    width=60)
        self.tree_sint_enf.grid(row=7, column=0, columnspan=2,
                                 sticky="nsew", padx=12, pady=(0,4))

        sint_btn = ttk.Frame(right, style="Surface.TFrame")
        sint_btn.grid(row=8, column=0, columnspan=2, sticky="w", padx=12, pady=(0,10))
        ttk.Button(sint_btn, text="+ Agregar síntoma", style="Ghost.TButton",
                   command=self._agregar_sintoma_enf).pack(side="left", padx=(0,4))
        ttk.Button(sint_btn, text="🗑 Quitar", style="Danger.TButton",
                   command=self._quitar_sintoma_enf).pack(side="left")

        self._refresh_tree_enf()

    def _refresh_tree_enf(self):
        self.tree_enf.delete(*self.tree_enf.get_children())
        for e in self.mgr.enfermedades.values():
            self.tree_enf.insert("", tk.END, iid=e.nombre,
                                  values=(e.nombre, e.sistema, e.tipo))

    def _on_select_enf(self, _event=None):
        sel = self.tree_enf.selection()
        if not sel:
            return
        nombre = sel[0]
        e = self.mgr.enfermedades.get(nombre)
        if not e:
            return
        self._enf_vars["enf_nombre"].set(e.nombre)
        self._enf_vars["enf_desc"].set(e.descripcion)
        self._enf_vars["enf_sistema"].set(e.sistema)
        self._enf_vars["enf_tipo"].set(e.tipo)
        self.tree_sint_enf.delete(*self.tree_sint_enf.get_children())
        for s, p in e.sintomas:
            self.tree_sint_enf.insert("", tk.END, values=(s, p))

    def _nueva_enfermedad(self):
        for k, v in self._enf_vars.items():
            v.set("" if "nombre" in k or "desc" in k else (SISTEMAS[0] if "sistema" in k else TIPOS[0]))
        self.tree_sint_enf.delete(*self.tree_sint_enf.get_children())
        self.tree_enf.selection_remove(*self.tree_enf.selection())

    def _editar_enfermedad(self):
        """Guarda enfermedad en memoria, escribe el .pl y recarga Prolog."""
        nombre = self._enf_vars["enf_nombre"].get().strip().lower().replace(" ", "_")
        desc   = self._enf_vars["enf_desc"].get().strip()
        sistema= self._enf_vars["enf_sistema"].get()
        tipo   = self._enf_vars["enf_tipo"].get()

        if not nombre:
            messagebox.showwarning("Error", "El nombre no puede estar vacío.")
            return

        sintomas = []
        for item in self.tree_sint_enf.get_children():
            s, p = self.tree_sint_enf.item(item, "values")
            sintomas.append((s, int(p)))

        sel = self.tree_enf.selection()
        nombre_viejo = sel[0] if sel else None

        nueva = Enfermedad(nombre, desc, sistema, tipo, sintomas)
        if nombre_viejo and nombre_viejo != nombre:
            self.mgr.editar_enfermedad(nombre_viejo, nueva)
        else:
            self.mgr.agregar_enfermedad(nueva)

        # Guardar al disco y recargar motor
        self._guardar_y_recargar()

    def _eliminar_enfermedad(self):
        sel = self.tree_enf.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona una enfermedad.")
            return
        nombre = sel[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
            self.mgr.eliminar_enfermedad(nombre)
            self._refresh_tree_enf()
            self.tree_sint_enf.delete(*self.tree_sint_enf.get_children())

    def _agregar_sintoma_enf(self):
        catalogo = self.mgr.sintomas_catalogo
        dial = _SintomaDialog(self, catalogo)
        self.wait_window(dial)
        if dial.resultado:
            s, p = dial.resultado
            self.tree_sint_enf.insert("", tk.END, values=(s, p))

    def _quitar_sintoma_enf(self):
        sel = self.tree_sint_enf.selection()
        if sel:
            self.tree_sint_enf.delete(sel[0])

    # ----------------------------------------------------------------
    #  TAB 2 — Medicamentos
    # ----------------------------------------------------------------
    def _tab_medicamentos(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="💊 Medicamentos")
        frame.grid_columnconfigure(0, weight=2)
        frame.grid_columnconfigure(1, weight=3)
        frame.grid_rowconfigure(0, weight=1)

        left = ttk.Frame(frame, style="Surface.TFrame")
        left.grid(row=0, column=0, sticky="nsew", padx=(10,5), pady=10)

        ttk.Label(left, text="Medicamentos registrados", style="H3.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=10, pady=(10,4))

        self.tree_med = ttk.Treeview(left, columns=("nombre",), show="headings", height=16)
        self.tree_med.heading("nombre", text="Medicamento")
        self.tree_med.column("nombre", width=180)
        self.tree_med.pack(fill="both", expand=True, padx=10, pady=(0,6))
        self.tree_med.bind("<<TreeviewSelect>>", self._on_select_med)

        btn_row = ttk.Frame(left, style="Surface.TFrame")
        btn_row.pack(fill="x", padx=10, pady=(0,10))
        ttk.Button(btn_row, text="+ Nuevo", style="Primary.TButton",
                   command=self._nuevo_medicamento).pack(side="left", padx=(0,4))
        ttk.Button(btn_row, text="💾 Guardar", style="Ghost.TButton",
                   command=self._guardar_medicamento).pack(side="left", padx=(0,4))
        ttk.Button(btn_row, text="🗑 Eliminar", style="Danger.TButton",
                   command=self._eliminar_medicamento).pack(side="left")

        # Formulario
        right = ttk.Frame(frame, style="Surface.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(5,10), pady=10)
        right.grid_columnconfigure(1, weight=1)

        ttk.Label(right, text="Detalle del medicamento", style="H3.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12,8))

        self._med_nombre_var = tk.StringVar()
        ttk.Label(right, text="Nombre:", background=PALETTE["surface"])\
            .grid(row=1, column=0, sticky="w", padx=12, pady=4)
        ttk.Entry(right, textvariable=self._med_nombre_var, width=28)\
            .grid(row=1, column=1, sticky="ew", padx=(0,12), pady=4)

        # Trata
        ttk.Label(right, text="Trata enfermedades:", style="H3.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=2, column=0, columnspan=2, sticky="w", padx=12, pady=(12,4))
        self.list_trata = tk.Listbox(right, selectmode=tk.MULTIPLE, height=5,
                                      bd=1, highlightthickness=0)
        self.list_trata.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0,4))

        # Contra-alergias
        ttk.Label(right, text="Contraindicado con alergias:", style="H3.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=4, column=0, columnspan=2, sticky="w", padx=12, pady=(12,4))
        self._med_contra_a_var = tk.StringVar()
        ttk.Entry(right, textvariable=self._med_contra_a_var, width=40)\
            .grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=(0,4))
        ttk.Label(right, text="(separar con comas)", style="Muted.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=6, column=0, columnspan=2, sticky="w", padx=12)

        # Contra-condiciones
        ttk.Label(right, text="Contraindicado con condiciones:", style="H3.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=7, column=0, columnspan=2, sticky="w", padx=12, pady=(12,4))
        self._med_contra_c_var = tk.StringVar()
        ttk.Entry(right, textvariable=self._med_contra_c_var, width=40)\
            .grid(row=8, column=0, columnspan=2, sticky="ew", padx=12, pady=(0,12))
        ttk.Label(right, text="(separar con comas)", style="Muted.TLabel",
                  background=PALETTE["surface"])\
            .grid(row=9, column=0, columnspan=2, sticky="w", padx=12)

        self._refresh_tree_med()
        self._refresh_list_trata()

    def _refresh_tree_med(self):
        self.tree_med.delete(*self.tree_med.get_children())
        for m in self.mgr.medicamentos.values():
            self.tree_med.insert("", tk.END, iid=m.nombre, values=(m.nombre,))

    def _refresh_list_trata(self):
        self.list_trata.delete(0, tk.END)
        for e in self.mgr.enfermedades:
            self.list_trata.insert(tk.END, e)

    def _on_select_med(self, _=None):
        sel = self.tree_med.selection()
        if not sel:
            return
        m = self.mgr.medicamentos.get(sel[0])
        if not m:
            return
        self._med_nombre_var.set(m.nombre)
        self._med_contra_a_var.set(", ".join(m.contra_alergia))
        self._med_contra_c_var.set(", ".join(m.contra_condicion))
        # Seleccionar enfermedades que trata
        self.list_trata.selection_clear(0, tk.END)
        for i in range(self.list_trata.size()):
            if self.list_trata.get(i) in m.trata:
                self.list_trata.selection_set(i)

    def _nuevo_medicamento(self):
        self._med_nombre_var.set("")
        self._med_contra_a_var.set("")
        self._med_contra_c_var.set("")
        self.list_trata.selection_clear(0, tk.END)
        self.tree_med.selection_remove(*self.tree_med.selection())

    def _guardar_medicamento(self):
        nombre = self._med_nombre_var.get().strip().lower().replace(" ", "_")
        if not nombre:
            messagebox.showwarning("Error", "El nombre no puede estar vacío.")
            return
        trata  = [self.list_trata.get(i) for i in self.list_trata.curselection()]
        ca = [x.strip() for x in self._med_contra_a_var.get().split(",") if x.strip()]
        cc = [x.strip() for x in self._med_contra_c_var.get().split(",") if x.strip()]

        sel = self.tree_med.selection()
        nombre_viejo = sel[0] if sel else None
        nuevo = Medicamento(nombre, trata, ca, cc)
        if nombre_viejo and nombre_viejo != nombre:
            self.mgr.editar_medicamento(nombre_viejo, nuevo)
        else:
            self.mgr.agregar_medicamento(nuevo)

        self._guardar_y_recargar()

    def _eliminar_medicamento(self):
        sel = self.tree_med.selection()
        if not sel:
            messagebox.showwarning("Selecciona", "Selecciona un medicamento.")
            return
        nombre = sel[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
            self.mgr.eliminar_medicamento(nombre)
            self._refresh_tree_med()

    # ----------------------------------------------------------------
    #  TAB 3 — Catálogo de Síntomas
    # ----------------------------------------------------------------
    def _tab_sintomas(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="🔬 Síntomas")

        card = ttk.Frame(frame, style="Surface.TFrame")
        card.pack(fill="both", expand=True, padx=14, pady=14)

        ttk.Label(card, text="Catálogo de síntomas del sistema", style="H3.TLabel",
                  background=PALETTE["surface"]).pack(anchor="w", padx=12, pady=(12,4))
        ttk.Label(card,
                  text="Estos síntomas aparecen en el módulo de pacientes como opciones de selección.",
                  style="Muted.TLabel", background=PALETTE["surface"])\
            .pack(anchor="w", padx=12, pady=(0,10))

        self.list_sint_cat = tk.Listbox(card, height=14, bd=1, highlightthickness=0)
        self.list_sint_cat.pack(fill="both", expand=True, padx=12, pady=(0,8))

        row = ttk.Frame(card, style="Surface.TFrame")
        row.pack(fill="x", padx=12, pady=(0,12))
        self._sint_nuevo_var = tk.StringVar()
        ttk.Entry(row, textvariable=self._sint_nuevo_var, width=22)\
            .pack(side="left", padx=(0,6))
        ttk.Button(row, text="+ Agregar", style="Primary.TButton",
                   command=self._agregar_sint_cat).pack(side="left", padx=(0,4))
        ttk.Button(row, text="🗑 Quitar seleccionado", style="Danger.TButton",
                   command=self._quitar_sint_cat).pack(side="left")

        self._refresh_list_sint_cat()

    def _refresh_list_sint_cat(self):
        self.list_sint_cat.delete(0, tk.END)
        for s in sorted(self.mgr.sintomas_catalogo):
            self.list_sint_cat.insert(tk.END, s)

    def _agregar_sint_cat(self):
        nombre = self._sint_nuevo_var.get().strip().lower().replace(" ", "_")
        if not nombre:
            return
        self.mgr.agregar_sintoma_catalogo(nombre)
        self._sint_nuevo_var.set("")
        self._refresh_list_sint_cat()

    def _quitar_sint_cat(self):
        sel = self.list_sint_cat.curselection()
        if not sel:
            return
        nombre = self.list_sint_cat.get(sel[0])
        if messagebox.askyesno("Confirmar",
                                f"¿Quitar '{nombre}' del catálogo?\n"
                                "(se eliminará de todas las enfermedades)"):
            self.mgr.eliminar_sintoma_catalogo(nombre)
            self._refresh_list_sint_cat()

    # ----------------------------------------------------------------
    #  TAB 4 — Archivo .pl
    # ----------------------------------------------------------------
    def _tab_archivo(self, nb):
        frame = ttk.Frame(nb)
        nb.add(frame, text="📄 Archivo .pl")

        card = ttk.Frame(frame, style="Surface.TFrame")
        card.pack(fill="both", expand=True, padx=14, pady=14)

        btn_row = ttk.Frame(card, style="Surface.TFrame")
        btn_row.pack(fill="x", padx=12, pady=(12,8))
        ttk.Button(btn_row, text="🔄 Refrescar vista", style="Ghost.TButton",
                   command=self._refrescar_vista_pl).pack(side="left", padx=(0,6))
        ttk.Button(btn_row, text="📥 Cargar .pl externo", style="Ghost.TButton",
                   command=self._cargar_pl_externo).pack(side="left", padx=(0,6))
        ttk.Button(btn_row, text="💾 Exportar copia", style="Ghost.TButton",
                   command=self._exportar_pl).pack(side="left")

        self.txt_pl = tk.Text(card, font=("Consolas", 9), wrap="none",
                               bd=1, relief="solid")
        scroll_y = ttk.Scrollbar(card, command=self.txt_pl.yview)
        scroll_x = ttk.Scrollbar(card, orient="horizontal",
                                  command=self.txt_pl.xview)
        self.txt_pl.configure(yscrollcommand=scroll_y.set,
                               xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.txt_pl.pack(fill="both", expand=True, padx=(12,0), pady=(0,12))
        self._refrescar_vista_pl()

    def _refrescar_vista_pl(self):
        if os.path.exists(self.pl_ruta):
            with open(self.pl_ruta, encoding="utf-8") as f:
                contenido = f.read()
            self.txt_pl.config(state="normal")
            self.txt_pl.delete("1.0", tk.END)
            self.txt_pl.insert("1.0", contenido)
            self.txt_pl.config(state="disabled")

    def _cargar_pl_externo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo .pl",
            filetypes=[("Prolog files", "*.pl"), ("All files", "*.*")]
        )
        if not ruta:
            return
        import shutil
        shutil.copy(ruta, self.pl_ruta)
        self.mgr = PLManager(self.pl_ruta)
        self.mgr = PLManager(self.pl_ruta)
        self._guardar_y_recargar(silent=True)
        messagebox.showinfo("Listo", "Archivo .pl cargado y motor recargado.")

    def _exportar_pl(self):
        ruta = filedialog.asksaveasfilename(
            title="Exportar .pl",
            defaultextension=".pl",
            filetypes=[("Prolog files", "*.pl")]
        )
        if ruta:
            import shutil
            shutil.copy(self.pl_ruta, ruta)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")

    def _guardar_y_recargar(self, silent=False):
        # Paso 1: guardar .pl en disco
        try:
            self.mgr.guardar()
        except Exception as ex:
            messagebox.showerror("ERROR paso 1 - guardar disco",
                f"Fallo al escribir el archivo:\n{ex}")
            return

        # Paso 2: recargar Prolog (no detener flujo si falla)
        try:
            self.engine.recargar()
        except Exception as ex:
            messagebox.showwarning("AVISO paso 2 - Prolog",
                f"Archivo guardado OK. Prolog reporto:\n{ex}")

        # Paso 3: DEBUG - mostrar que hay en mgr
        n = len(self.mgr.enfermedades)
        nombres = list(self.mgr.enfermedades.keys())
        messagebox.showinfo("DEBUG enfermedades en mgr",
            f"Total en memoria: {n}\nLista: {nombres}")

        # Paso 4: refrescar UI
        self._refresh_tree_enf()
        self._refresh_tree_med()
        self._refresh_list_trata()
        self._refresh_list_sint_cat()
        self._refrescar_vista_pl()
        self.update_idletasks()

        if not silent:
            messagebox.showinfo("Listo",
                "Guardado y recargado correctamente.")

# ----------------------------------------------------------------
#  Diálogo auxiliar para agregar síntoma con peso
# ----------------------------------------------------------------
class _SintomaDialog(tk.Toplevel):
    def __init__(self, parent, catalogo):
        super().__init__(parent)
        self.title("Agregar síntoma")
        self.resizable(False, False)
        self.resultado = None
        self.transient(parent)
        self.grab_set()

        ttk.Label(self, text="Síntoma:").grid(row=0, column=0, padx=12, pady=8, sticky="w")
        self._sint = tk.StringVar(value=catalogo[0] if catalogo else "")
        ttk.Combobox(self, textvariable=self._sint, values=catalogo,
                     state="readonly", width=22)\
            .grid(row=0, column=1, padx=(0,12), pady=8)

        ttk.Label(self, text="Peso (1-5):").grid(row=1, column=0, padx=12, sticky="w")
        self._peso = tk.IntVar(value=3)
        ttk.Spinbox(self, from_=1, to=5, textvariable=self._peso, width=8)\
            .grid(row=1, column=1, padx=(0,12), pady=4, sticky="w")

        btn = ttk.Frame(self)
        btn.grid(row=2, column=0, columnspan=2, pady=12)
        ttk.Button(btn, text="Agregar", style="Primary.TButton",
                   command=self._ok).pack(side="left", padx=6)
        ttk.Button(btn, text="Cancelar", style="Ghost.TButton",
                   command=self.destroy).pack(side="left")

    def _ok(self):
        self.resultado = (self._sint.get(), self._peso.get())
        self.destroy()