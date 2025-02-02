import os
import imagenes
import videos
import audio

# Registros de errores y operaciones.
LOG_ERRORES = "log_errores.txt"
LOG_OPERACIONES = "log_ultima_operacion.txt"

EXTENSIONES = {
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"],
    "Audio": [".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"],
    "Documentos": [".pdf", ".docx", ".xlsx", ".txt"],
    "Otros": [".zip", ".rar", ".7z"]
}

# INICIO - Registro de errores y función deshacer.
def registrar_operacion(original, destino):
    """
    Registra una operación de movimiento en el archivo de log.
    """
    with open(LOG_OPERACIONES, "a") as log:
        log.write(f"{original}|{destino}\n")
def deshacer_ultima_operacion():
    """
    Deshace la última operación basada en el log de operaciones.
    """
    if not os.path.exists(LOG_OPERACIONES):
        print("No hay operaciones previas para deshacer.")
        return

    confirmacion = input("¿Deseas deshacer la última operación? (s/n): ")
    if confirmacion.lower() != "s":
        print("Operación cancelada.")
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
    print("Operación deshecha con éxito.")
  
# FIN - Registro de errores y función deshacer.

# INICIO - Operaciones
def seleccionar_tipos_archivo():
    print("\nTipos de archivos disponibles:")
    for idx, tipo in enumerate(EXTENSIONES.keys(), start=1):
        print(f"{idx}. {tipo}")
    seleccion = input("Elija el tipo de archivo a buscar (1-5): ").strip()
    try:
        idx = int(seleccion)
        if 1 <= idx <= len(EXTENSIONES):
            tipo_seleccionado = list(EXTENSIONES.keys())[idx - 1]
            extensiones_seleccionadas = EXTENSIONES[tipo_seleccionado]
            return tipo_seleccionado, extensiones_seleccionadas
        else:
            print("Selección fuera de rango.")
            return None, None
    except ValueError:
        print("Selección inválida. Intente nuevamente.")
        return None, None

def iniciar_busqueda(carpeta_origen, carpeta_destino, tipo_seleccionado, extensiones_seleccionadas):
    if not carpeta_origen or not carpeta_destino or not extensiones_seleccionadas:
        print("Debe elegir la carpeta de origen, carpeta de destino y tipo de archivo antes de iniciar la búsqueda.")
        return

    if tipo_seleccionado == "Imagenes":
        print(f"Buscando duplicados de tipo {tipo_seleccionado}...")
        duplicados = imagenes.buscar_duplicados_imagenes(carpeta_origen, extensiones_seleccionadas)
        imagenes.mover_duplicados_imagenes(duplicados, carpeta_destino, registrar_operacion)

    elif tipo_seleccionado == "Videos":
        print(f"Buscando duplicados de tipo {tipo_seleccionado}...")
        videos.buscar_videos(carpeta_origen, carpeta_destino)

    elif tipo_seleccionado == "Audio":
        print(f"Buscando duplicados de tipo {tipo_seleccionado}...")
        duplicados_audio = audio.buscar_duplicados_audio(carpeta_origen)
        audio.mover_duplicados_audio(duplicados_audio, carpeta_destino)

    else:
        print(f"Actualmente, no hay soporte avanzado para {tipo_seleccionado}.")
    print("Proceso de búsqueda completado.")

# FIN - Operaciones

# INICIO - Menú principal
def menu_principal():
    print("\nDOPPELFILES")
    print("1. Elegir carpeta/s de origen")
    print("2. Elegir carpeta destino")
    print("3. Seleccionar tipos de archivo")
    print("4. Iniciar búsqueda de duplicados")
    print("5. Deshacer última operación")
    print("6. Ayuda")
    print("0. Salir")
    return input("Seleccione una opción: ")

def main():
    carpeta_origen = None
    carpeta_destino = None
    tipo_seleccionado = None
    extensiones_seleccionadas = None

    while True:
        opcion = menu_principal()
        match opcion:
            case "1":
                carpeta_origen = input("Ingrese la carpeta de origen: ").strip()
                if os.path.exists(carpeta_origen):
                    print(f"Carpeta de origen elegida: {carpeta_origen}")
                else:
                    print("La carpeta ingresada no existe.")

            case "2":
                carpeta_destino = input("Ingrese la carpeta de destino: ").strip()
                if os.path.exists(carpeta_destino):
                    print(f"Carpeta de destino elegida: {carpeta_destino}")
                else:
                    os.makedirs(carpeta_destino, exist_ok=True)
                    print(f"Carpeta de destino creada: {carpeta_destino}")

            case "3":
                tipo_seleccionado, extensiones_seleccionadas = seleccionar_tipos_archivo()
                if tipo_seleccionado:
                    print(f"Tipo seleccionado: {tipo_seleccionado}")
                    print(f"Extensiones: {', '.join(extensiones_seleccionadas)}")

            case "4":
                iniciar_busqueda(carpeta_origen, carpeta_destino, tipo_seleccionado, extensiones_seleccionadas)

            case "5":
                deshacer_ultima_operacion()

            case "6":
                print("\nAyuda:")
                print("1. Elegir carpeta/s: Elija las carpetas donde buscar archivos duplicados.")
                print("2. Elegir destino: Elija la carpeta donde mover los duplicados encontrados.")
                print("3. Seleccionar tipos de archivo: Defina qué tipo/s de archivo desea buscar.")
                print("4. Iniciar búsqueda de duplicados: Ejecuta la búsqueda de duplicados en la/s carpeta/s seleccionada/s.")
                print("5. Deshacer última operación: Revierte la última operación realizada.")

            case "0":
                print("Saliendo del programa...")
                break

            case _:
                print("Opción no válida. Intente nuevamente.")
              
# FIN - Menú principal

if __name__ == "__main__":
    main()
