import os, time
import imagenes, videos, audio, documentos, otros
from colorama import Fore, Style, init
from tabulate import tabulate
from config import registrar_operacion, deshacer_ultima_operacion

init(autoreset=True)

EXTENSIONES = {
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
    "Audio": [".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"],
    "Documentos": [".txt", ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".ppt", ".pptx", 
                   ".ppsx", ".odt", ".ods", ".odp", ".pdf", ".epub", ".mobi"],
    "Otros": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".ttf", ".otf"],
}

# INICIO - Encapsulado
def elegir_carpeta_origen(): # Opción 1
    global carpeta_origen
    carpeta_origen = input("Ingrese la carpeta de origen: ").strip()
    if os.path.exists(carpeta_origen):
        print(Fore.LIGHTMAGENTA_EX + f"Carpeta de origen elegida: {carpeta_origen}" + Style.RESET_ALL)
    else:
        print(Fore.LIGHTRED_EX + "La carpeta ingresada no existe." + Style.RESET_ALL)

def elegir_carpeta_destino(): # Opción 2
    global carpeta_destino
    carpeta_destino = input("Ingrese la carpeta de destino: ").strip()
    if os.path.exists(carpeta_destino):
        print(Fore.LIGHTMAGENTA_EX + f"Carpeta de destino elegida: {carpeta_destino}" + Style.RESET_ALL)
    else:
        os.makedirs(carpeta_destino, exist_ok=True)
        print(Fore.LIGHTMAGENTA_EX + f"Carpeta de destino creada: {carpeta_destino}" + Style.RESET_ALL)

def elegir_tipo(): # Opción 3
    global tipo_seleccionado, extensiones_seleccionadas
    print(Fore.LIGHTMAGENTA_EX + "\nTipos de archivos disponibles:" + Style.RESET_ALL)

    for idx, tipo in enumerate(EXTENSIONES.keys(), start=1):
        print(Fore.LIGHTMAGENTA_EX + f"{idx}. {tipo}" + Style.RESET_ALL)
    
    seleccion = input("Elija el tipo de archivo a buscar (1-5): ").strip()

    try:
        idx = int(seleccion)

        if 1 <= idx <= len(EXTENSIONES):
            tipo_seleccionado = list(EXTENSIONES.keys())[idx - 1]
            extensiones_seleccionadas = EXTENSIONES[tipo_seleccionado]
            print(Fore.LIGHTMAGENTA_EX + f"Tipo seleccionado: {tipo_seleccionado}")
            print(Fore.LIGHTMAGENTA_EX + f"Extensiones: {', '.join(extensiones_seleccionadas)}" + Style.RESET_ALL)
            return tipo_seleccionado, extensiones_seleccionadas
        
        else:
            print(Fore.LIGHTRED_EX + "Selección fuera de rango." + Style.RESET_ALL)
            return None, None
        
    except ValueError:
        print(Fore.LIGHTRED_EX + "Selección inválida. Intente nuevamente." + Style.RESET_ALL)
        return None, None

