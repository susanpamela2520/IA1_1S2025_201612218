from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import os

from pyswip import Prolog

#Aqui esta el motor de inferencia logica de MediLogic
#Es el puente entre Python y Prolog usando pyswip
#Carga el archivo .pl y expone metodos para consultar el sistema experto

@dataclass
class ResultadoDiagnostico:
    #Resultado de un diagnostico completo para una enfermedad
    enfermedad: str
    afinidad: int
    urgencia: str
    medicamentos: List[str] = field(default_factory=list)
    sintomas_coincidentes: List[str] = field(default_factory=list)


def _atom(valor) -> str:
    #Convierte cualquier tipo que retorne pyswip a string limpio
    #En Windows pyswip puede devolver Atom, bytes, frozenset o str
    if isinstance(valor, (set, frozenset)):
        return _atom(next(iter(valor))) if valor else ""
    if isinstance(valor, bytes):
        return valor.decode("utf-8")
    return str(valor)


class PrologEngine:

    def __init__(self, ruta_archivo: str):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"Archivo Prolog no encontrado: {ruta_archivo}")
        self.ruta_archivo = ruta_archivo
        self.prolog = Prolog()
        self._cargar_archivo(ruta_archivo)

    def _cargar_archivo(self, ruta: str) -> None:
        #Carga el archivo .pl en el motor Prolog
        #Convierte la ruta a formato Unix para compatibilidad con Windows
        ruta_abs = os.path.abspath(ruta).replace("\\", "/")
        self.prolog.consult(ruta_abs)
        # Verificar que la regla principal existe
        ok = list(self.prolog.query("current_predicate(diagnosticar/3)."))
        if not ok:
            raise RuntimeError(
                "El .pl no contiene 'diagnosticar/3'. Verifica el archivo medilogic.pl."
            )

    def recargar(self) -> None:
        #Recarga el archivo .pl cuando el Admin hace cambios
        #pyswip usa singleton global: NO se puede hacer Prolog() de nuevo
        #Se usa load_files con if(true) para forzar recarga aunque ya estuviera cargado
        ruta_abs = os.path.abspath(self.ruta_archivo).replace("\\", "/")
        list(self.prolog.query(f"load_files('{ruta_abs}', [if(true)])."))

    # ------------------------------------------------------------------
    # Perfil del paciente
    # ------------------------------------------------------------------

    def limpiar_paciente(self) -> None:
        #Borra el perfil del paciente actual de la memoria de Prolog
        list(self.prolog.query("limpiar_paciente."))

    def cargar_perfil_paciente(
        self,
        sintomas: List[Tuple[str, str]],
        alergias: List[str],
        condiciones: List[str],
    ) -> None:
        #Carga el perfil del paciente en la memoria de Prolog
        #sintomas: [(nombre, severidad), ...]  ej: [("fiebre", "severo"), ...]
        #alergias: ["alergia_aines", ...]
        #condiciones: ["insuficiencia_renal", ...]
        self.limpiar_paciente()
        for s, sev in sintomas:
            list(self.prolog.query(f"assertz(sintoma_paciente({s},{sev}))."))
        for a in alergias:
            list(self.prolog.query(f"assertz(alergia_paciente({a}))."))
        for c in condiciones:
            list(self.prolog.query(f"assertz(condicion_paciente({c}))."))

    # ------------------------------------------------------------------
    # Queries (minimo 5 requeridas por el proyecto)
    # ------------------------------------------------------------------

    def q1_listar_enfermedades(self) -> List[str]:
        #QUERY 1 - Lista todas las enfermedades registradas en el .pl
        return sorted(set(
            _atom(r["E"]) for r in self.prolog.query("listar_enfermedades(E).")
        ))

    def q2_afinidad_todas(self) -> Dict[str, int]:
        #QUERY 2 - Porcentaje de afinidad del paciente con cada enfermedad
        return {
            _atom(r["E"]): int(r["P"])
            for r in self.prolog.query(
                "enfermedad(E,_,_,_), porcentaje_afinidad(E,P)."
            )
        }

    def q3_diagnosticar_todo(self) -> List[Tuple[str, int, str]]:
        #QUERY 3 - Diagnostico completo: enfermedades con afinidad > 0 ordenadas descendente
        out = []
        vistos = set()
        for r in self.prolog.query("diagnosticar(E,P,U)."):
            e = _atom(r["E"])
            if e not in vistos:
                vistos.add(e)
                out.append((e, int(r["P"]), _atom(r["U"])))
        return sorted(out, key=lambda x: x[1], reverse=True)

    def q4_medicamentos_seguros(self, enfermedad: str) -> List[str]:
        #QUERY 4 - Medicamentos seguros para una enfermedad (sin contraindicaciones)
        return sorted(set(
            _atom(r["M"])
            for r in self.prolog.query(f"medicamento_seguro_para({enfermedad},M).")
        ))

    def q5_sintomas_que_coincidieron(self, enfermedad: str) -> List[str]:
        #QUERY 5 - Sintomas del paciente que coincidieron con la enfermedad
        #Sirve para explicar la inferencia al usuario
        return sorted(set(
            _atom(r["S"])
            for r in self.prolog.query(f"sintomas_coincidentes({enfermedad},S).")
        ))

    # ------------------------------------------------------------------
    # Diagnostico completo integrado
    # ------------------------------------------------------------------

    def diagnostico_completo(self) -> List[ResultadoDiagnostico]:
        #Ejecuta el diagnostico completo
        #Retorna lista de ResultadoDiagnostico ordenada por afinidad descendente
        return [
            ResultadoDiagnostico(
                enfermedad=e,
                afinidad=p,
                urgencia=u,
                medicamentos=self.q4_medicamentos_seguros(e),
                sintomas_coincidentes=self.q5_sintomas_que_coincidieron(e),
            )
            for e, p, u in self.q3_diagnosticar_todo()
        ]

    # Consultas auxiliares para el modulo Admin
    def listar_medicamentos(self) -> List[str]:
        return sorted(set(
            _atom(r["M"]) for r in self.prolog.query("medicamento(M).")
        ))

    def listar_sintomas_de(self, enfermedad: str) -> List[Tuple[str, int]]:
        return sorted(
            (_atom(r["S"]), int(r["P"]))
            for r in self.prolog.query(f"tiene_sintoma({enfermedad},S,P).")
        )