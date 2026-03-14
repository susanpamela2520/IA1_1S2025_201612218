import argparse
import datetime
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Agregar el directorio raiz al path para poder importar los modulos del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.pl_manager import PLManager, Enfermedad, Medicamento

# Parsear el archivo TXT
# Lee el archivo bloque por bloque separados por "---"

def parsear_archivo(ruta: str) -> list:
    """Lee el archivo .txt y retorna lista de dicts con los datos de cada enfermedad."""
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")

    bloques = []
    bloque_actual = {}

    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            # Ignorar comentarios y lineas vacias
            if not linea or linea.startswith("#"):
                continue
            # El separador "---" indica fin de un bloque
            if linea == "---":
                if bloque_actual:
                    bloques.append(bloque_actual)
                    bloque_actual = {}
                continue
            # Separar clave: valor
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                bloque_actual[clave.strip().upper()] = valor.strip()

    # Agregar ultimo bloque si no tenia "---" al final
    if bloque_actual:
        bloques.append(bloque_actual)

    return bloques


def normalizar_bloque(bloque: dict) -> dict:
    """Convierte un bloque raw del TXT a un dict con los campos normalizados."""
    e = {
        "nombre":       bloque.get("ENFERMEDAD", "").strip().lower().replace(" ", "_"),
        "descripcion":  bloque.get("DESCRIPCION", "Sin descripcion"),
        "sistema":      bloque.get("SISTEMA", "respiratorio").strip().lower(),
        "tipo":         bloque.get("TIPO", "viral").strip().lower(),
        "sintomas":     [],
        "medicamentos": [],
        "contra_a":     [],  # contraindicaciones por alergia
        "contra_c":     [],  # contraindicaciones por condicion
    }

    # Parsear sintomas: "fiebre:5, tos:3" -> [("fiebre", 5), ("tos", 3)]
    for par in bloque.get("SINTOMAS", "").split(","):
        par = par.strip()
        if ":" in par:
            s, p = par.split(":", 1)
            try:
                e["sintomas"].append((s.strip(), int(p.strip())))
            except ValueError:
                pass
        elif par:
            e["sintomas"].append((par, 3))  # peso por defecto

    # Parsear medicamentos: "amoxicilina, paracetamol"
    e["medicamentos"] = [m.strip() for m in bloque.get("MEDICAMENTOS", "").split(",") if m.strip()]

    # Parsear contraindicaciones: "ibuprofeno:alergia_aines"
    for par in bloque.get("CONTRA_ALERGIA", "").split(","):
        par = par.strip()
        if ":" in par:
            med, alergia = par.split(":", 1)
            e["contra_a"].append((med.strip(), alergia.strip()))

    for par in bloque.get("CONTRA_CONDICION", "").split(","):
        par = par.strip()
        if ":" in par:
            med, cond = par.split(":", 1)
            e["contra_c"].append((med.strip(), cond.strip()))

    return e



# Cargar las enfermedades al PLManager y guardar el .pl
# Este es el "backend del RPA" - no usa interfaz grafica

def cargar_enfermedades(enfermedades: list, pl_ruta: str) -> list:
    """
    Carga las enfermedades directamente al PLManager.
    Actualiza el archivo medilogic.pl sin abrir la interfaz grafica.
    Retorna la bitacora de lo que hizo.
    """
    mgr = PLManager(pl_ruta)
    bitacora = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bitacora.append(f"{'='*60}")
    bitacora.append(f"  MediLogic RPA - Inicio de carga")
    bitacora.append(f"  Fecha y hora: {ts}")
    bitacora.append(f"  Archivo .pl: {pl_ruta}")
    bitacora.append(f"  Enfermedades a cargar: {len(enfermedades)}")
    bitacora.append(f"{'='*60}")

    cargadas = 0
    errores = 0

    for e in enfermedades:
        try:
            if not e["nombre"]:
                raise ValueError("Nombre de enfermedad vacio")

            # Agregar la enfermedad al PLManager
            nueva = Enfermedad(
                nombre=e["nombre"],
                descripcion=e["descripcion"],
                sistema=e["sistema"],
                tipo=e["tipo"],
                sintomas=e["sintomas"],
            )
            mgr.agregar_enfermedad(nueva)

            # Agregar o actualizar medicamentos asociados
            for nombre_med in e["medicamentos"]:
                if nombre_med not in mgr.medicamentos:
                    mgr.agregar_medicamento(Medicamento(nombre_med))
                # Asociar medicamento con la enfermedad
                if e["nombre"] not in mgr.medicamentos[nombre_med].trata:
                    mgr.medicamentos[nombre_med].trata.append(e["nombre"])

            # Agregar contraindicaciones por alergia
            for med_c, alergia in e["contra_a"]:
                if med_c in mgr.medicamentos:
                    if alergia not in mgr.medicamentos[med_c].contra_alergia:
                        mgr.medicamentos[med_c].contra_alergia.append(alergia)

            # Agregar contraindicaciones por condicion
            for med_c, cond in e["contra_c"]:
                if med_c in mgr.medicamentos:
                    if cond not in mgr.medicamentos[med_c].contra_condicion:
                        mgr.medicamentos[med_c].contra_condicion.append(cond)

            registro = (
                f"[OK]  {ts} | '{e['nombre']}' cargada | "
                f"sistema={e['sistema']} | tipo={e['tipo']} | "
                f"sintomas={len(e['sintomas'])} | "
                f"medicamentos={', '.join(e['medicamentos']) or 'ninguno'}"
            )
            print(registro)
            bitacora.append(registro)
            cargadas += 1

        except Exception as ex:
            registro = f"[ERROR] {ts} | '{e.get('nombre', '?')}': {ex}"
            print(registro)
            bitacora.append(registro)
            errores += 1

    # Guardar el archivo .pl actualizado
    mgr.guardar()

    resumen = (
        f"\n{'='*60}\n"
        f"  RESUMEN FINAL\n"
        f"  Enfermedades cargadas exitosamente: {cargadas}\n"
        f"  Errores: {errores}\n"
        f"  Archivo .pl actualizado: {pl_ruta}\n"
        f"{'='*60}"
    )
    print(resumen)
    bitacora.append(resumen)

    return bitacora



