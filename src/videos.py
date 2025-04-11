import os
import cv2
import shutil
from tqdm import tqdm
from PIL import Image
import imagehash
from contextlib import closing
from colorama import Fore, Style, init
from config import registrar_error, registrar_operacion, mover_a_problematicos, EXTENSIONES_VIDEOS

init(autoreset=True)

# INICIO -Configuraciones dinámicas.
UMBRAL_ERRORES_FRAMES = 3
UMBRAL_SIMILITUD_HASH = 5

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
        with closing(cv2.VideoCapture(ruta_video)) as cap:
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
def obtener_archivos_videos(carpeta): # Busca videos válidos en una carpeta y subcarpetas.
    archivos = []
    for root, _, files in os.walk(carpeta):
        for file in files:
            if file.lower().endswith(tuple(EXTENSIONES_VIDEOS)):
                archivos.append(os.path.join(root, file))
    return archivos

def calcular_hashes_videos(carpeta_origen):
    archivos = obtener_archivos_videos(carpeta_origen)
    print(f"Videos encontrados: {len(archivos)}")
    hashes = {}
    for ruta in tqdm(archivos, desc="Calculando hashes"):
        hash_video = calcular_hash_video(ruta)
        if hash_video:
            hashes.setdefault(hash_video, []).append(ruta)
    return hashes

def calcular_hash_video(ruta_video):
    """
    Calcula un hash perceptual promedio usando imagehash.phash, usando estrategia segura (str).
    """
    try:
        frame_interval = definir_frame_interval(ruta_video)
        backend = configurar_backend(ruta_video)
        cap = cv2.VideoCapture(ruta_video, backend)
        if not cap.isOpened():
            raise ValueError("No se puede abrir el video.")
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count == 0:
            raise ValueError("El archivo de video no contiene frames válidos.")
        frames_hash = []
        errores = 0
        for i in tqdm(range(0, frame_count, max(1, frame_interval)), desc="Procesando frames"):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret or frame is None or frame.shape[0] == 0 or frame.shape[1] == 0:
                errores += 1
                registrar_error(ruta_video, f"Frame {i} vacío o ilegible.")
                if errores >= UMBRAL_ERRORES_FRAMES:
                    raise RuntimeError("Demasiados frames corruptos.")
                continue
            try:
                imagen = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                hash_val = imagehash.phash(imagen)
                if not isinstance(hash_val, imagehash.ImageHash):
                    raise TypeError(f"Hash inesperado: {type(hash_val)}")
                frames_hash.append(str(hash_val))
            except Exception as e:
                errores += 1
                registrar_error(ruta_video, f"Error al procesar frame {i}: {e}")
                if errores >= UMBRAL_ERRORES_FRAMES:
                    raise RuntimeError("Demasiados errores de procesamiento de frames")
                continue
        cap.release()
        if not frames_hash:
            return None
        # Estrategia: concatenar y usar la más común (modo seguro)
        from collections import Counter
        hash_comun = Counter(frames_hash).most_common(1)[0][0]
        return hash_comun
    except Exception as e:
        registrar_error(ruta_video, f"Error al calcular hash: {e}, moviendo a problemáticos.")
        try:
            cap.release()
        except:
            pass
        mover_a_problematicos(ruta_video, os.path.dirname(ruta_video))
        return None

# FIN - Hashes.

# INICIO - Análisis y procesamiento.
def obtener_duplicados_videos(hashes):
    return {h: r for h, r in hashes.items() if len(r) > 1}

def obtener_duplicados_similares(hashes, umbral=UMBRAL_SIMILITUD_HASH):
    agrupados = {}
    for nuevo_hash, rutas in hashes.items():
        h_nuevo = int(nuevo_hash)
        agregado = False
        for existente in list(agrupados.keys()):
            if abs(int(existente) - h_nuevo) <= umbral:
                agrupados[existente].extend(rutas)
                agregado = True
                break
        if not agregado:
            agrupados[nuevo_hash] = list(rutas)
    return {h: r for h, r in agrupados.items() if len(r) > 1}

def seleccionar_mejor_calidad(grupo_videos): # Selecciona el video de mejor calidad basado en resolución, duración y tamaño.
    def obtener_calidad(ruta):
        try:
            cap = cv2.VideoCapture(ruta)
            if not cap.isOpened():
                return 0, 0, 0
            ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 1
            duracion = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)
            tamano = os.path.getsize(ruta)
            cap.release()
            return ancho * alto, duracion, tamano
        except:
            return 0, 0, 0
    return max(grupo_videos, key=lambda ruta: obtener_calidad(ruta))

def procesar_duplicados_videos(carpeta_origen, carpeta_destino):
    hashes = calcular_hashes_videos(carpeta_origen)
    duplicados = obtener_duplicados_videos(hashes)
    if not duplicados:
        print(Fore.LIGHTYELLOW_EX + "No se encontraron duplicados." + Style.RESET_ALL)
        return
    mover_duplicados_videos(duplicados, carpeta_destino)

# FIN - Análisis y procesamiento.

# INICIO - Ejecución.
def buscar_videos(carpeta_origen, carpeta_destino):
    procesar_duplicados_videos(carpeta_origen, carpeta_destino)

def mover_duplicados_videos(duplicados, carpeta_destino): # Mueve los archivos duplicados, dejando el de mejor calidad.
    os.makedirs(carpeta_destino, exist_ok=True)
    nombres_existentes = set(os.listdir(carpeta_destino))
    for hash_, grupo in tqdm(duplicados.items(), desc="Moviendo duplicados"):
        if not grupo:
            continue
        referencia = seleccionar_mejor_calidad(grupo)
        grupo.remove(referencia)
        if not grupo:
            continue
        for ruta in grupo:
            try:
                nombre_base, extension = os.path.splitext(os.path.basename(ruta))
                nombre_actual = os.path.basename(ruta)
                contador = 1
                while nombre_actual in nombres_existentes:
                    nombre_actual = f"{nombre_base}_{contador}{extension}"
                    contador += 1
                nombres_existentes.add(nombre_actual)
                destino = os.path.join(carpeta_destino, nombre_actual)
                shutil.move(ruta, destino)
                registrar_operacion(ruta, destino)
            except Exception as e:
                registrar_error(ruta, f"Error al mover archivo: {e}, moviendo a problemáticos.")
                mover_a_problematicos(ruta, carpeta_destino)
    print(Fore.LIGHTGREEN_EX + "Videos movidos exitosamente." + Style.RESET_ALL)

# FIN - Ejecución.
