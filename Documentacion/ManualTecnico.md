# MediLogic — Manual Técnico
**Universidad San Carlos de Guatemala · Facultad de Ingeniería · IA1 · 2026**  
**Estudiante:** Susan Pamela Herrera Monzon · **Carné:** 201612218

---

## 1. Descripción General del Sistema

MediLogic es una aplicación de escritorio desarrollada en Python con interfaz gráfica Tkinter, que implementa un sistema experto basado en lógica declarativa Prolog. El sistema permite a un paciente ingresar sus síntomas con nivel de severidad, alergias y condiciones crónicas, para obtener un diagnóstico preliminar con porcentaje de afinidad, nivel de urgencia y sugerencia segura de medicamentos.

El motor de inferencia se implementa completamente en Prolog. Python actúa como capa de presentación e integración mediante la biblioteca **pyswip**, que expone el motor SWI-Prolog como un módulo callable desde Python.

---

## 2. Patrón de Arquitectura — MVC

El proyecto sigue el patrón **MVC (Model - View - Controller)**:

| Capa | Tecnología | Responsabilidad |
|---|---|---|
| **Model** | SWI-Prolog (.pl) + PLManager | Base de conocimiento, hechos y reglas de inferencia |
| **View** | Python / Tkinter | Vistas: Home, Login, Paciente, Admin |
| **Controller** | Python / pyswip (PrologEngine) | Coordina la comunicación entre UI y Prolog |
| **Automatización** | Python / PyAutoGUI | RPA de carga masiva y notificación email |

---

## 3. Estructura de Archivos

```
P1/
├── main.py                  # Punto de entrada, controlador de vistas
├── auth.py                  # Servicio de autenticación (admin/1234)
├── requirements.txt         # Dependencias Python
├── backend/
│   ├── prolog_engine.py     # Motor de inferencia (pyswip <-> Prolog)
│   ├── pl_manager.py        # Lector/escritor del archivo .pl
│   └── pdf_generator.py     # Generador de informes PDF
├── prolog/
│   └── medilogic.pl         # Base de conocimiento Prolog
├── ui/
│   ├── styles.py            # Paleta de colores y estilos ttk
│   ├── home_view.py         # Pantalla de inicio
│   ├── login_view.py        # Login administrativo
│   ├── patient_view.py      # Módulo paciente
│   └── admin_view.py        # Módulo admin: CRUD
└── rpa/
    ├── rpa_carga.py         # Script RPA
    └── input_ejemplo.txt    # Archivo de entrada de ejemplo
```

---

## 4. Base de Conocimiento Prolog (medilogic.pl)

### 4.1 Predicados Dinámicos

Se declaran dinámicos porque son afirmados (`assertz`) y retractados (`retractall`) desde Python en cada consulta del paciente:

```prolog
:- dynamic sintoma_paciente/2.    "sintoma_paciente(nombre_sintoma, severidad)"
:- dynamic alergia_paciente/1.    "alergia_paciente(nombre_alergia)"
:- dynamic condicion_paciente/1.  "condicion_paciente(nombre_condicion_cronica)"
```

### 4.2 Hechos Estáticos

| Hecho | Descripción | Ejemplo |
|---|---|---|
| `enfermedad/4` | Nombre, descripción, sistema, tipo | `enfermedad(gripe, '...', respiratorio, viral).` |
| `sintoma/1` | Catálogo de síntomas válidos | `sintoma(fiebre).` |
| `tiene_sintoma/3` | Enfermedad, síntoma, peso (1-5) | `tiene_sintoma(gripe, fiebre, 5).` |
| `medicamento/1` | Medicamentos disponibles | `medicamento(paracetamol).` |
| `trata/2` | Medicamento trata enfermedad | `trata(paracetamol, gripe).` |
| `contraindicado_alergia/2` | Medicamento contraindicado por alergia | `contraindicado_alergia(ibuprofeno, alergia_aines).` |
| `contraindicado_condicion/2` | Medicamento contraindicado por condición | `contraindicado_condicion(ibuprofeno, insuficiencia_renal).` |

### 4.3 Uso de Cortes (!)

Se usa el operador de **corte (!)** para lograr determinismo. Sin corte, Prolog intentaría satisfacer cláusulas alternativas innecesariamente:

```prolog
% Corte en multiplicador_sev: una vez encontrada la severidad, no seguir buscando
multiplicador_sev(leve,     1) :- !.
multiplicador_sev(moderado, 2) :- !.
multiplicador_sev(severo,   3) :- !.

% Corte en nivel_urgencia: garantiza que solo se evalúe un nivel
nivel_urgencia(E, alta) :-
    sintoma_paciente(dolor_pecho, severo),
    enfermedad(E, _, respiratorio, _), !.

nivel_urgencia(E, media) :-
    porcentaje_afinidad(E, P),
    P >= 60, !.

nivel_urgencia(_, baja).
```

### 4.4 Recursión: sumar_lista/2

Implementación recursiva propia para sumar listas, demostrando el uso de recursión en Prolog mediante el patrón cabeza-cola:

```prolog
% Caso base: lista vacía suma 0
sumar_lista([], 0).

% Caso recursivo: suma la cabeza más el resultado de la cola
sumar_lista([Cabeza|Cola], Suma) :-
    sumar_lista(Cola, SumaCola),
    Suma is Cabeza + SumaCola.
```

### 4.5 Listas: obtener_sintomas_paciente/1

