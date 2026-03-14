%   MediLogic — Base de Conocimiento en Prolog

% ----------------------------------------------------------
% Aqui estan los Predicados dinámicos 
% estos tiene la informacion dinamica que puede modificarse en la ejecución, como los síntomas actuales del paciente, alergias y condiciones crónicas.
% desde Python para cada paciente.
% ----------------------------------------------------------
:- dynamic sintoma_paciente/2.    % sintoma_paciente(nombre_sintoma, severidad)
:- dynamic alergia_paciente/1.    % alergia_paciente(nombre_alergia)
:- dynamic condicion_paciente/1.  % condicion_paciente(nombre_condicion_cronica)


% ============================================================
%  CATÁLOGO DE SÍNTOMAS
%  Aqui se toma como referencia los sintomas
%  Administrado por ADMIN
% ============================================================
sintoma(fiebre).
sintoma(tos).
sintoma(dolor_garganta).
sintoma(congestion_nasal).
sintoma(dolor_cabeza).
sintoma(dolor_pecho).
sintoma(fatiga).
sintoma(nausea).
sintoma(vomito).
sintoma(diarrea).

% ============================================================
% ENFERMEDADES
%   enfermedad(Nombre, Descripcion, SistemaDelCuerpo, Tipo).
% ============================================================
enfermedad(gripe, 'Infeccion viral comun con fiebre y malestar general', respiratorio, viral).

enfermedad(resfriado, 'Cuadro leve respiratorio con congestion y tos', respiratorio, viral).

enfermedad(covid19, 'Infeccion viral respiratoria con fiebre tos y fatiga', respiratorio, viral).

enfermedad(gastritis, 'Inflamacion del estomago con nausea y malestar', digestivo, agudo).

enfermedad(sinusitis, 'Inflamacion de los senos paranasales con congestion y presion facial', respiratorio, bacteriano).

% ============================================================
% SÍNTOMAS POR ENFERMEDAD CON PESO
%   tiene_sintoma(Enfermedad, Sintoma, Peso).
%   Peso va de 1 (poco relevante) a 5 (muy relevante).
% ============================================================
tiene_sintoma(gripe, fiebre,         5).
tiene_sintoma(gripe, tos,            4).
tiene_sintoma(gripe, fatiga,         4).
tiene_sintoma(gripe, dolor_cabeza,   3).
tiene_sintoma(gripe, dolor_garganta, 3).

tiene_sintoma(resfriado, congestion_nasal, 5).
tiene_sintoma(resfriado, tos,             3).
tiene_sintoma(resfriado, dolor_garganta,  3).
tiene_sintoma(resfriado, dolor_cabeza,    2).
tiene_sintoma(resfriado, fiebre,          1).

tiene_sintoma(covid19, fatiga,        5).
tiene_sintoma(covid19, fiebre,        4).
tiene_sintoma(covid19, tos,           4).
tiene_sintoma(covid19, dolor_pecho,   3).
tiene_sintoma(covid19, dolor_cabeza,  3).

tiene_sintoma(gastritis, nausea,       5).
tiene_sintoma(gastritis, fatiga,       2).
tiene_sintoma(gastritis, dolor_cabeza, 1).
tiene_sintoma(gastritis, vomito, 4).
tiene_sintoma(gastritis, diarrea, 1).

tiene_sintoma(sinusitis, congestion_nasal, 5).
tiene_sintoma(sinusitis, dolor_cabeza, 4).
tiene_sintoma(sinusitis, fiebre, 3).
tiene_sintoma(sinusitis, dolor_garganta, 2).
tiene_sintoma(sinusitis, fatiga, 2).


% ============================================================
% MEDICAMENTOS
% medicamentos (Nombre)
% ============================================================
medicamento(paracetamol).
medicamento(ibuprofeno).
medicamento(antihistaminico).
medicamento(omeprazol).
medicamento(amoxicilina).
medicamento(azitromicina).

% Qué enfermedad trata cada medicamento

trata(paracetamol,     gripe).
trata(paracetamol,     resfriado).
trata(paracetamol,     covid19).
trata(paracetamol,     sinusitis).

trata(ibuprofeno,      gripe).
trata(ibuprofeno,      resfriado).
trata(ibuprofeno,      sinusitis).

