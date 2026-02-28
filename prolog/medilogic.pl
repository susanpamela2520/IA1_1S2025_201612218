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
% ============================================================
sintoma(fiebre).
sintoma(tos).
sintoma(dolor_garganta).
sintoma(congestion_nasal).
sintoma(dolor_cabeza).
sintoma(dolor_pecho).
sintoma(fatiga).
sintoma(nausea).


% ============================================================
% ENFERMEDADES
%   enfermedad(Nombre, Descripcion, SistemaDelCuerpo, Tipo).
% ============================================================
enfermedad(gripe,
    "Infeccion viral comun con fiebre y malestar general.",
    respiratorio, viral).

enfermedad(resfriado,
    "Cuadro leve respiratorio con congestion y tos.",
    respiratorio, viral).

enfermedad(covid19,
    "Infeccion viral respiratoria con fiebre, tos y fatiga.",
    respiratorio, viral).

enfermedad(gastritis,
    "Inflamacion del estomago con nausea y malestar.",
    digestivo, agudo).


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


% ============================================================
% MEDICAMENTOS
% ============================================================
medicamento(paracetamol).
medicamento(ibuprofeno).
medicamento(antihistaminico).
medicamento(omeprazol).

% Qué enfermedad trata cada medicamento
trata(paracetamol,     gripe).
trata(paracetamol,     resfriado).
trata(paracetamol,     covid19).
trata(ibuprofeno,      gripe).
trata(ibuprofeno,      resfriado).
trata(antihistaminico, resfriado).
trata(omeprazol,       gastritis).

% Medicamentos que NO se deben usar si el paciente tiene cierta alergia
contraindicado_alergia(ibuprofeno,      alergia_aines).
contraindicado_alergia(antihistaminico, alergia_antihistaminicos).

% Medicamentos que NO se deben usar si el paciente tiene cierta condición crónica
contraindicado_condicion(ibuprofeno, insuficiencia_renal).
contraindicado_condicion(ibuprofeno, gastritis_cronica).

% ============================================================
% UTILIDADES
% ============================================================

% Borra todos los datos del paciente actual de la memoria
limpiar_paciente :-
    retractall(sintoma_paciente(_, _)),
    retractall(alergia_paciente(_)),
    retractall(condicion_paciente(_)).

% Convierte la severidad en un número multiplicador
%   leve=1, moderado=2, severo=3
multiplicador_severidad(leve,     1).
multiplicador_severidad(moderado, 2).
multiplicador_severidad(severo,   3).

% Lista todas las enfermedades registradas
listar_enfermedades(E) :- enfermedad(E, _, _, _).


% ============================================================
% CÁLCULO DE AFINIDAD
%   La afinidad mide qué tan probable es que el paciente
%   tenga una enfermedad, en base a los síntomas que reportó.
% ============================================================

% Puntuación que aporta UN síntoma del paciente para una enfermedad
puntuacion_componente(Enfermedad, Valor) :-
    sintoma_paciente(Sintoma, Severidad),
    tiene_sintoma(Enfermedad, Sintoma, Peso),
    multiplicador_severidad(Severidad, Mult),
    Valor is Peso * Mult.

% Puntaje máximo posible (si todos los síntomas fueran "severo")
puntaje_maximo(Enfermedad, Maximo) :-
    findall(Peso, tiene_sintoma(Enfermedad, _, Peso), ListaPesos),
    sum_list(ListaPesos, SumaBase),
    Maximo is SumaBase * 3.

% Puntaje real que obtuvo el paciente para una enfermedad
puntaje_obtenido(Enfermedad, Puntaje) :-
    findall(V, puntuacion_componente(Enfermedad, V), Valores),
    sum_list(Valores, Puntaje).

% Porcentaje de afinidad (0 a 100)
porcentaje_afinidad(Enfermedad, Porcentaje) :-
    puntaje_maximo(Enfermedad, Maximo),
    puntaje_obtenido(Enfermedad, Obtenido),
    ( Maximo =:= 0
    -> Porcentaje is 0
    ;  PReal is (Obtenido / Maximo) * 100,
       round(PReal, Porcentaje)
    ).

% ============================================================
% SECCIÓN 7: NIVEL DE URGENCIA
% ============================================================

% ALTA: dolor de pecho severo con posible covid19
nivel_urgencia(covid19, alta) :-
    sintoma_paciente(dolor_pecho, severo).

% MEDIA: afinidad >= 60%
nivel_urgencia(Enfermedad, media) :-
    porcentaje_afinidad(Enfermedad, P),
    P >= 60.

% BAJA: afinidad < 60%
nivel_urgencia(Enfermedad, baja) :-
    porcentaje_afinidad(Enfermedad, P),
    P < 60.

% ============================================================
% SECCIÓN 8: MEDICAMENTO SEGURO
% ============================================================

% Inseguro si hay alergia que lo contraindica
medicamento_inseguro(Med) :-
    alergia_paciente(Alergia),
    contraindicado_alergia(Med, Alergia).

% Inseguro si hay condición crónica que lo contraindica
medicamento_inseguro(Med) :-
    condicion_paciente(Condicion),
    contraindicado_condicion(Med, Condicion).

% Seguro = trata la enfermedad Y no está contraindicado
medicamento_seguro_para(Enfermedad, Med) :-
    trata(Med, Enfermedad),
    \+ medicamento_inseguro(Med).




% ============================================================
%  EXPLICACIÓN síntomas que coincidieron
%   Para mostrarle al paciente por qué se sugirió la enfermedad
% ============================================================
sintomas_coincidentes(Enfermedad, Sintoma) :-
    sintoma_paciente(Sintoma, _),
    tiene_sintoma(Enfermedad, Sintoma, _).

% ============================================================
% DIAGNÓSTICO FINAL
%   Regla principal que llama Python.
%   diagnosticar(Enfermedad, Porcentaje, Urgencia)
% ============================================================
diagnosticar(Enfermedad, Porcentaje, Urgencia) :-
    enfermedad(Enfermedad, _, _, _),
    porcentaje_afinidad(Enfermedad, Porcentaje),
    Porcentaje > 0,
    nivel_urgencia(Enfermedad, Urgencia).
