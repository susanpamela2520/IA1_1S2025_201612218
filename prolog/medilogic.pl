%   MediLogic - Base de Conocimiento en Prolog
%   USAC Facultad de Ingenieria - IA1 2026 - Carnet: 201612218

% ----------------------------------------------------------
% Predicados dinamicos
% Se modifican en tiempo de ejecucion desde Python por paciente.
% ----------------------------------------------------------
:- dynamic sintoma_paciente/2.    % sintoma_paciente(nombre_sintoma, severidad)
:- dynamic alergia_paciente/1.    % alergia_paciente(nombre_alergia)
:- dynamic condicion_paciente/1.  % condicion_paciente(nombre_condicion_cronica)

% Permite que los hechos de estos predicados aparezcan en cualquier
% orden dentro del archivo sin generar warnings de SWI-Prolog.
:- discontiguous contraindicado_alergia/2.
:- discontiguous contraindicado_condicion/2.
:- discontiguous trata/2.
:- discontiguous tiene_sintoma/3.


% ============================================================
% CATALOGO DE SINTOMAS
% Administrado por el modulo Admin
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
enfermedad(gripe,     'Infeccion viral comun con fiebre y malestar general',           respiratorio, viral).
enfermedad(resfriado, 'Cuadro leve respiratorio con congestion y tos',                 respiratorio, viral).
enfermedad(covid19,   'Infeccion viral respiratoria con fiebre tos y fatiga',          respiratorio, viral).
enfermedad(gastritis, 'Inflamacion del estomago con nausea y malestar',                digestivo,    agudo).
enfermedad(sinusitis, 'Inflamacion de los senos paranasales con congestion facial',    respiratorio, bacteriano).

% ============================================================
% SINTOMAS POR ENFERMEDAD CON PESO
%   tiene_sintoma(Enfermedad, Sintoma, Peso).
%   Peso: 1 (poco relevante) a 5 (muy relevante).
% ============================================================
tiene_sintoma(gripe, fiebre,           5).
tiene_sintoma(gripe, tos,              4).
tiene_sintoma(gripe, fatiga,           4).
tiene_sintoma(gripe, dolor_cabeza,     3).
tiene_sintoma(gripe, dolor_garganta,   3).

tiene_sintoma(resfriado, congestion_nasal, 5).
tiene_sintoma(resfriado, tos,              3).
tiene_sintoma(resfriado, dolor_garganta,   3).
tiene_sintoma(resfriado, dolor_cabeza,     2).
tiene_sintoma(resfriado, fiebre,           1).

tiene_sintoma(covid19, fatiga,             5).
tiene_sintoma(covid19, fiebre,             4).
tiene_sintoma(covid19, tos,                4).
tiene_sintoma(covid19, dolor_pecho,        3).
tiene_sintoma(covid19, dolor_cabeza,       3).

tiene_sintoma(gastritis, nausea,           5).
tiene_sintoma(gastritis, vomito,           4).
tiene_sintoma(gastritis, fatiga,           2).
tiene_sintoma(gastritis, diarrea,          1).
tiene_sintoma(gastritis, dolor_cabeza,     1).

tiene_sintoma(sinusitis, congestion_nasal, 5).
tiene_sintoma(sinusitis, dolor_cabeza,     4).
tiene_sintoma(sinusitis, fiebre,           3).
tiene_sintoma(sinusitis, dolor_garganta,   2).
tiene_sintoma(sinusitis, fatiga,           2).

% ============================================================
% MEDICAMENTOS
% ============================================================
medicamento(paracetamol).
medicamento(ibuprofeno).
medicamento(antihistaminico).
medicamento(omeprazol).
medicamento(amoxicilina).
medicamento(azitromicina).

% Tratamientos
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
trata(amoxicilina,     sinusitis).
trata(azitromicina,    sinusitis).

% Contraindicaciones
contraindicado_alergia(ibuprofeno,      alergia_aines).
contraindicado_alergia(antihistaminico, alergia_antihistaminicos).
contraindicado_alergia(amoxicilina,     alergia_penicilina).

contraindicado_condicion(ibuprofeno, insuficiencia_renal).
contraindicado_condicion(ibuprofeno, gastritis_cronica).
contraindicado_condicion(omeprazol,  insuficiencia_hepatica).


% ============================================================
% REGLAS DE INFERENCIA
% ============================================================

% --- Limpiar perfil del paciente actual ---
limpiar_paciente :-
    retractall(sintoma_paciente(_, _)),
    retractall(alergia_paciente(_)),
    retractall(condicion_paciente(_)).

