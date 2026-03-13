#Aqui se carga masivamente las enfermedades
#lee el archivo.txt con PyAutoGUI
#Se llena el formulario 
#Usa modulo admin y tambien manda el email a la bitacora

import argparse, time, datetime, os, sys, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    import pyautogui
    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False
    print("Advertencia: PyAutoGUI no está instalado. La función de carga masiva no estará disponible.")


## Path al proyecto 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)   

#Contantest de tiempo 
PAUSA_CLICK  = 0.4   # segundos entre clics
PAUSA_ESCR   = 0.05  # pausa entre teclas escritas
PAUSA_LARGA  = 1.0   # espera después de acciones lentas

pyautogui.PAUSE        = PAUSA_CLICK  if PYAUTOGUI_OK else 0
pyautogui.FAILSAFE     = True         if PYAUTOGUI_OK else False

#Parseo del archivo de entrada

def parsear_archivo(ruta:str) -> list:
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"El archivo '{ruta}' no existe.")

    bloques = []
    bloque_actual = {}

    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if linea == "---":
                if bloque_actual:
                    bloques.append(bloque_actual)
                    bloque_actual = {}
                continue
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                clave  = clave.strip().upper()
                valor  = valor.strip()
                bloque_actual[clave] = valor
    if bloque_actual:  # último bloque sin "---"
        bloques.append(bloque_actual)

    return bloques


#Normalizacion de enfermedades

def normalizar_enfermedad(bloque: dict) -> dict:
    """Normaliza y valida los campos de un bloque."""
    e = {
        "nombre":      bloque.get("ENFERMEDAD", "").strip().lower().replace(" ", "_"),
        "descripcion": bloque.get("DESCRIPCION", "Sin descripcion"),
        "sistema":     bloque.get("SISTEMA", "respiratorio").strip().lower(),
        "tipo":        bloque.get("TIPO", "viral").strip().lower(),
        "sintomas":    [],
        "medicamentos":[],
        "contra_a":    [],
        "contra_c":    [],
    }

#Sintomas: "fiebre: 5, tos:3"

    sint_raw = bloque.get("SINTOMAS", "")
    for par in sint_raw.split(","):
        par = par.strip()
        if ":" in par:
            s, p = par.split(":", 1)
            try:
                e["sintomas"].append((s.strip(), int(p.strip())))
            except ValueError:
                pass
        elif par:
            e["sintomas"].append((par, 3))  # peso por defecto

    # Medicamentos simples
    meds_raw = bloque.get("MEDICAMENTOS", "")
    e["medicamentos"] = [m.strip() for m in meds_raw.split(",") if m.strip()]

        # Contraindicaciones
    for par in bloque.get("CONTRA_ALERGIA", "").split(","):
        par = par.strip()
        if ":" in par:
            m, a = par.split(":", 1)
            e["contra_a"].append((m.strip(), a.strip()))

    for par in bloque.get("CONTRA_CONDICION", "").split(","):
        par = par.strip()
        if ":" in par:
            m, c = par.split(":", 1)
            e["contra_c"].append((m.strip(), c.strip()))

    return e


