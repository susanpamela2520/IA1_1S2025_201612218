from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import os

from pyswip import Prolog

@dataclass

#Agrupa la informacion que se le da al paciente
class ResultadoDiagnostico:
    enfermedad: str
    afinidad: int          # nivel de porcentaje de 0-100
    urgencia: str          # alto,medio o bajo
    medicamentos: List[str]  = field(default_factory=list)
    sintomas_coincidentes: List[str]  = field(default_factory=list)

# Aqui se hace el puente entre python y el medilogi.pl
class PrologEngine:
    def __init__(self, ruta_archivo: str):
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"No se encontró el archivo Prolog: {ruta_archivo}")
        self.ruta_archivo = ruta_archivo
        self.prolog = Prolog()
        self._cargar_archivo(ruta_archivo)
    
#Carga archivo de prolog
    def _cargar_archivo(self, ruta: str) -> None:
        ruta_abs = os.path.abspath(ruta).replace("\\", "/")  # Asegura formato correcto en Windows
        self.prolog.consult(ruta_abs)
        ok = list(self.prolog.query("current_predicate(enfermedad/4)."))
        if not ok:
            raise RuntimeError(f"El archivo Prolog no se cargó correctamente o no define 'enfermedad/4'.")

#Recarga el motor de prolog
    def recargar(self) -> None:
        self.prolog = Prolog()
        self._cargar_archivo(self.ruta_archivo)

#Borra los datos del paciente anterior    
    def limpiar_paciente(self) -> None:
        list(self.prolog.query("limpiar_paciente."))


    def cargar_perfil_paciente(self,sintomas: List[Tuple[str, str]],   # [("fiebre","severo"), ("tos","leve"), ...]
                               alergias: List[str],               # ["alergia_aines", ...] 
                               condiciones: List[str],            # ["insuficiencia_renal", ...] 
                               )  -> None:
        
        # Aqui se registra en Prolog los datos del paciente actual.
        # y tambien se limpia primero cualquier dato previo.
        self.limpiar_paciente()
        for s, severidad in sintomas:
            list(self.prolog.query(f"assertz(sintoma_paciente({s}, {severidad}))."))
        for a in alergias:
            list(self.prolog.query(f"assertz(alergia_paciente({a}))."))
        for c in condiciones:
            list(self.prolog.query(f"assertz(condicion_paciente({c}))."))

    
    #QUERIES INDIVIDUALE 
    #estas sirven para mostrar el razonamiento del sistema

    #Query1: listar enfermedades registradas
    #mostrar que conoce el sistema y que se puede diagnosticar
   
    def q1_listar_enfermedades(self) -> List[str]:
        return sorted(set(str(r["E"]) for r in self.prolog.query("listar_enfermedades(E).")))

   #Query2: porcentaje de afinidad con todas las enfermedades
    def q2_afinidad_todas(self) -> Dict[str, int]:
            return{str(r["E"]): int(r["P"])
                for r in self.prolog.query("enfermedad(E,_,_,_), porcentaje_afinidad(E,P).")}  
         
    #Query3: diagnostica todas las enfermedades que tengan mayor a 0
    def q3_diagnosticar_todo(self) -> List[Tuple[str, int, str]]:
        out = []
        vistos = set()
        for r in self.prolog.query("diagnosticar(E, P, U)."):
            e = str(r["E"])
            if e not in vistos:
                vistos.add(e)
                out.append((e, int(r["P"]), str(r["U"])))
        return sorted(out, key=lambda x: x[1], reverse=True)


    #Query4: medicamentos seguros para una enfermedad dada
    def q4_medicamentos_seguros(self, enfermedad: str) -> List[str]:
        return sorted(set(str(r["M"]))
                         for r in self.prolog.query(f"medicamento_seguro_para({enfermedad}, M)."))


    #Query5: sintomas que coincidieron para una enfermedad dada
    def q5_sintomas_que_coincidieron(self, enfermedad: str) -> List[str]:
       return sorted(set(str(r["S"])
                            for r in self.prolog.query(f"sintomas_coincidentes({enfermedad}, S).")))           


    
    #Parte de Diagnostico 
    #aqui se hace el diagnostico completo 
    #aqui se llaman las queries para tener la informacion 

    def diagnostico_completo(self) -> List[ResultadoDiagnostico]:
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
    
    #Espacio para administracion

    def listar_medicamentos(self) -> List[str]:
        return sorted(set(str(r["M"]) for r in self.prolog.query("medicamento(M).")))

    def listar_sintomas_de(self, enfermedad: str) -> List[Tuple[str, int]]:
        return sorted((str(r["S"]), int(r["P"]))
                      for r in self.prolog.query(f"tiene_sintoma({enfermedad},S,P)."))
