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

#Se carga directamente al PLManager 
#localemnte 
#puede dar la lista de registros

def cargar_via_pl_manager(enfermedades: list, pl_ruta: str) -> list:
    """
    Método principal: carga las enfermedades directamente al PLManager,
    sin necesidad de interfaz gráfica.
    Retorna lista de registros de bitácora.
    """
    from backend.pl_manager import PLManager, Enfermedad, Medicamento

    mgr = PLManager(pl_ruta)
    bitacora = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for e in enfermedades:
        try:
            # Agregar enfermedad
            nueva = Enfermedad(
                nombre=e["nombre"],
                descripcion=e["descripcion"],
                sistema=e["sistema"],
                tipo=e["tipo"],
                sintomas=e["sintomas"],
            )
            mgr.agregar_enfermedad(nueva)

            # Agregar / actualizar medicamentos
            for nombre_med in e["medicamentos"]:
                if nombre_med not in mgr.medicamentos:
                    mgr.agregar_medicamento(Medicamento(nombre_med))
                mgr.medicamentos[nombre_med].trata.append(e["nombre"])
                # Evitar duplicados
                mgr.medicamentos[nombre_med].trata = list(
                    set(mgr.medicamentos[nombre_med].trata)
                )

            # Contraindicaciones alergia
            for med_c, alergia in e["contra_a"]:
                if med_c in mgr.medicamentos:
                    if alergia not in mgr.medicamentos[med_c].contra_alergia:
                        mgr.medicamentos[med_c].contra_alergia.append(alergia)

            # Contraindicaciones condición
            for med_c, cond in e["contra_c"]:
                if med_c in mgr.medicamentos:
                    if cond not in mgr.medicamentos[med_c].contra_condicion:
                        mgr.medicamentos[med_c].contra_condicion.append(cond)

            registro = (
                f"[OK]  {ts} | Enfermedad '{e['nombre']}' cargada | "
                f"Sistema: {e['sistema']} | Tipo: {e['tipo']} | "
                f"Síntomas: {len(e['sintomas'])} | "
                f"Medicamentos: {', '.join(e['medicamentos']) or 'ninguno'}"
            )
            print(registro)
            bitacora.append(registro)

        except Exception as ex:
            registro = f"[ERROR] {ts} | Enfermedad '{e['nombre']}': {ex}"
            print(registro)
            bitacora.append(registro)

    # Guardar el .pl actualizado
    mgr.guardar()
    fin = f"\n[FIN] {ts} | Total cargadas: {len(enfermedades)} | Archivo .pl actualizado."
    print(fin)
    bitacora.append(fin)

    return bitacora

#Carga por GUI con pyautogui

def _localizar_o_error(imagen: str, timeout: int = 5) -> tuple:
    """Espera hasta encontrar una imagen en pantalla."""
    for _ in range(timeout * 2):
        pos = pyautogui.locateCenterOnScreen(imagen, confidence=0.8)
        if pos:
            return pos
        time.sleep(0.5)
    raise RuntimeError(f"No se encontró elemento en pantalla: {imagen}")