def iniciar_busqueda(carpeta_origen, carpeta_destino, tipo_seleccionado): # Opción 4
    if not carpeta_origen or not carpeta_destino or not tipo_seleccionado:
        print(Fore.LIGHTRED_EX + "Debe elegir la carpeta de origen, carpeta de destino y tipo de archivo antes de iniciar la búsqueda." + Style.RESET_ALL)
        return

    if tipo_seleccionado == "Imagenes":
        print(Fore.LIGHTMAGENTA_EX + f"Buscando duplicados de tipo {tipo_seleccionado}..." + Style.RESET_ALL)
        duplicados_imagenes = imagenes.buscar_duplicados_imagenes(carpeta_origen)
        imagenes.mover_duplicados_imagenes(duplicados_imagenes, carpeta_destino, registrar_operacion)

    elif tipo_seleccionado == "Videos":
        print(Fore.LIGHTMAGENTA_EX + f"Buscando duplicados de tipo {tipo_seleccionado}..." + Style.RESET_ALL)
        videos.buscar_videos(carpeta_origen, carpeta_destino)

    elif tipo_seleccionado == "Audio":
        print(Fore.LIGHTMAGENTA_EX + f"Buscando duplicados de tipo {tipo_seleccionado}..." + Style.RESET_ALL)
        duplicados_audio = audio.buscar_duplicados_audio(carpeta_origen)
        audio.mover_duplicados_audio(duplicados_audio, carpeta_destino)

    elif tipo_seleccionado == "Documentos":
        print(Fore.LIGHTMAGENTA_EX + f"Buscando duplicados de tipo {tipo_seleccionado}..." + Style.RESET_ALL)
        duplicados_documentos = documentos.buscar_duplicados_documentos(carpeta_origen)
        documentos.mover_duplicados_documentos(duplicados_documentos, carpeta_destino, registrar_operacion)

    elif tipo_seleccionado == "Otros":
        print(Fore.LIGHTMAGENTA_EX + f"Buscando duplicados de tipo {tipo_seleccionado}..." + Style.RESET_ALL)
        duplicados_otros = otros.buscar_duplicados_otros(carpeta_origen)
        otros.mover_duplicados_otros(duplicados_otros, carpeta_destino, registrar_operacion)

    else:
        print(Fore.LIGHTRED_EX + f"Actualmente, no hay soporte avanzado para {tipo_seleccionado}." + Style.RESET_ALL)

    print(Fore.LIGHTGREEN_EX + "Proceso de búsqueda completado." + Style.RESET_ALL)

# FIN - Encapsulado

# INICIO - Personalizado
def logo_ascii():
    logo = r"""
██████╗  ██████╗ ██████╗ ██████╗ ███████╗██╗     ███████╗██╗██╗     ███████╗███████╗
██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔════╝██║     ██╔════╝██║██║     ██╔════╝██╔════╝
██║  ██║██║   ██║██████╔╝██████╔╝█████╗  ██║     █████╗  ██║██║     █████╗  ███████╗
██║  ██║██║   ██║██╔═══╝ ██╔═══╝ ██╔══╝  ██║     ██╔══╝  ██║██║     ██╔══╝  ╚════██║
██████╔╝╚██████╔╝██║     ██║     ███████╗███████╗██║     ██║███████╗███████╗███████║
╚═════╝  ╚═════╝ ╚═╝     ╚═╝     ╚══════╝╚══════╝╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝                                                                           
"""
    print (Fore.LIGHTCYAN_EX + logo + Style.RESET_ALL)

def animacion_inicio():
    print(Fore.LIGHTMAGENTA_EX + "Iniciando", end="", flush=True)
    for _ in range(8):
        time.sleep(0.1)
        print (Fore.LIGHTMAGENTA_EX + ".", end="", flush=True)
    print("\n" + Style.RESET_ALL)

def limpiar_consola():
    os.system("cls" if os.name == "nt" else "clear")

def animacion_cierre():
    print(Fore.LIGHTMAGENTA_EX + "Cerrando", end="", flush=True)
    for _ in range(8):
        time.sleep(0.1)
        print (Fore.LIGHTMAGENTA_EX + ".", end="", flush=True)
    print("\n" + Style.RESET_ALL)

# FIN - Personalizado

# INICIO - Menú principal
def menu_principal():

    print(Fore.LIGHTCYAN_EX + "=" * 38)
    print(Fore.LIGHTCYAN_EX + " " * 11  + "MENÚ PRINCIPAL")
    print(Fore.LIGHTCYAN_EX + "=" * 38 + Style.RESET_ALL)

    opciones = [
        ["1.", "Elegir carpeta/s de origen"],
        ["2.", "Elegir carpeta destino"],
        ["3.", "Seleccionar tipo/s de archivo"],
        ["4.", "Iniciar búsqueda de duplicados"],
        ["5.", "Deshacer última operación"],
        ["6.", "Ayuda"],
        ["7.", "Información"],
        ["0.", "Salir"]
    ]

    print(Fore.LIGHTMAGENTA_EX + tabulate(opciones, tablefmt="grid") + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + "=" * 38 + Style.RESET_ALL)

    return input("Seleccione una opción: ")