# Guardar bitacora como texto plano

def guardar_bitacora_local(bitacora: list) -> str:
    """Guarda la bitacora en un archivo .txt con timestamp en el nombre."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(BASE_DIR, f"rpa_bitacora_{ts}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(bitacora))
    print(f"\n[LOG] Bitacora guardada en: {ruta}")
    return ruta

# Enviar bitacora por correo (opcional)
# Requiere Gmail App Password: myaccount.google.com/apppasswords

def enviar_email(bitacora: list, destinatario: str,
                 smtp_user: str, smtp_pass: str) -> None:
    """Envia la bitacora por correo electronico al administrador."""
    asunto = f"MediLogic RPA - Bitacora de carga {datetime.date.today()}"
    cuerpo  = "\n".join(bitacora)

    msg = MIMEMultipart()
    msg["From"]    = smtp_user
    msg["To"]      = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, destinatario, msg.as_string())
        print(f"[EMAIL] Bitacora enviada correctamente a: {destinatario}")
    except Exception as ex:
        print(f"[EMAIL-ERROR] No se pudo enviar: {ex}")
        print("[EMAIL] Guardando bitacora localmente...")
        guardar_bitacora_local(bitacora)

#Entrada RPA

def main():
    parser = argparse.ArgumentParser(
        description="MediLogic RPA - Carga masiva de enfermedades desde archivo TXT"
    )
    parser.add_argument(
        "--archivo",
        default=os.path.join(os.path.dirname(__file__), "input_ejemplo.txt"),
        help="Ruta al archivo .txt con las enfermedades a cargar"
    )
    parser.add_argument(
        "--email",
        default="",
        help="Email destinatario para enviar la bitacora"
    )
    parser.add_argument(
        "--smtp_user",
        default="",
        help="Tu correo Gmail para enviar la bitacora"
    )
    parser.add_argument(
        "--smtp_pass",
        default="",
        help="App Password de Gmail (no la contrasena normal)"
    )
    args = parser.parse_args()

    # Ruta al archivo .pl del proyecto
    pl_ruta = os.path.join(BASE_DIR, "prolog", "medilogic.pl")

    print(f"\n{'='*60}")
    print(f"  MediLogic RPA - Iniciando")
    print(f"  Archivo de entrada: {args.archivo}")
    print(f"  Archivo .pl destino: {pl_ruta}")
    print(f"{'='*60}\n")

    # Paso 1: Leer y parsear el archivo TXT
    print("[PASO 1] Leyendo archivo de entrada...")
    bloques_raw   = parsear_archivo(args.archivo)
    enfermedades  = [normalizar_bloque(b) for b in bloques_raw]
    print(f"         Se encontraron {len(enfermedades)} enfermedad(es) para cargar.\n")

    # Paso 2: Cargar al PLManager y guardar el .pl
    print("[PASO 2] Cargando enfermedades al sistema...")
    bitacora = cargar_enfermedades(enfermedades, pl_ruta)

    # Paso 3: Guardar bitacora local o enviar por email
    if args.email and args.smtp_user and args.smtp_pass:
        print(f"\n[PASO 3] Enviando bitacora por correo a {args.email}...")
        enviar_email(bitacora, args.email, args.smtp_user, args.smtp_pass)
    else:
        print("\n[PASO 3] Guardando bitacora como archivo de texto...")
        guardar_bitacora_local(bitacora)

    print("\n[RPA] Proceso finalizado exitosamente.")


if __name__ == "__main__":
    main()