def cargar_via_gui(enfermedades: list) -> list:
    """
    Carga usando PyAutoGUI para interactuar con la aplicación en ejecución.
    NOTA: La aplicación debe estar abierta y en la pantalla de Admin.
    Esta función asume que la app está visible y el panel de Enfermedades activo.
    """
    if not PYAUTOGUI_OK:
        print("[SIMULACIÓN] PyAutoGUI no disponible — ejecutando en modo simulación.")
        return ["[SIMULACIÓN] Carga GUI simulada (PyAutoGUI no instalado)"]

    bitacora = []
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for e in enfermedades:
        try:
            print(f"[RPA] Procesando: {e['nombre']}")

            # Clic en botón "+ Nueva" de la pestaña Enfermedades
            pyautogui.hotkey("alt", "tab")  # traer la app al frente
            time.sleep(PAUSA_LARGA)

            # Buscar y hacer clic en campo "Nombre"
            # (posición relativa al centro de la pantalla — ajustar si es necesario)
            w, h = pyautogui.size()
            campo_nombre_x = int(w * 0.60)
            campo_nombre_y = int(h * 0.35)

            # Limpiar y escribir nombre
            pyautogui.click(campo_nombre_x, campo_nombre_y)
            pyautogui.hotkey("ctrl", "a")
            pyautogui.typewrite(e["nombre"], interval=PAUSA_ESCR)
            time.sleep(PAUSA_CLICK)

            # Descripción
            pyautogui.press("tab")
            pyautogui.hotkey("ctrl", "a")
            pyautogui.typewrite(e["descripcion"][:80], interval=PAUSA_ESCR)

            registro = f"[RPA-GUI] {ts} | '{e['nombre']}' ingresado por GUI"
            print(registro)
            bitacora.append(registro)

        except Exception as ex:
            registro = f"[RPA-ERROR] {ts} | '{e['nombre']}': {ex}"
            print(registro)
            bitacora.append(registro)

    return bitacora

    #Envio de email

    def enviar_email_bitacora(
    bitacora: list,
    destinatario: str,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    remitente: str = "",
    contrasena: str = "",
) -> None:
    """
    Envía la bitácora de cambios por correo electrónico.
    Para Gmail necesitas una "App Password" (no la contraseña normal).
    """
    if not remitente or not contrasena:
        print("[EMAIL] Credenciales SMTP no configuradas. Guardando bitácora local.")
        _guardar_bitacora_local(bitacora)
        return

    asunto = f"MediLogic RPA — Bitácora de carga {datetime.date.today()}"
    cuerpo  = "\n".join(bitacora)

    msg = MIMEMultipart()
    msg["From"]    = remitente
    msg["To"]      = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(remitente, contrasena)
            server.sendmail(remitente, destinatario, msg.as_string())
        print(f"[EMAIL] Bitácora enviada a {destinatario}")
    except Exception as ex:
        print(f"[EMAIL-ERROR] No se pudo enviar email: {ex}")
        _guardar_bitacora_local(bitacora)


def _guardar_bitacora_local(bitacora: list) -> None:
    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = os.path.join(BASE_DIR, f"rpa_bitacora_{ts}.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(bitacora))
    print(f"[LOG] Bitácora guardada en: {ruta}")


    #Ejecutado linea de comandos 


ef main():
    parser = argparse.ArgumentParser(description="MediLogic RPA — Carga masiva de enfermedades")
    parser.add_argument("--archivo", default="rpa/input_ejemplo.txt",
                        help="Ruta al archivo .txt con las enfermedades a cargar")
    parser.add_argument("--email",   default="",
                        help="Email destinatario de la bitácora")
    parser.add_argument("--smtp_user", default="",
                        help="Usuario/email SMTP para enviar la bitácora")
    parser.add_argument("--smtp_pass", default="",
                        help="Contraseña SMTP (App Password para Gmail)")
    parser.add_argument("--gui",    action="store_true",
                        help="Usar PyAutoGUI para llenar la interfaz gráfica")
    args = parser.parse_args()

    # Ruta al archivo .pl
    pl_ruta = os.path.join(BASE_DIR, "knowledge", "medilogic.pl")

    print(f"\n{'='*60}")
    print(f"  MediLogic RPA — Iniciando carga masiva")
    print(f"  Archivo: {args.archivo}")
    print(f"  Modo:    {'GUI (PyAutoGUI)' if args.gui else 'Directo (PLManager)'}")
    print(f"{'='*60}\n")

    # 1. Parsear archivo
    bloques_raw = parsear_archivo(args.archivo)
    enfermedades = [normalizar_enfermedad(b) for b in bloques_raw]
    print(f"[INFO] Se encontraron {len(enfermedades)} enfermedad(es) para cargar.\n")

    # 2. Cargar
    if args.gui:
        bitacora = cargar_via_gui(enfermedades)
    else:
        bitacora = cargar_via_pl_manager(enfermedades, pl_ruta)

    # 3. Enviar email / guardar bitácora
    if args.email:
        enviar_email_bitacora(
            bitacora,
            destinatario=args.email,
            remitente=args.smtp_user,
            contrasena=args.smtp_pass,
        )
    else:
        _guardar_bitacora_local(bitacora)

    print("\n[RPA] Proceso finalizado.")


if __name__ == "__main__":
    main()
