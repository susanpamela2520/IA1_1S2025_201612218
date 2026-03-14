%  MediLogic — Base de Conocimiento Médico (generado automáticamente)
%  Actualizado: 2026-03-13 19:25:43

:- dynamic sintoma_paciente/2.
:- dynamic alergia_paciente/1.
:- dynamic condicion_paciente/1.

:- discontiguous contraindicado_alergia/2.
:- discontiguous contraindicado_condicion/2.
:- discontiguous trata/2.
:- discontiguous tiene_sintoma/3.

% --- Catálogo de síntomas ---
sintoma(congestion_nasal).
sintoma(diarrea).
sintoma(dolor_cabeza).
sintoma(dolor_garganta).
sintoma(dolor_pecho).
sintoma(escalofrios).
sintoma(fatiga).
sintoma(fiebre).
sintoma(mareo).
sintoma(nausea).
sintoma(sangrado_nariz).
sintoma(tos).
sintoma(vomito).

% --- Enfermedades ---
enfermedad(gripe, 'Infeccion viral comun con fiebre y malestar general', respiratorio, viral).
enfermedad(resfriado, 'Cuadro leve respiratorio con congestion y tos', respiratorio, viral).
enfermedad(covid19, 'Infeccion viral respiratoria con fiebre tos y fatiga', respiratorio, viral).
enfermedad(gastritis, 'Inflamacion del estomago con nausea y malestar', digestivo, agudo).
enfermedad(sinusitis, 'Inflamacion de los senos paranasales con congestion y presion facial', respiratorio, bacteriano).

% --- Relación enfermedad-síntoma-peso ---
tiene_sintoma(gripe, fiebre, 5).
tiene_sintoma(gripe, tos, 4).
tiene_sintoma(gripe, fatiga, 4).
tiene_sintoma(gripe, dolor_cabeza, 3).
tiene_sintoma(gripe, dolor_garganta, 3).
tiene_sintoma(resfriado, congestion_nasal, 5).
tiene_sintoma(resfriado, tos, 3).
tiene_sintoma(resfriado, dolor_garganta, 3).
tiene_sintoma(resfriado, dolor_cabeza, 2).
tiene_sintoma(resfriado, fiebre, 1).
tiene_sintoma(covid19, fatiga, 5).
tiene_sintoma(covid19, fiebre, 4).
tiene_sintoma(covid19, tos, 4).
tiene_sintoma(covid19, dolor_pecho, 3).
tiene_sintoma(covid19, dolor_cabeza, 3).
tiene_sintoma(gastritis, nausea, 5).
tiene_sintoma(gastritis, vomito, 4).
tiene_sintoma(gastritis, fatiga, 2).
tiene_sintoma(gastritis, dolor_cabeza, 1).
tiene_sintoma(gastritis, diarrea, 1).
tiene_sintoma(sinusitis, congestion_nasal, 5).
tiene_sintoma(sinusitis, dolor_cabeza, 4).
tiene_sintoma(sinusitis, fiebre, 3).
tiene_sintoma(sinusitis, dolor_garganta, 2).
tiene_sintoma(sinusitis, fatiga, 2).

% --- Medicamentos ---
medicamento(paracetamol).
medicamento(ibuprofeno).
medicamento(antihistaminico).
medicamento(omeprazol).
medicamento(amoxicilina).
medicamento(azitromicina).

% --- Tratamientos ---
trata(paracetamol, gripe).
trata(paracetamol, resfriado).
trata(paracetamol, covid19).
trata(paracetamol, sinusitis).
trata(ibuprofeno, gripe).
trata(ibuprofeno, resfriado).
trata(ibuprofeno, sinusitis).
trata(antihistaminico, resfriado).
trata(antihistaminico, sinusitis).
trata(omeprazol, gastritis).
trata(amoxicilina, sinusitis).
trata(azitromicina, sinusitis).

% --- Contraindicaciones por alergia ---
contraindicado_alergia(ibuprofeno, alergia_aines).
contraindicado_alergia(antihistaminico, alergia_antihistaminicos).
contraindicado_alergia(amoxicilina, alergia_penicilina).

% --- Contraindicaciones por condicion cronica ---
contraindicado_condicion(ibuprofeno, insuficiencia_renal).
contraindicado_condicion(ibuprofeno, gastritis_cronica).
contraindicado_condicion(omeprazol, insuficiencia_hepatica).


%REGLAS DE INFERENCIA 

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
    not((sintoma_paciente(dolor_pecho, severo), enfermedad(E, _, respiratorio, _))).
 
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
    not(medicamento_inseguro(M)).

sintomas_coincidentes(E, S) :-
    sintoma_paciente(S, _),
    tiene_sintoma(E, S, _).

diagnosticar(E, Porcentaje, Urgencia) :-
    enfermedad(E, _, _, _),
    porcentaje_afinidad(E, Porcentaje),
    Porcentaje > 0,
    nivel_urgencia(E, Urgencia).
