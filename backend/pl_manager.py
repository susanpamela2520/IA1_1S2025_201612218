"""
backend/pl_manager.py
Gestor del archivo .pl — permite leer y escribir la base de conocimiento
sin editar el archivo manualmente.
Usado por el módulo Administrador.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import re, os, shutil, datetime


@dataclass
class Enfermedad:
    nombre: str
    descripcion: str
    sistema: str      # respiratorio | digestivo | endocrino | neurologico | inmunologico
    tipo: str         # viral | bacteriano | cronico | agudo | inmunologico
    sintomas: List[Tuple[str, int]] = field(default_factory=list)   # [(nombre, peso), ...]


@dataclass
class Medicamento:
    nombre: str
    trata: List[str] = field(default_factory=list)             # enfermedades que trata
    contra_alergia: List[str] = field(default_factory=list)    # alergias que lo contraindican
    contra_condicion: List[str] = field(default_factory=list)  # condiciones que lo contraindican


SISTEMAS = ["respiratorio", "digestivo", "endocrino", "neurologico", "inmunologico"]
TIPOS    = ["viral", "bacteriano", "cronico", "agudo", "inmunologico"]
SINTOMAS_CATALOGO = [
    "fiebre", "tos", "dolor_garganta", "congestion_nasal",
    "dolor_cabeza", "dolor_pecho", "fatiga", "nausea",
    "vomito", "diarrea", "mareo", "escalofrios",
]


class PLManager:
    """
    Lee el archivo .pl, mantiene los datos en memoria y puede reescribir
    el archivo completo preservando la sección de reglas fijas.
    """

    # Sección de reglas de inferencia (no se toca, siempre se añade al final)
    REGLAS_FIJAS = """
% =============================================================
%  SECCIÓN 8 — REGLAS DE INFERENCIA (no modificar manualmente)
% =============================================================

limpiar_paciente :-
    retractall(sintoma_paciente(_, _)),
    retractall(alergia_paciente(_)),
    retractall(condicion_paciente(_)).

multiplicador_sev(leve,     1).
multiplicador_sev(moderado, 2).
multiplicador_sev(severo,   3).

listar_enfermedades(E) :- enfermedad(E, _, _, _).

componente_puntaje(E, Valor) :-
    sintoma_paciente(S, Sev),
    tiene_sintoma(E, S, Peso),
    multiplicador_sev(Sev, M),
    Valor is Peso * M.

puntaje_maximo(E, Max) :-
    findall(P, tiene_sintoma(E, _, P), Pesos),
    sum_list(Pesos, SumaPesos),
    Max is SumaPesos * 3.

puntaje_obtenido(E, Puntaje) :-
    findall(V, componente_puntaje(E, V), Valores),
    sum_list(Valores, Puntaje).

porcentaje_afinidad(E, Porcentaje) :-
    puntaje_maximo(E, Max),
    puntaje_obtenido(E, Obtenido),
    ( Max =:= 0
    -> Porcentaje is 0
    ;  PorcentajeF is (Obtenido / Max) * 100,
       round(PorcentajeF, Porcentaje)
    ).

nivel_urgencia(E, alta) :-
    sintoma_paciente(dolor_pecho, severo),
    enfermedad(E, _, respiratorio, _).

nivel_urgencia(E, media) :-
    porcentaje_afinidad(E, P),
    P >= 60,
    \\+ ( sintoma_paciente(dolor_pecho, severo),
         enfermedad(E, _, respiratorio, _) ).

nivel_urgencia(E, baja) :-
    porcentaje_afinidad(E, P),
    P < 60.

medicamento_inseguro(M) :-
    alergia_paciente(A),
    contraindicado_alergia(M, A).

medicamento_inseguro(M) :-
    condicion_paciente(C),
    contraindicado_condicion(M, C).

medicamento_seguro_para(E, M) :-
    trata(M, E),
    \\+ medicamento_inseguro(M).

sintomas_coincidentes(E, S) :-
    sintoma_paciente(S, _),
    tiene_sintoma(E, S, _).

diagnosticar(E, Porcentaje, Urgencia) :-
    enfermedad(E, _, _, _),
    porcentaje_afinidad(E, Porcentaje),
    Porcentaje > 0,
    nivel_urgencia(E, Urgencia).
