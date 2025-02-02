import os
from PIL import Image, ImageChops, ImageFile
import imagehash
from collections import defaultdict
from tqdm import tqdm
import shutil
import time

# Registros de errores y operaciones.
LOG_ERRORES = "log_errores.txt"
LOG_OPERACIONES = "log_ultima_operacion.txt"

EXTENSIONES_IMAGENES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"]

ImageFile.LOAD_TRUNCATED_IMAGES = True # Permitir la carga de imágenes truncadas.

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

# INICIO - Hashes.
def calcular_varios_hashes(ruta_imagen):
    """
    Calcula múltiples hashes perceptuales para una imagen.
    """
    try:
        with Image.open(ruta_imagen) as img:
            img.verify()  # Verifica si la imagen está corrupta antes de procesarla.
        with Image.open(ruta_imagen) as img:  # Reabrir después de verificar.
            if img.mode != "RGB":
                img = img.convert("RGB")
            return (
                imagehash.average_hash(img),
                imagehash.phash(img),
                imagehash.dhash(img),
                imagehash.whash(img)
            )
    except Exception as e:
        registrar_error(ruta_imagen, f"Imagen dañada o truncada: {e}")
        return None

def calcular_hashes_imagenes(archivos, umbral_hash=3):
    """
    Procesa las imágenes y calcula los hashes perceptuales.
    Agrupa hashes similares según el umbral proporcionado.
    """
    hashes = defaultdict(list)
    for ruta in tqdm(archivos, desc="Procesando imágenes"):
        hashes_varios = calcular_varios_hashes(ruta)
        if hashes_varios:
            encontrado = False
            for key in hashes:
                if son_duplicados(hashes_varios, key, umbral_hash):
                    hashes[key].append(ruta)
                    encontrado = True
                    break
            if not encontrado:
                hashes[hashes_varios] = [ruta]
    return hashes

def son_duplicados(hashes1, hashes2, umbral=3):
    """
    Determina si dos imágenes son duplicados comparando múltiples hashes.
    """
    return all(abs(h1 - h2) <= umbral for h1, h2 in zip(hashes1, hashes2))

# FIN - Hashes.

# INICIO - Análisis y procesamiento.
def obtener_archivos_imagenes(carpeta):
    """
    Busca imágenes válidas en una carpeta y subcarpetas.
    """
    archivos = []
    for root, _, files in os.walk(carpeta):
        for file in files:
            if file.lower().endswith(tuple(EXTENSIONES_IMAGENES)):
                archivos.append(os.path.join(root, file))
    return archivos

def comparar_por_histograma(img1_path, img2_path, umbral=0.9):
    """
    Compara dos imágenes por su histograma para determinar similitud.
    """
    try:
        with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
            hist1 = img1.histogram()
            hist2 = img2.histogram()
            similitud = sum(1 - abs(h1 - h2) / max(h1, h2) for h1, h2 in zip(hist1, hist2)) / len(hist1)
            return similitud >= umbral
    except Exception as e:
        registrar_error(img1_path, f"Error al comparar histogramas: {e}")
        return False

def seleccionar_mejor_calidad(grupo_imagenes):
    """
    Selecciona la imagen de mejor calidad (mayor resolución o tamaño).
    """
    return max(grupo_imagenes, key=lambda img: (Image.open(img).size[0] * Image.open(img).size[1], os.path.getsize(img)))

# FIN - Análisis y procesamiento.

def mover_archivo_con_reintento(origen, destino, intentos=3, espera=5):
    """
    Intenta mover un archivo con reintentos en caso de error.
    """
    for intento in range(intentos):
        try:
            shutil.move(origen, destino)
            return True
        except PermissionError:
            time.sleep(espera)
        except Exception as e:
            registrar_error(origen, f"Error inesperado al mover: {e}")
            return False
    registrar_error(origen, f"No se pudo mover tras {intentos} intentos.")
    return False

# INICIO - Ejecución.
def buscar_duplicados_imagenes(carpeta_origen, extensiones, umbral_hash=3):
    """
    Busca duplicados de imágenes en una carpeta y devuelve un diccionario
    de duplicados donde la clave es el hash y el valor son las rutas de las imágenes.
    """
    archivos = [ruta for ruta in obtener_archivos_imagenes(carpeta_origen) if ruta.lower().endswith(tuple(extensiones))]
    print(f"Imágenes encontradas: {len(archivos)}")
    hashes = calcular_hashes_imagenes(archivos, umbral_hash)
    return {hash_: rutas for hash_, rutas in hashes.items() if len(rutas) > 1}

def mover_duplicados_imagenes(duplicados, carpeta_destino, registrar_operacion):
    """
    Mueve los archivos duplicados, dejando el de mejor calidad en su lugar.
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    for hash_, grupo in tqdm(duplicados.items(), desc="Moviendo duplicados"):
        mejor = seleccionar_mejor_calidad(grupo)
        grupo.remove(mejor)

        for ruta in grupo:
            destino = os.path.join(carpeta_destino, os.path.basename(ruta))

            contador = 1
            while os.path.exists(destino):
                destino = os.path.join(
                    carpeta_destino,
                    f"{os.path.splitext(os.path.basename(ruta))[0]}_{contador}{os.path.splitext(ruta)[1]}"
                )
                contador += 1

            if not mover_archivo_con_reintento(ruta, destino):
                continue

            registrar_operacion(ruta, destino)

    print("Proceso completado.")

# FIN - Ejecución.
