%   MediLogic — Base de Conocimiento en Prolog

% ----------------------------------------------------------
% SECCIÓN 0: Predicados dinámicos
%   "Dinámico" significa que estos hechos se agregan y borran
%   en tiempo de ejecución (desde Python) para cada paciente.
% ----------------------------------------------------------
:- dynamic sintoma_paciente/2.    % sintoma_paciente(nombre_sintoma, severidad)
:- dynamic alergia_paciente/1.    % alergia_paciente(nombre_alergia)
:- dynamic condicion_paciente/1.  % condicion_paciente(nombre_condicion_cronica)


% ============================================================
% SECCIÓN 1: CATÁLOGO DE SÍNTOMAS
%   Solo sirve como referencia/documentación.
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
% SECCIÓN 2: ENFERMEDADES
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
% SECCIÓN 3: SÍNTOMAS POR ENFERMEDAD CON PESO
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
% SECCIÓN 4: MEDICAMENTOS
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

