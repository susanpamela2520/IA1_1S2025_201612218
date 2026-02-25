% ==============================
% MediLogic - Base de Conocimiento (Prolog)
% ==============================

:- dynamic patient_symptom/2.
:- dynamic patient_allergy/1.
:- dynamic patient_condition/1.

% ------------------------------
% Catálogo de síntomas (solo referencia)
% symptom(Name).
% ------------------------------
symptom(fiebre).
symptom(tos).
symptom(dolor_garganta).
symptom(congestion_nasal).
symptom(dolor_cabeza).
symptom(dolor_pecho).
symptom(fatiga).
symptom(nausea).

% ------------------------------
% Enfermedades
% disease(Name, Description, System, Type).
% ------------------------------
disease(gripe, "Infección viral común con fiebre y malestar general.", respiratorio, viral).
disease(resfriado, "Cuadro leve respiratorio con congestión y tos.", respiratorio, viral).
disease(covid19, "Infección viral respiratoria con fiebre, tos y fatiga.", respiratorio, viral).
disease(gastritis, "Inflamación del estómago con náusea y malestar.", digestivo, agudo).

% ------------------------------
% Relación enfermedad - síntoma con peso base (1..5)
% has_symptom(Disease, Symptom, Weight).
% ------------------------------
has_symptom(gripe, fiebre, 5).
has_symptom(gripe, tos, 4).
has_symptom(gripe, dolor_cabeza, 3).
has_symptom(gripe, fatiga, 4).
has_symptom(gripe, dolor_garganta, 3).

has_symptom(resfriado, congestion_nasal, 5).
has_symptom(resfriado, tos, 3).
has_symptom(resfriado, dolor_garganta, 3).
has_symptom(resfriado, dolor_cabeza, 2).
has_symptom(resfriado, fiebre, 1).

has_symptom(covid19, fiebre, 4).
has_symptom(covid19, tos, 4).
has_symptom(covid19, fatiga, 5).
has_symptom(covid19, dolor_pecho, 3).
has_symptom(covid19, dolor_cabeza, 3).

has_symptom(gastritis, nausea, 5).
has_symptom(gastritis, fatiga, 2).
has_symptom(gastritis, dolor_cabeza, 1).

% ------------------------------
% Medicamentos
% medication(Name).
% treats(Med, Disease).
% contraindicated_with_allergy(Med, Allergy).
% contraindicated_with_condition(Med, Condition).
% ------------------------------
medication(paracetamol).
medication(ibuprofeno).
medication(antihistaminico).
medication(omeprazol).

treats(paracetamol, gripe).
treats(paracetamol, resfriado).
treats(paracetamol, covid19).

treats(ibuprofeno, gripe).
treats(ibuprofeno, resfriado).

treats(antihistaminico, resfriado).
treats(omeprazol, gastritis).

% Alergias (ejemplo)
contraindicated_with_allergy(ibuprofeno, alergia_aines).
contraindicated_with_allergy(antihistaminico, alergia_antihistaminicos).

% Enfermedades crónicas (ejemplo)
contraindicated_with_condition(ibuprofeno, insuficiencia_renal).
contraindicated_with_condition(ibuprofeno, gastritis_cronica).

% ==============================
% Utilidades
% ==============================

% Limpia el perfil del paciente en memoria
clear_patient :-
    retractall(patient_symptom(_,_)),
    retractall(patient_allergy(_)),
    retractall(patient_condition(_)).

% Severidad -> multiplicador (leve=1, moderado=2, severo=3)
sev_mult(leve, 1).
sev_mult(moderado, 2).
sev_mult(severo, 3).

% Lista de enfermedades
list_diseases(D) :- disease(D,_,_,_).

% ==============================
% Score/Afinidad (inferencia)
% ==============================

% score_component(Disease, Value) para cada síntoma ingresado que coincide
score_component(D, Value) :-
    patient_symptom(Symptom, Sev),
    has_symptom(D, Symptom, W),
    sev_mult(Sev, M),
    Value is W * M.

% total_possible(Disease, TotalBase) suma de pesos base (sirve para normalizar)
total_possible(D, TotalBase) :-
    findall(W, has_symptom(D, _, W), Ws),
    sum_list(Ws, TotalBase).

% matched_score(Disease, Score) suma de score_component
matched_score(D, Score) :-
    findall(V, score_component(D, V), Vs),
    sum_list(Vs, Score).

% affinity_percent(Disease, Percent)
% Normalización: max posible = TotalBase*3 (por severo)
affinity_percent(D, Percent) :-
    total_possible(D, TotalBase),
    matched_score(D, Score),
    Max is TotalBase * 3,
    ( Max =:= 0 -> Percent is 0
    ; PercentFloat is (Score / Max) * 100,
      round(PercentFloat, Percent)
    ).


