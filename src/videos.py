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
    with open(LOG_ERRORES, "a") as log:
        log.write(f"{ruta}: {mensaje}\n")

def registrar_operacion(original, destino):
    """
    Registra una operación de movimiento en el archivo de log.
    """
    with open(LOG_OPERACIONES, "a") as log:
        log.write(f"{original}|{destino}\n")

# FIN - Registro de errores y función deshacer.

# INICIO - Backend de decodificación para OpenCV.
def configurar_backend(backend="DirectShow"):
    """
    Tuve que agregarlo debido a errores en el procesamiento
    de diferentes archivos. Para probar si con diferentes
    decodificadores algo cambiaba.
    """
    backends = {
        "FFmpeg": cv2.CAP_FFMPEG, # Gral.
        "GStreamer": cv2.CAP_GSTREAMER, # Linux.
        "DirectShow": cv2.CAP_DSHOW # Windows.
    }
    if backend in backends:
        cv2.VideoCapture.set(cv2.CAP_PROP_BACKEND, backends[backend])
        print(f"Backend configurado a {backend}.")
    else:
        print(f"Backend {backend} no reconocido. Usando configuración predeterminada.")

# FIN - Backend de decodificación para OpenCV.

# INICIO - Hashes.
def calcular_hash_video(ruta_video, frame_interval=60):
    """
    Calcula un hash basado en frames seleccionados de un video.
    """
    try:
        cap = cv2.VideoCapture(ruta_video)
        if not cap.isOpened():
            raise ValueError("No se puede abrir el video.")

        frames_hash = []
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        for i in range(0, frame_count, frame_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                continue

            # Convierte el frame a escala de grises para simplificar el cálculo del hash.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames_hash.append(hash(gray.tobytes()))

        cap.release()
        return sum(frames_hash) // len(frames_hash) if frames_hash else None

    except Exception as e:
        registrar_error(ruta_video, f"Error al calcular hash: {e}")
        return None

def calcular_hashes_videos(archivos, frame_interval=60):
    """
    Procesa los videos y calcula los hashes basados en frames seleccionados.
    """
    hashes = defaultdict(list)
    for ruta in tqdm(archivos, desc="Procesando videos"):
        hash_video = calcular_hash_video(ruta, frame_interval)
        if hash_video:
            hashes[hash_video].append(ruta)
    return hashes

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
            ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duracion = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
            tamano = os.path.getsize(ruta)
            cap.release()
            return ancho * alto, duracion, tamano
        except Exception as e:
            registrar_error(ruta, f"Error al obtener calidad: {e}")
            return 0, 0, 0

    return max(grupo_videos, key=lambda ruta: obtener_calidad(ruta))

# FIN - Análisis y procesamiento.

# INICIO - Ejecución.
def buscar_videos(carpeta_origen, carpeta_destino, registrar_operacion_func):
    """
    Busca duplicados de videos en una carpeta y subcarpetas.
    """
    archivos = obtener_archivos_videos(carpeta_origen)
    print(f"Videos encontrados: {len(archivos)}")
    hashes = calcular_hashes_videos(archivos)

    duplicados = {hash_: rutas for hash_, rutas in hashes.items() if len(rutas) > 1}
    mover_duplicados_videos(duplicados, carpeta_destino)

def mover_duplicados_videos(duplicados, carpeta_destino):
    """
    Mueve los archivos duplicados, dejando uno como referencia.
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    for hash_, grupo in tqdm(duplicados.items(), desc="Moviendo duplicados"):
        referencia = seleccionar_mejor_calidad(grupo)  # Elige el mejor.
        grupo.remove(referencia)

        for ruta in grupo:
            destino = os.path.join(carpeta_destino, os.path.basename(ruta))

            contador = 1
            while os.path.exists(destino):
                destino = os.path.join(
                    carpeta_destino,
                    f"{os.path.splitext(os.path.basename(ruta))[0]}_{contador}{os.path.splitext(ruta)[1]}"
                )
                contador += 1

            try:
                shutil.move(ruta, destino)
                registrar_operacion(ruta, destino)
            except Exception as e:
                registrar_error(ruta, f"Error al mover: {e}")

    print("Proceso de movimiento completado.")

# FIN - Ejecución.