Uso de `findall/3` para construir dinámicamente una lista con los síntomas del paciente:

```prolog
obtener_sintomas_paciente(Lista) :-
    findall(S, sintoma_paciente(S, _), Lista).
```

---

## 5. Motor de Inferencia Python (prolog_engine.py)

### 5.1 Conexión Python — Prolog

```python
from pyswip import Prolog

prolog = Prolog()
prolog.consult("prolog/medilogic.pl")   # Carga el .pl

# Cargar perfil del paciente (assertz desde Python)
prolog.query("assertz(sintoma_paciente(fiebre, severo)).")
prolog.query("assertz(alergia_paciente(alergia_aines)).")

# Ejecutar diagnóstico
for r in prolog.query("diagnosticar(E, P, U)."):
    print(f"Enfermedad: {r['E']}, Afinidad: {r['P']}%, Urgencia: {r['U']}")
```

### 5.2 Las 5 Queries del Proyecto

| Query | Método Python | Consulta Prolog | Retorna |
|---|---|---|---|
| Q1 | `q1_listar_enfermedades()` | `listar_enfermedades(E).` | Lista de enfermedades |
| Q2 | `q2_afinidad_todas()` | `enfermedad(E,_,_,_), porcentaje_afinidad(E,P).` | Dict {enfermedad: %} |
| Q3 | `q3_diagnosticar_todo()` | `diagnosticar(E,P,U).` | Lista ordenada por afinidad |
| Q4 | `q4_medicamentos_seguros(E)` | `medicamento_seguro_para(E,M).` | Lista de medicamentos seguros |
| Q5 | `q5_sintomas_que_coincidieron(E)` | `sintomas_coincidentes(E,S).` | Lista de síntomas coincidentes |

### 5.3 Recarga del Motor

```python
def recargar(self) -> None:
    # pyswip es singleton global, NO se puede hacer Prolog() de nuevo
    # Se usa load_files con if(true) para forzar recarga
    ruta_abs = os.path.abspath(self.ruta_archivo).replace("\\", "/")
    list(self.prolog.query(f"load_files('{ruta_abs}', [if(true)])."))
```

---

## 6. Módulo Administrador (admin_view.py)

Permite gestionar la base de conocimiento en tiempo real sin editar el `.pl` manualmente:

| Pestaña | Funcionalidad |
|---|---|
| **Enfermedades** | Agregar, editar y eliminar enfermedades con sus síntomas y pesos |
| **Medicamentos** | Agregar, editar y eliminar medicamentos con contraindicaciones |
| **Síntomas** | Gestionar el catálogo de síntomas disponibles |
| **Archivo .pl** | Ver contenido, cargar archivo externo, exportar copia |

### Flujo de actualización en tiempo real

```
1. Admin hace cambios en la interfaz (CRUD)
2. Presiona "Guardar y Recargar"
3. PLManager.guardar() → reescribe medilogic.pl en disco
4. engine.recargar() → load_files() recarga el .pl en Prolog
5. Los siguientes diagnósticos ya usan los datos actualizados
```

---

## 7. RPA — Automatización (rpa_carga.py)

El script RPA carga enfermedades masivamente desde un archivo TXT:

### Formato del archivo de entrada

```
ENFERMEDAD: neumonia
DESCRIPCION: Infeccion que inflama los sacos de aire
SISTEMA: respiratorio
TIPO: bacteriano
SINTOMAS: fiebre:4, tos:5, fatiga:4, dolor_pecho:5
MEDICAMENTOS: amoxicilina, paracetamol
CONTRA_ALERGIA: amoxicilina:alergia_penicilina
CONTRA_CONDICION:
---
```

### Ejecución

```bash
# Carga directa (sin email)
python rpa/rpa_carga.py --archivo rpa/input_ejemplo.txt

# Con envío de email
python rpa/rpa_carga.py --archivo rpa/input_ejemplo.txt \
    --email admin@correo.com \
    --smtp_user tucorreo@gmail.com \
    --smtp_pass APP_PASSWORD
```

### Flujo del RPA

```
Paso 1: Leer y parsear el archivo TXT bloque por bloque
Paso 2: Normalizar campos (lowercase, guiones bajos)
Paso 3: Cargar al PLManager (actualiza objetos en memoria)
Paso 4: PLManager.guardar() → reescribe medilogic.pl
Paso 5: Generar bitácora de texto plano con timestamps
Paso 6: Guardar bitácora local o enviar por SMTP
```

---

## 8. Decisiones de Diseño

| Decisión | Justificación |
|---|---|
| **Cortes en nivel_urgencia** | Garantiza que solo se evalúe un nivel de urgencia por enfermedad. Sin corte, Prolog intentaría todas las cláusulas. |
| **Recursión propia sumar_lista** | Demuestra dominio de Prolog puro. El patrón `[Cabeza\|Cola]` es la forma idiomática de procesar listas. |
| **assertz/retractall para perfil** | Permite limpiar y recargar el perfil del paciente por consulta sin reiniciar el motor Prolog. |
| **PLManager como parser/writer** | Separa la lógica de lectura/escritura del .pl de la lógica de diagnóstico (principio de responsabilidad única). |
| **Patrón MVC** | Facilita el mantenimiento: se puede cambiar la UI sin tocar la lógica Prolog, y viceversa. |
| **pyswip como puente** | Biblioteca estándar para integrar SWI-Prolog con Python, estable y sin necesidad de servidor. |

---