def menu_ayuda():
    print(Fore.LIGHTYELLOW_EX + "=" * 108)
    print(Fore.LIGHTYELLOW_EX + " " * 51  + "AYUDA")
    print(Fore.LIGHTYELLOW_EX + "=" * 108 + Style.RESET_ALL)

    opciones = [
        ["1. Elegir carpeta/s:", "Elija las carpetas donde buscar archivos duplicados."],
        ["2. Elegir destino:", "Elija la carpeta donde mover los duplicados encontrados."],
        ["3. Seleccionar tipos de archivo:", "Defina qué tipo/s de archivo desea buscar."],
        ["4. Iniciar búsqueda de duplicados:", "Ejecuta la búsqueda de duplicados en la/s carpeta/s seleccionada/s."],
        ["5. Deshacer última operación:", "Revierte la última operación realizada."]
    ]

    print(Fore.LIGHTYELLOW_EX + tabulate(opciones, tablefmt="grid") + Style.RESET_ALL)
    print(Fore.LIGHTYELLOW_EX + "=" * 108 + Style.RESET_ALL)

def menu_tipos():
    print(Fore.LIGHTGREEN_EX + "=" * 141)
    print(Fore.LIGHTGREEN_EX + " " * 59 + "EXTENSIONES RECONOCIDAS")
    print(Fore.LIGHTGREEN_EX + "=" * 141 + Style.RESET_ALL)

    opciones = [
        ["Imagenes", '".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"'],
        ["Videos", '".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"'],
        ["Audio", '".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"'],
        ["Documentos", '".txt", ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".ppt", ".pptx",".ppsx", ".odt", ".ods", ".odp", ".pdf", ".epub", ".mobi"'],
        ["Otros", '".zip", ".rar", ".7z", ".tar", ".gz", ".iso", ".ttf", ".otf"']
    ]

    print(Fore.LIGHTGREEN_EX + tabulate(opciones, tablefmt="grid") + Style.RESET_ALL)
    print(Fore.LIGHTGREEN_EX + "=" * 141 + Style.RESET_ALL)

def informacion():
    print(Fore.LIGHTBLUE_EX + "=" * 55)
    print(Fore.LIGHTBLUE_EX + " " * 22 + "INFORMACIÓN")
    print(Fore.LIGHTBLUE_EX + "=" * 55 + Style.RESET_ALL)

    opciones = [
        ["Autor", "MBit_8 (https://mbit08.space/)"],
        ["Versión", "2.0.0"],
        ["Repositorio", "https://github.com/MBit08/DoppelFiles"],
        ["Licencia", "AGPL 3.0"],
        ["Apoyo", "https://www.patreon.com/MBit_8"]
    ]

    print(Fore.LIGHTBLUE_EX + tabulate(opciones, tablefmt="grid") + Style.RESET_ALL)
    print(Fore.LIGHTBLUE_EX + "=" * 55 + Style.RESET_ALL)

def main():

    limpiar_consola()
    logo_ascii()
    animacion_inicio()

    while True:
        opcion = menu_principal()
        match opcion:
            case "1":
                elegir_carpeta_origen()

            case "2":
                elegir_carpeta_destino()

            case "3":
                elegir_tipo()

            case "4":
                iniciar_busqueda(carpeta_origen, carpeta_destino, tipo_seleccionado)

            case "5":
                deshacer_ultima_operacion()

            case "6":
                menu_ayuda()
                menu_tipos()
            
            case "7":
                informacion()

            case "0":
                animacion_cierre()
                break

            case _:
                print(Fore.LIGHTMAGENTA_EX + "Opción no válida. Intente nuevamente.\n" + Style.RESET_ALL)
              
# FIN - Menú principal

if __name__ == "__main__":
    main()
