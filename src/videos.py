import os
import cv2
import shutil
from tqdm import tqdm
from colorama import Fore, Style, init
from config import registrar_error, registrar_operacion, mover_a_problematicos, EXTENSIONES_VIDEOS

init(autoreset=True)

"""
IMPORTANTE
Volví a una versión anterior, aunque con algunos ajustes, debido a que
el último código subido si bien había pasado las pruebas simples, al ejecutarlo
con un volumen mucho mayor de archivos aleatorios (en todos los aspectos), el
programa movía muchos falsos positivos incluso archivos sin ningún tipo de duplicado o similar
y dejaba varios archivos que si tenían duplicados, incluso aquellos que eran una copia exacta.
Es una solución temporal mientras puedo ajustar la nueva versión.
"""

# INICIO - Configuraciones dinámicas.
def configurar_backend(ruta_video): # Intenta configurar el mejor backend de decodificación disponible.
    backends = [cv2.CAP_FFMPEG, cv2.CAP_GSTREAMER, cv2.CAP_DSHOW]

    for backend in backends:
        cap = cv2.VideoCapture(ruta_video, backend)
        if cap.isOpened():
            cap.release()
            return backend
        
    print(Fore.LIGHTYELLOW_EX + "No se pudo seleccionar backend, usando predeterminado." + Style.RESET_ALL)
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
def obtener_archivos_videos(carpeta): # Busca archivos válidos en la carpeta origen y subcarpetas.
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
    archivos = obtener_archivos_videos(carpeta_origen)
    print(f"Videos encontrados: {len(archivos)}")
    
    hashes = {}
    for ruta in tqdm(archivos, desc="Calculando hashes"):
        hash_video = calcular_hash_video(ruta)
        if hash_video:
            hashes.setdefault(hash_video, []).append(ruta)
    
    duplicados = {hash_: rutas for hash_, rutas in hashes.items() if len(rutas) > 1}
    mover_duplicados_videos(duplicados, carpeta_destino)

def mover_duplicados_videos(duplicados, carpeta_destino): # Mueve los archivos duplicados, dejando el de mejor calidad.
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

    print(Fore.LIGHTGREEN_EX + "Videos duplicados movidos exitosamente." + Style.RESET_ALL)

# FIN - Ejecución.
