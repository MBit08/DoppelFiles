import os
from PIL import Image, ImageChops
import imagehash
from collections import defaultdict
from tqdm import tqdm
import shutil

# Registros de errores y operaciones.
LOG_ERRORES = "log_errores.txt"
LOG_OPERACIONES = "log_ultima_operacion.txt"

EXTENSIONES_IMAGENES = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg"]

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

# INICIO - Hashes.
def calcular_hash_imagen(ruta_imagen):
    """
    Calcula el hash perceptual de una imagen usando imagehash.
    """
    try:
        with Image.open(ruta_imagen) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")
            return imagehash.average_hash(img)
    except Exception as e:
        registrar_error(ruta_imagen, f"Error al procesar la imagen: {e}")
        return None

def calcular_hashes_imagenes(archivos, umbral=5):
    """
    Procesa las imágenes en paralelo y calcula los hashes perceptuales.
    Agrupa hashes similares según el umbral proporcionado.
    """
    hashes = defaultdict(list)
    for ruta in tqdm(archivos, desc="Procesando imágenes"):
        ruta, hash_, dimensiones = procesar_imagen(ruta)
        if hash_:
            hash_key = next((key for key in hashes if abs(hash_ - key) <= umbral), hash_)
            hashes[hash_key].append((ruta, dimensiones))
    return hashes

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

def obtener_dimensiones(ruta_imagen):
    """
    Devuelve las dimensiones (ancho, alto) de una imagen.
    """
    try:
        with Image.open(ruta_imagen) as img:
            return img.size
    except Exception as e:
        registrar_error(ruta_imagen, f"Error al obtener dimensiones: {e}")
        return (0, 0)

def es_miniatura(dimensiones, umbral_ancho=150, umbral_alto=150):
    """
    Determina si una imagen es una miniatura basada en sus dimensiones.
    """
    ancho, alto = dimensiones
    return ancho <= umbral_ancho and alto <= umbral_alto

def procesar_imagen(ruta):
    """
    Procesa una imagen para calcular su hash perceptual y dimensiones.
    """
    hash_ = calcular_hash_imagen(ruta)
    dimensiones = obtener_dimensiones(ruta)
    return ruta, hash_, dimensiones

def seleccionar_mejor_calidad(grupo_imagenes):
    """
    Selecciona la imagen de mejor calidad (mayor resolución o tamaño).
    """
    return max(grupo_imagenes, key=lambda img: (img[1][0] * img[1][1], os.path.getsize(img[0])))

# FIN - Análisis y procesamiento.

# INICIO - Ejecución.
def buscar_duplicados_imagenes(carpeta_origen, extensiones):
    """
    Busca duplicados de imágenes en una carpeta y devuelve un diccionario
    de duplicados donde la clave es el hash y el valor son las rutas de las imágenes.
    """
    archivos = [ruta for ruta in obtener_archivos_imagenes(carpeta_origen) if ruta.lower().endswith(tuple(extensiones))]
    print(f"Imágenes encontradas: {len(archivos)}")
    hashes = calcular_hashes_imagenes(archivos)
    return {hash_: rutas for hash_, rutas in hashes.items() if len(rutas) > 1}

def mover_duplicados_imagenes(duplicados, carpeta_destino, registrar_operacion):
    """
    Mueve los archivos duplicados, dejando la de mejor calidad en su lugar.
    También mueve miniaturas detectadas a una subcarpeta de miniaturas.
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    for hash_, grupo in tqdm(duplicados.items(), desc="Moviendo duplicados"):
        mejor = seleccionar_mejor_calidad(grupo)
        grupo.remove(mejor)

        for ruta, dimensiones in grupo:
            if es_miniatura(dimensiones):
                subcarpeta_miniaturas = os.path.join(carpeta_destino, "miniaturas")
                os.makedirs(subcarpeta_miniaturas, exist_ok=True)
                destino = os.path.join(subcarpeta_miniaturas, os.path.basename(ruta))
            else:
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