"""

    def __init__(self, ruta_pl: str):
        self.ruta_pl = ruta_pl
        self.enfermedades: Dict[str, Enfermedad] = {}
        self.medicamentos: Dict[str, Medicamento] = {}
        self.sintomas_catalogo: List[str] = list(SINTOMAS_CATALOGO)
        self._parsear()

    def _parsear(self) -> None:
        """Lee el .pl actual y extrae enfermedades, síntomas y medicamentos."""
        if not os.path.exists(self.ruta_pl):
            return
        with open(self.ruta_pl, encoding="utf-8") as f:
            contenido = f.read()

        # Enfermedades
        for m in re.finditer(
            r"enfermedad\((\w+),\s*'([^']*)',\s*(\w+),\s*(\w+)\)", contenido
        ):
            nombre, desc, sistema, tipo = m.groups()
            self.enfermedades[nombre] = Enfermedad(nombre, desc, sistema, tipo)

        # Síntomas por enfermedad
        for m in re.finditer(r"tiene_sintoma\((\w+),\s*(\w+),\s*(\d+)\)", contenido):
            enf, sint, peso = m.groups()
            if enf in self.enfermedades:
                self.enfermedades[enf].sintomas.append((sint, int(peso)))

        # Medicamentos
        for m in re.finditer(r"^medicamento\((\w+)\)\.", contenido, re.MULTILINE):
            nombre = m.group(1)
            self.medicamentos[nombre] = Medicamento(nombre)

        # Tratamientos
        for m in re.finditer(r"trata\((\w+),\s*(\w+)\)", contenido):
            med, enf = m.groups()
            if med in self.medicamentos:
                self.medicamentos[med].trata.append(enf)

        # Contraindicaciones alergia
        for m in re.finditer(r"contraindicado_alergia\((\w+),\s*(\w+)\)", contenido):
            med, alergia = m.groups()
            if med in self.medicamentos:
                self.medicamentos[med].contra_alergia.append(alergia)

        # Contraindicaciones condición
        for m in re.finditer(r"contraindicado_condicion\((\w+),\s*(\w+)\)", contenido):
            med, cond = m.groups()
            if med in self.medicamentos:
                self.medicamentos[med].contra_condicion.append(cond)

        # Catálogo de síntomas
        for m in re.finditer(r"^sintoma\((\w+)\)\.", contenido, re.MULTILINE):
            s = m.group(1)
            if s not in self.sintomas_catalogo:
                self.sintomas_catalogo.append(s)

    def guardar(self) -> None:
        """Genera y escribe el archivo .pl completo desde los datos en memoria."""
        # Backup automático
        if os.path.exists(self.ruta_pl):
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            shutil.copy(self.ruta_pl, self.ruta_pl + f".bak_{ts}")

        lineas = []
        lineas.append(
            "% =============================================================\n"
            "%  MediLogic — Base de Conocimiento Médico (generado automáticamente)\n"
            f"%  Actualizado: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "% =============================================================\n"
        )

        # Sección 1: Dinámicos
        lineas.append(
            "\n:- dynamic sintoma_paciente/2.\n"
            ":- dynamic alergia_paciente/1.\n"
            ":- dynamic condicion_paciente/1.\n"
        )

        # Sección 2: Catálogo de síntomas
        lineas.append("\n% --- Catálogo de síntomas ---\n")
        for s in sorted(set(self.sintomas_catalogo)):
            lineas.append(f"sintoma({s}).\n")

        # Sección 3: Enfermedades
        lineas.append("\n% --- Enfermedades ---\n")
        for e in self.enfermedades.values():
            desc = e.descripcion.replace("'", "\\'")
            lineas.append(
                f"enfermedad({e.nombre}, '{desc}', {e.sistema}, {e.tipo}).\n"
            )

        # Sección 4: Síntomas por enfermedad
        lineas.append("\n% --- Relación enfermedad-síntoma-peso ---\n")
        for e in self.enfermedades.values():
            for sint, peso in sorted(e.sintomas, key=lambda x: -x[1]):
                lineas.append(f"tiene_sintoma({e.nombre}, {sint}, {peso}).\n")

        # Sección 5: Medicamentos
        lineas.append("\n% --- Medicamentos ---\n")
        for m in self.medicamentos.values():
            lineas.append(f"medicamento({m.nombre}).\n")

        # Sección 6: Tratamientos
        lineas.append("\n% --- Tratamientos ---\n")
        for m in self.medicamentos.values():
            for enf in m.trata:
                lineas.append(f"trata({m.nombre}, {enf}).\n")

        # Sección 7: Contraindicaciones
        lineas.append("\n% --- Contraindicaciones ---\n")
        for m in self.medicamentos.values():
            for a in m.contra_alergia:
                lineas.append(f"contraindicado_alergia({m.nombre}, {a}).\n")
            for c in m.contra_condicion:
                lineas.append(f"contraindicado_condicion({m.nombre}, {c}).\n")

        # Sección 8: Reglas fijas
        lineas.append(self.REGLAS_FIJAS)

        with open(self.ruta_pl, "w", encoding="utf-8") as f:
            f.writelines(lineas)

    # ------------------------------------------------------------------
    #  Operaciones CRUD — Enfermedades
    # ------------------------------------------------------------------

    def agregar_enfermedad(self, e: Enfermedad) -> None:
        self.enfermedades[e.nombre] = e
        # Registrar síntomas nuevos en catálogo
        for s, _ in e.sintomas:
            if s not in self.sintomas_catalogo:
                self.sintomas_catalogo.append(s)

    def editar_enfermedad(self, nombre: str, nueva: Enfermedad) -> None:
        if nombre in self.enfermedades:
            del self.enfermedades[nombre]
        self.enfermedades[nueva.nombre] = nueva

    def eliminar_enfermedad(self, nombre: str) -> None:
        self.enfermedades.pop(nombre, None)
        # Limpiar tratamientos que referencian esta enfermedad
        for m in self.medicamentos.values():
            if nombre in m.trata:
                m.trata.remove(nombre)

    # ------------------------------------------------------------------
    #  Operaciones CRUD — Medicamentos
    # ------------------------------------------------------------------

    def agregar_medicamento(self, m: Medicamento) -> None:
        self.medicamentos[m.nombre] = m

    def editar_medicamento(self, nombre: str, nuevo: Medicamento) -> None:
        self.medicamentos.pop(nombre, None)
        self.medicamentos[nuevo.nombre] = nuevo

    def eliminar_medicamento(self, nombre: str) -> None:
        self.medicamentos.pop(nombre, None)

    # ------------------------------------------------------------------
    #  Catálogo de síntomas
    # ------------------------------------------------------------------

    def agregar_sintoma_catalogo(self, nombre: str) -> None:
        if nombre not in self.sintomas_catalogo:
            self.sintomas_catalogo.append(nombre)

    def eliminar_sintoma_catalogo(self, nombre: str) -> None:
        if nombre in self.sintomas_catalogo:
            self.sintomas_catalogo.remove(nombre)
        # Quitar de todas las enfermedades
        for e in self.enfermedades.values():
            e.sintomas = [(s, p) for s, p in e.sintomas if s != nombre]
