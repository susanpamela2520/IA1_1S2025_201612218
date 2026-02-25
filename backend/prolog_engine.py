from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict
import os

from pyswip import Prolog


@dataclass
class DiagnosisResult:
    disease: str
    affinity: int
    urgency: str
    safe_meds: List[str]
    matched_symptoms: List[str]


class PrologEngine:
    def __init__(self, prolog_file_path: str):
        if not os.path.exists(prolog_file_path):
            raise FileNotFoundError(f"No existe el archivo Prolog: {prolog_file_path}")

        self.prolog = Prolog()
        # Cargar la base de conocimiento
        self.prolog.consult(prolog_file_path)

    def reset_patient(self) -> None:
        list(self.prolog.query("clear_patient."))

    def set_patient_profile(
        self,
        symptoms_with_severity: List[Tuple[str, str]],
        allergies: List[str],
        conditions: List[str],
    ) -> None:
        """
        symptoms_with_severity: [("fiebre","leve"), ("tos","severo"), ...]
        allergies: ["alergia_aines", ...]
        conditions: ["insuficiencia_renal", ...]
        """
        self.reset_patient()

        # Assert síntomas con severidad
        for sym, sev in symptoms_with_severity:
            q = f"assertz(patient_symptom({sym},{sev}))."
            list(self.prolog.query(q))

        # Assert alergias
        for a in allergies:
            q = f"assertz(patient_allergy({a}))."
            list(self.prolog.query(q))

        # Assert condiciones crónicas
        for c in conditions:
            q = f"assertz(patient_condition({c}))."
            list(self.prolog.query(q))

    # -------------------------
    # QUERIES (mínimo 5)
    # -------------------------

    def q1_list_diseases(self) -> List[str]:
        """QUERY #1: listar enfermedades registradas"""
        results = []
        for r in self.prolog.query("list_diseases(D)."):
            results.append(str(r["D"]))
        return sorted(list(set(results)))

    def q2_affinity_for_all(self) -> Dict[str, int]:
        """QUERY #2: afinidad para todas las enfermedades"""
        out: Dict[str, int] = {}
        for r in self.prolog.query("disease(D,_,_,_), affinity_percent(D,P)."):
            out[str(r["D"])] = int(r["P"])
        return out

    def q3_diagnose_all(self) -> List[Tuple[str, int, str]]:
        """QUERY #3: diagnósticos candidatos (D, Percent, Urgencia)"""
        out = []
        for r in self.prolog.query("diagnose(D,P,U)."):
            out.append((str(r["D"]), int(r["P"]), str(r["U"])))
        # Ordenar por afinidad desc
        out.sort(key=lambda x: x[1], reverse=True)
        return out

    def q4_safe_meds_for(self, disease: str) -> List[str]:
        """QUERY #4: medicamentos seguros para una enfermedad"""
        meds = []
        for r in self.prolog.query(f"safe_medication_for({disease}, M)."):
            meds.append(str(r["M"]))
        return sorted(list(set(meds)))

    def q5_matched_symptoms_for(self, disease: str) -> List[str]:
        """QUERY #5: qué síntomas coincidieron para una enfermedad (explicación)"""
        ms = []
        for r in self.prolog.query(f"matched_symptoms({disease}, S)."):
            ms.append(str(r["S"]))
        return sorted(list(set(ms)))

    # Resultado integrado para UI
    def full_diagnosis(self) -> List[DiagnosisResult]:
        candidates = self.q3_diagnose_all()
        final: List[DiagnosisResult] = []
        for d, p, u in candidates:
            meds = self.q4_safe_meds_for(d)
            matched = self.q5_matched_symptoms_for(d)
            final.append(
                DiagnosisResult(
                    disease=d,
                    affinity=p,
                    urgency=u,
                    safe_meds=meds,
                    matched_symptoms=matched,
                )
            )
        return final