trata(antihistaminico, resfriado).
trata(antihistaminico, sinusitis).

trata(omeprazol,       gastritis).

trata(amoxicilina,  sinusitis).
trata(azitromicina,    sinusitis).


% Contraindicaciones ------------------------------------
%  contraindicado_alergia(Medicamento, Alergia).
%  contraindicado_condicion(Medicamento, Condicion).
% -------------------------------------------------------
contraindicado_alergia(ibuprofeno,      alergia_aines).
contraindicado_alergia(antihistaminico, alergia_antihistaminicos).
contraindicado_alergia(amoxicilina,     alergia_penicilina).

contraindicado_condicion(ibuprofeno, insuficiencia_renal).
contraindicado_condicion(ibuprofeno, gastritis_cronica).
contraindicado_condicion(omeprazol,  insuficiencia_hepatica).


% ============================================================
% UTILIDADES (Reglas de Inferencia)
% ============================================================

% Borra todos los datos del paciente actual de la memoria
limpiar_paciente :-
    retractall(sintoma_paciente(_, _)),
    retractall(alergia_paciente(_)),
    retractall(condicion_paciente(_)).

% multiplicador para la severidad
%   leve=1, moderado=2, severo=3
multiplicador_severidad(leve,     1).
multiplicador_severidad(moderado, 2).
multiplicador_severidad(severo,   3).

% Lista todas las enfermedades registradas
listar_enfermedades(E) :- enfermedad(E, _, _, _).

%**

% --- Componente de puntaje (un síntoma ingresado que coincide) ---
%     componente_puntaje(Enfermedad, Valor)
componente_puntaje(E, Valor) :-
    sintoma_paciente(S, Sev),
    tiene_sintoma(E, S, Peso),
    multiplicador_severidad(Sev, M),
    Valor is Peso * M.

% --- Puntaje máximo posible (suma pesos * 3 para severidad severo) ---
puntaje_maximo(E, Max) :-
    findall(P, tiene_sintoma(E, _, P), Pesos),
    sum_list(Pesos, SumaPesos),
    Max is SumaPesos * 3.

% --- Puntaje obtenido con los síntomas del paciente ---
puntaje_obtenido(E, Puntaje) :-
    findall(V, componente_puntaje(E, V), Valores),
    sum_list(Valores, Puntaje).

% --- Porcentaje de afinidad normalizado 0-100 ---
porcentaje_afinidad(E, Porcentaje) :-
    puntaje_maximo(E, Max),
    puntaje_obtenido(E, Obtenido),
    ( Max =:= 0
    -> Porcentaje is 0
    ;  PorcentajeF is (Obtenido / Max) * 100,
       round(PorcentajeF, Porcentaje)
    ).

% --- Nivel de urgencia ---
% Alta: dolor_pecho severo en enfermedad respiratoria
nivel_urgencia(E, alta) :-
    sintoma_paciente(dolor_pecho, severo),
    enfermedad(E, _, respiratorio, _).

% Media: afinidad >= 60%
nivel_urgencia(E, media) :-
    porcentaje_afinidad(E, P),
    P >= 60,
    not((sintoma_paciente(dolor_pecho, severo), enfermedad(E, _, respiratorio, _))).

% Baja: afinidad < 60%
nivel_urgencia(E, baja) :-
    porcentaje_afinidad(E, P),
    P < 60.

% --- Medicamento inseguro para el paciente actual ---
medicamento_inseguro(M) :-
    alergia_paciente(A),
    contraindicado_alergia(M, A).

medicamento_inseguro(M) :-
    condicion_paciente(C),
    contraindicado_condicion(M, C).

% --- Medicamento seguro para una enfermedad ---
medicamento_seguro_para(E, M) :-
    trata(M, E),
    not(medicamento_inseguro(M)).

% --- Síntomas que coincidieron (explicación del diagnóstico) ---
sintomas_coincidentes(E, S) :-
    sintoma_paciente(S, _),
    tiene_sintoma(E, S, _).

% --- Regla principal de diagnóstico ---
%     diagnosticar(Enfermedad, Porcentaje, Urgencia)
diagnosticar(E, Porcentaje, Urgencia) :-
    enfermedad(E, _, _, _),
    porcentaje_afinidad(E, Porcentaje),
    Porcentaje > 0,
    nivel_urgencia(E, Urgencia).