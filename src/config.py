import os
import shutil
from datetime import datetime
from colorama import Fore, Style, init

EXTENSIONES_IMAGENES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"]
EXTENSIONES_VIDEOS = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"]
EXTENSIONES_DOCUMENTOS = [".txt", ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".ppt", ".pptx", 
                          ".ppsx", ".odt", ".ods", ".odp", ".pdf", ".epub", ".mobi"]
EXTENSIONES_OTROS = [".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".ttf", ".otf"]

LOG_DIR = "Registros"
os.makedirs(LOG_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
LOG_ERRORES = os.path.join(LOG_DIR, f"errores-{TIMESTAMP}.txt")
LOG_OPERACIONES = os.path.join(LOG_DIR, f"operaciones-{TIMESTAMP}.txt")

# INICIO - Registro de errores, función deshacer y apartar archivos problematicos.
def registrar_error(ruta, mensaje, consola=True):
    """
    Registra un error en el archivo y lo muestra en consola.
    """
    with open(LOG_ERRORES, "a", encoding="utf-8") as log:
        log.write(f"{ruta}: {mensaje}\n")
    if consola:
        print(Fore.LIGHTRED_EX + f"[ERROR] {ruta}: {mensaje}" + Style.RESET_ALL)

def registrar_operacion(original, destino, consola=False):
    """
    Registra la operación en el archivo y la muestra en consola.
    """
    with open(LOG_OPERACIONES, "a", encoding="utf-8") as log:
        log.write(f"{original}|{destino}\n")
    if consola:
        print(Fore.LIGHTGREEN_EX + f"[MOVIDO] {original} -> {destino}" + Style.RESET_ALL)

def deshacer_ultima_operacion():
    """
    Deshace la última operación basada en el log de operaciones.
    """
    if not os.path.exists(LOG_OPERACIONES):
        print(Fore.LIGHTYELLOW_EX + "No hay operaciones previas para deshacer." + Style.RESET_ALL)
        return

    confirmacion = input("¿Deseas deshacer la última operación? (s/n): ")
    if confirmacion.lower() != "s":
        print(Fore.LIGHTRED_EX + "Operación cancelada." + Style.RESET_ALL)
        return

    with open(LOG_OPERACIONES, "r") as log:
        operaciones = log.readlines()

    for operacion in reversed(operaciones):
        original, destino = operacion.strip().split("|")
        try:
            os.rename(destino, original)
            print(f"Restaurado: {destino} -> {original}")
        except Exception as e:
            print(f"Error al restaurar {destino}: {e}")

    os.remove(LOG_OPERACIONES)  # Borra el log después de deshacer.
    print(Fore.LIGHTGREEN_EX + "Operación deshecha con éxito." + Style.RESET_ALL)

def mover_a_problematicos(ruta, carpeta_destino):
    """
    Crea la carpeta "Problematicos" y mueve a ella los archivos que generen algún error.
    """
    carpeta_problematicos = os.path.join(carpeta_destino, "Problematicos")
    os.makedirs(carpeta_problematicos, exist_ok=True)
    destino = os.path.join(carpeta_problematicos, os.path.basename(ruta))
    shutil.move(ruta, destino)
    
# FIN - Registro de errores, función deshacer y apartar archivos problematicos.
