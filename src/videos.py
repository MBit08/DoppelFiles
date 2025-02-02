import os
import cv2
from tqdm import tqdm
import shutil
from collections import defaultdict

# Registros de errores y operaciones.
LOG_ERRORES = "log_errores.txt"
LOG_OPERACIONES = "log_ultima_operacion.txt"

EXTENSIONES_VIDEOS = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"]

# INICIO - Registro de errores y función deshacer.
def registrar_error(ruta, mensaje):
    """
    Registra un error en el archivo de errores.
    """
    with open(LOG_ERRORES, "a", encoding="utf-8") as log:
        log.write(f"{ruta}: {mensaje}\n")

def registrar_operacion(original, destino):
    """
    Registra una operación de movimiento en el archivo de log.
    """
    with open(LOG_OPERACIONES, "a", encoding="utf-8") as log:
        log.write(f"{original}|{destino}\n")

def mover_a_problematicos(ruta, carpeta_destino):
    """
    Mueve el archivo que genera el error a una subcarpeta.
    """
    carpeta_problematicos = os.path.join(carpeta_destino, "problematicos")
    os.makedirs(carpeta_problematicos, exist_ok=True)
    destino = os.path.join(carpeta_problematicos, os.path.basename(ruta))
    shutil.move(ruta, destino)

# FIN - Registro de errores y función deshacer.

# INICIO -Configuraciones dinámicas.
def configurar_backend(ruta_video):
    """
    Intenta configurar el mejor backend de decodificación disponible.
    """
    backends = [cv2.CAP_FFMPEG, cv2.CAP_GSTREAMER, cv2.CAP_DSHOW]
    for backend in backends:
        cap = cv2.VideoCapture(ruta_video, backend)
        if cap.isOpened():
            cap.release()
            return backend
    print("No se pudo seleccionar backend, usando predeterminado.")
    return None

def definir_frame_interval(ruta_video):
    """
    Determina automáticamente el frame_interval en función de la duración y FPS del video.
    """
    try:
        cap = cv2.VideoCapture(ruta_video)
        if not cap.isOpened():
            return 30  # Valor por defecto si no se puede abrir el video.

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        duracion = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps if fps > 0 else 60

        if duracion < 60:
            return 10  # Videos cortos: Mayor precisión.
        elif duracion < 300:
            return 30  # Videos medios: Balanceado.
        else:
            return 60  # Videos largos: Optimizado.
    except Exception:
        return 30  # Valor por defecto en caso de error.

# FIN - Configuraciones dinámicas.

# INICIO - Hashes.
def calcular_hash_video(ruta_video):
    """
    Calcula un hash basado en frames seleccionados de un video.
    Utiliza un frame_interval dinámico determinado por la función definir_frame_interval.
    """
    frame_interval = definir_frame_interval(ruta_video)
    backend = configurar_backend(ruta_video)
    try:
        cap = cv2.VideoCapture(ruta_video, backend)
        if not cap.isOpened():
            raise ValueError("No se puede abrir el video.")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count == 0:
            raise ValueError("El archivo de video no contiene frames válidos.")

        frames_hash = []
        for i in tqdm(range(0, frame_count, max(1, frame_interval)), desc="Procesando frames"):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                registrar_error(ruta_video, f"Error al leer frame {i}, moviendo a problemáticos.")
                cap.release()
                mover_a_problematicos(ruta_video, os.path.dirname(ruta_video))
                return None

            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frames_hash.append(hash(gray.tobytes()))
            except Exception as e:
                registrar_error(ruta_video, f"Error al procesar frame {i}: {e}, moviendo a problemáticos.")
                cap.release()
                mover_a_problematicos(ruta_video, os.path.dirname(ruta_video))
                return None

        cap.release()
        return sum(frames_hash) // len(frames_hash) if frames_hash else None

    except Exception as e:
        registrar_error(ruta_video, f"Error al calcular hash: {e}, moviendo a problemáticos.")
        mover_a_problematicos(ruta_video, os.path.dirname(ruta_video))
        return None

# FIN - Hashes.

# INICIO - Análisis y procesamiento.
def obtener_archivos_videos(carpeta):
    """
    Busca videos válidos en una carpeta y subcarpetas.
    """
    archivos = []
    for root, _, files in os.walk(carpeta):
        for file in files:
            if file.lower().endswith(tuple(EXTENSIONES_VIDEOS)):
                archivos.append(os.path.join(root, file))
    return archivos

def seleccionar_mejor_calidad(grupo_videos):
    """
    Selecciona el video de mejor calidad basado en resolución, duración y tamaño.
    """
    def obtener_calidad(ruta):
        try:
            cap = cv2.VideoCapture(ruta)
            if not cap.isOpened():
                raise ValueError("No se puede abrir el video.")

            ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 1
            duracion = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)
            tamano = os.path.getsize(ruta)
            cap.release()
            return ancho * alto, duracion, tamano
        
        except Exception as e:
            registrar_error(ruta, f"Error al obtener calidad: {e}")
            return 0, 0, 0

    return max(grupo_videos, key=lambda ruta: obtener_calidad(ruta))

# FIN - Análisis y procesamiento.

# INICIO - Ejecución.
def buscar_videos(carpeta_origen, carpeta_destino):
    """
    Busca duplicados de videos en una carpeta y subcarpetas.
    """
    archivos = obtener_archivos_videos(carpeta_origen)
    print(f"Videos encontrados: {len(archivos)}")
    
    hashes = {}
    for ruta in tqdm(archivos, desc="Calculando hashes"):
        hash_video = calcular_hash_video(ruta)
        if hash_video:
            hashes.setdefault(hash_video, []).append(ruta)
    
    duplicados = {hash_: rutas for hash_, rutas in hashes.items() if len(rutas) > 1}
    mover_duplicados_videos(duplicados, carpeta_destino)

def mover_duplicados_videos(duplicados, carpeta_destino):
    """
    Mueve los archivos duplicados, dejando uno como referencia.
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    for hash_, grupo in tqdm(duplicados.items(), desc="Moviendo duplicados"):
        referencia = seleccionar_mejor_calidad(grupo)
        grupo.remove(referencia)

        for ruta in grupo:
            try:
                destino = os.path.join(carpeta_destino, os.path.basename(ruta))
                contador = 1
                nombre_base, extension = os.path.splitext(os.path.basename(ruta))
                while os.path.exists(destino):
                    destino = os.path.join(
                        carpeta_destino,
                        f"{nombre_base}_{contador}{extension}"
                    )
                    contador += 1
                shutil.move(ruta, destino)
                registrar_operacion(ruta, destino)
            except Exception as e:
                registrar_error(ruta, f"Error al mover archivo: {e}, moviendo a problemáticos.")
                mover_a_problematicos(ruta, carpeta_destino)

    print("Proceso completado.")

# FIN - Ejecución.
