from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import os

from pyswip import Prolog


@dataclass
class ResultadoDiagnostico:
    """Agrupa todo lo que se le muestra al paciente sobre una enfermedad."""
    enfermedad: str
    afinidad: int          # porcentaje 0-100
    urgencia: str          # "alta", "media" o "baja"
    medicamentos: List[str]
    sintomas_coincidentes: List[str]


class PrologEngine:
    """
    Puente entre Python y el archivo medilogic.pl.
    Carga la base de conocimiento y expone métodos para hacer consultas.
    """

    def __init__(self, ruta_archivo: str):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo Prolog: {ruta_archivo}")

        self.prolog = Prolog()
        self.prolog.consult(ruta_archivo)

        # Verificar que la regla principal existe en el archivo cargado
        ok = list(self.prolog.query("current_predicate(diagnosticar/3)."))
        if not ok:
            raise RuntimeError(
                "El archivo Prolog cargó pero no tiene la regla 'diagnosticar/3'. "
                "Revisa que medilogic.pl esté completo."
            )

    # ----------------------------------------------------------
    # MANEJO DEL PERFIL DEL PACIENTE
    # ----------------------------------------------------------

    def limpiar_paciente(self) -> None:
        """Borra los datos del paciente anterior de la memoria Prolog."""
        list(self.prolog.query("limpiar_paciente."))

    def cargar_perfil_paciente(
        self,
        sintomas: List[Tuple[str, str]],   # [("fiebre","severo"), ("tos","leve"), ...]
        alergias: List[str],               # ["alergia_aines", ...]
        condiciones: List[str],            # ["insuficiencia_renal", ...]
    ) -> None:
        """
        Registra en Prolog los datos del paciente actual.
        Primero limpia cualquier dato previo.
        """
        self.limpiar_paciente()

        for sintoma, severidad in sintomas:
            list(self.prolog.query(f"assertz(sintoma_paciente({sintoma}, {severidad}))."))

        for alergia in alergias:
            list(self.prolog.query(f"assertz(alergia_paciente({alergia}))."))

        for condicion in condiciones:
            list(self.prolog.query(f"assertz(condicion_paciente({condicion}))."))

    # ----------------------------------------------------------
    # LAS 5 CONSULTAS (queries) AL MOTOR PROLOG
    # ----------------------------------------------------------

    def q1_listar_enfermedades(self) -> List[str]:
        """
        QUERY 1: Devuelve la lista de enfermedades registradas en el sistema.
        Útil para mostrar qué conoce el sistema.
        """
        resultados = [str(r["E"]) for r in self.prolog.query("listar_enfermedades(E).")]
        return sorted(set(resultados))

    def q2_afinidad_todas(self) -> Dict[str, int]:
        """
        QUERY 2: Calcula el porcentaje de afinidad del paciente actual
        con TODAS las enfermedades (incluyendo las que tienen 0%).
        """
        resultado = {}
        for r in self.prolog.query("enfermedad(E,_,_,_), porcentaje_afinidad(E,P)."):
            resultado[str(r["E"])] = int(r["P"])
        return resultado

    def q3_diagnosticar_todo(self) -> List[Tuple[str, int, str]]:
        """
        QUERY 3: Devuelve enfermedades con afinidad > 0, ordenadas de mayor a menor.
        Cada elemento es (enfermedad, porcentaje, urgencia).
        """
        resultados = []
        for r in self.prolog.query(
            "enfermedad(E,_,_,_), porcentaje_afinidad(E,P), nivel_urgencia(E,U), P > 0."
        ):
            resultados.append((str(r["E"]), int(r["P"]), str(r["U"])))
        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados

    def q4_medicamentos_seguros(self, enfermedad: str) -> List[str]:
        """
        QUERY 4: Devuelve medicamentos que tratan la enfermedad dada
        y que NO están contraindicados para este paciente.
        """
        meds = [
            str(r["M"])
            for r in self.prolog.query(f"medicamento_seguro_para({enfermedad}, M).")
        ]
        return sorted(set(meds))

    def q5_sintomas_que_coincidieron(self, enfermedad: str) -> List[str]:
        """
        QUERY 5: Explica qué síntomas del paciente apuntaron a esta enfermedad.
        Sirve para mostrar el razonamiento del sistema.
        """
        sintomas = [
            str(r["S"])
            for r in self.prolog.query(f"sintomas_coincidentes({enfermedad}, S).")
        ]
        return sorted(set(sintomas))

    # ----------------------------------------------------------
    # DIAGNÓSTICO COMPLETO (llama las 5 queries)
    # ----------------------------------------------------------

    def diagnostico_completo(self) -> List[ResultadoDiagnostico]:
        """
        Ejecuta el diagnóstico completo y devuelve una lista de resultados
        ordenados de mayor a menor afinidad, listos para mostrar en la UI.
        """
        candidatos = self.q3_diagnosticar_todo()
        resultados = []

        for enfermedad, porcentaje, urgencia in candidatos:
            meds = self.q4_medicamentos_seguros(enfermedad)
            coincidentes = self.q5_sintomas_que_coincidieron(enfermedad)

            resultados.append(
                ResultadoDiagnostico(
                    enfermedad=enfermedad,
                    afinidad=porcentaje,
                    urgencia=urgencia,
                    medicamentos=meds,
                    sintomas_coincidentes=coincidentes,
                )
            )

        return resultados