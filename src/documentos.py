import os
import shutil
import hashlib
from tqdm import tqdm

# Registros de errores y operaciones.
LOG_ERRORES = "log_errores.txt"
LOG_OPERACIONES = "log_ultima_operacion.txt"

EXTENSIONES_DOCUMENTOS = [".txt", ".doc", ".docx", ".xls", ".xlsx", ".xlsm", ".ppt", ".pptx", 
                          ".ppsx", ".odt", ".ods", ".odp", ".pdf", ".epub", ".mobi"]

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

# FIN - Registro de errores y función deshacer.

# INICIO - Hash.
def calcular_hash_documento(ruta_documento):
    """
    Calcula un hash SHA-256 del contenido del archivo de documento.
    """
    try:
        hash_sha256 = hashlib.sha256()
        with open(ruta_documento, "rb") as f:
            for bloque in iter(lambda: f.read(4096), b""):
                hash_sha256.update(bloque)
        return hash_sha256.hexdigest()
    except Exception as e:
        registrar_error(ruta_documento, f"Error al calcular hash: {e}")
        return None

# FIN - Hash.

# INICIO - Ejecución.
def obtener_archivos_documentos(carpeta_origen):
    """
    Busca archivos válidos en una carpeta y subcarpetas.
    """
    archivos = []
    for root, _, files in os.walk(carpeta_origen):
        for file in files:
            if file.lower().endswith(tuple(EXTENSIONES_DOCUMENTOS)):
                archivos.append(os.path.join(root, file))
    return archivos

def buscar_duplicados_documentos(carpeta_origen):
    """
    Busca duplicados en la carpeta origen.
    Solo considera duplicados los que tienen el mismo contenido y extensión.
    """
    archivos = obtener_archivos_documentos(carpeta_origen)
    print(f"Documentos encontrados: {len(archivos)}")
    hashes = {}
    
    for ruta in tqdm(archivos, desc="Calculando hashes"):
        hash_documento = calcular_hash_documento(ruta)
        if hash_documento:
            clave = (hash_documento, os.path.splitext(ruta)[1])
            if clave not in hashes:
                hashes[clave] = []
            hashes[clave].append(ruta)
    
    duplicados = {clave: rutas for clave, rutas in hashes.items() if len(rutas) > 1}
    return duplicados

def mover_duplicados_documentos(duplicados, carpeta_destino):
    """
    Mueve los archivos duplicados a la carpeta destino.
    """
    os.makedirs(carpeta_destino, exist_ok=True)
    for _, grupo in tqdm(duplicados.items(), desc="Moviendo duplicados"):
        original = grupo[0]
        grupo.remove(original)
        
        for ruta in grupo:
            try:
                destino = os.path.join(carpeta_destino, os.path.basename(ruta))
                contador = 1
                while os.path.exists(destino):
                    destino = os.path.join(
                        carpeta_destino,
                        f"{os.path.splitext(os.path.basename(ruta))[0]}_{contador}{os.path.splitext(ruta)[1]}"
                    )
                    contador += 1
                shutil.move(ruta, destino)
                registrar_operacion(ruta, destino)
            except Exception as e:
                registrar_error(ruta, f"Error al mover archivo: {e}")
    
    print("Proceso completado.")

# FIN - Ejecución