% --- Multiplicador de severidad ---
%     Uso de CORTE (!) para evitar backtracking innecesario
%     una vez encontrada la severidad correcta.
multiplicador_severidad(leve,     1) :- !.
multiplicador_severidad(moderado, 2) :- !.
multiplicador_severidad(severo,   3) :- !.

% --- Listar enfermedades ---
listar_enfermedades(E) :- enfermedad(E, _, _, _).

% --- Componente de puntaje por sintoma coincidente ---
componente_puntaje(E, Valor) :-
    sintoma_paciente(S, Sev),
    tiene_sintoma(E, S, Peso),
    multiplicador_severidad(Sev, M),
    Valor is Peso * M.

% --- Puntaje maximo posible (suma de pesos * 3) ---
puntaje_maximo(E, Max) :-
    findall(P, tiene_sintoma(E, _, P), Pesos),
    sumar_lista(Pesos, SumaPesos),
    Max is SumaPesos * 3.

% --- Puntaje obtenido con sintomas del paciente ---
puntaje_obtenido(E, Puntaje) :-
    findall(V, componente_puntaje(E, V), Valores),
    sumar_lista(Valores, Puntaje).

% ============================================================
% RECURSION: sumar_lista/2
%   Implementacion recursiva propia para sumar los elementos
%   de una lista. Equivale a sum_list pero definida manualmente
%   para demostrar uso de recursion en Prolog.
%
%   Caso base: lista vacia suma 0.
%   Caso recursivo: suma cabeza + resultado recursivo de la cola.
% ============================================================
sumar_lista([], 0).
sumar_lista([Cabeza|Cola], Suma) :-
    sumar_lista(Cola, SumaCola),
    Suma is Cabeza + SumaCola.

% --- Porcentaje de afinidad normalizado 0-100 ---
%     Uso de CORTE en rama de Max=0 para evitar division por cero.
porcentaje_afinidad(E, 0) :-
    puntaje_maximo(E, 0), !.
porcentaje_afinidad(E, Porcentaje) :-
    puntaje_maximo(E, Max),
    puntaje_obtenido(E, Obtenido),
    PorcentajeF is (Obtenido / Max) * 100,
    round(PorcentajeF, Porcentaje).

% --- Nivel de urgencia ---
%     Uso de CORTE en cada clausula para garantizar determinismo:
%     una vez que se encuentra el nivel, no se sigue buscando.

% Alta: dolor de pecho severo + enfermedad respiratoria
nivel_urgencia(E, alta) :-
    sintoma_paciente(dolor_pecho, severo),
    enfermedad(E, _, respiratorio, _), !.

% Media: afinidad >= 60%
nivel_urgencia(E, media) :-
    porcentaje_afinidad(E, P),
    P >= 60, !.

% Baja: cualquier otro caso
nivel_urgencia(_, baja).

% --- Medicamento inseguro para el paciente actual ---
%     Uso de CORTE: si ya encontramos una razon de riesgo,
%     no necesitamos seguir buscando otras.
medicamento_inseguro(M) :-
    alergia_paciente(A),
    contraindicado_alergia(M, A), !.
medicamento_inseguro(M) :-
    condicion_paciente(C),
    contraindicado_condicion(M, C), !.

% --- Medicamento seguro para una enfermedad ---
medicamento_seguro_para(E, M) :-
    trata(M, E),
    not(medicamento_inseguro(M)).

% --- Sintomas del paciente que coincidieron con la enfermedad ---
%     Usado para explicar la inferencia al usuario.
sintomas_coincidentes(E, S) :-
    sintoma_paciente(S, _),
    tiene_sintoma(E, S, _).

% ============================================================
% LISTAS: obtener_sintomas_paciente/1
%   Recopila en una lista todos los sintomas actuales del paciente.
%   Demuestra uso de findall para construir listas dinamicamente.
% ============================================================
obtener_sintomas_paciente(Lista) :-
    findall(S, sintoma_paciente(S, _), Lista).

% ============================================================
% REGLA PRINCIPAL DE DIAGNOSTICO
%   diagnosticar(Enfermedad, Porcentaje, Urgencia)
%   Llamada desde Python via pyswip para cada consulta.
% ============================================================
diagnosticar(E, Porcentaje, Urgencia) :-
    enfermedad(E, _, _, _),
    porcentaje_afinidad(E, Porcentaje),
    Porcentaje > 0,
    nivel_urgencia(E, Urgencia).