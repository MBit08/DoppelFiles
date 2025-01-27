# DoppelFiles
Pequeño programa que se encarga de identificar y mover archivos duplicados. -Nuevas funciones en desarrollo-

---

## Índice
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Uso](#uso)
4. [Problemas conocidos y soluciones](#problemas-conocidos-y-soluciones)
5. [Estado actual](#estado-actual)
6. [Ideas a futuro](#a-futuro)
7. [Contribuciones](#contribuciones)
8. [Licencia](#licencia)

---

## INTRODUCCIÓN
Trabajo con un enorme volumen de archivos y discos, muchas veces por falta de tiempo he tenido que mover documentos entre discos sin verificar si ya existián.
Esto a largo plazo me dejó con un desorden importante, por eso necesitaba un programa que me permitiera manejar toda esa cantidad y limpiar los duplicados.
Entiendo que existen ya programas para esto sin embargo las mejores opciones son de pago y/o no me generan mucha confianza, en especial aquellas que utilizan llamadas a servidor.
Siendo una razón más para crear mi propio programa.

En mi inocencia creí que iba a ser algo pequeño y simple, al final resultó un quebradero de cabeza con la cantidad de errores que fueron apareciendo. Entonces decidí compartir el progreso,
por si a alguien más le servía de ayuda o inspiración.

## INSTALACIÓN
### Requisitos previos
1. Python 3.9 o superior.
2. Dependencias listadas en "requirements.txt"

### Instrucciones
1. Clona este repositorio.
2. cd DoppelFiles
3. pip install -r requirements.txt

## USO
1. Inicia el programa desde la terminal: python main.py
2. Elegí la/s carpeta/s de origen. Si son más de una tenés que separa el path con ","
3. Elegí la carpeta de destino.
4. Definí el tipo de archivo a buscar.
5. Inicia la búsqueda.
Si te saltas algún paso la búsqueda no inicia y aparece un mensaje avisando del paso faltante.

## PROBLEMAS CONOCIDOS Y SOLUCIONES
### Error con OpenCV y PyLint:
- Mensaje: Module 'cv2' has no ...
- Solución: Agrega el siguiente argumento en la configuración de PyLint. "python.linting.pylintArgs": ["--extension-pkg-whitelist=cv2"]
### Error al procesar imágenes corruptas:
- Mensaje: cannot identify image file.
- Solución: El programa ignora automáticamente las imágenes no válidas y registra los errores en "log_errores.txt"
### Error al decodificar H.264
Sigo trabajando para encontrar la solución a este problema. En una de las versiones anteriores no pasaba pero creo que sobreescribí ese archivo por accidente, así que me toca investigar de vuelta.
### Varios falsos positivos (+10 cada 100 archivos)
Al igual que el anterior problema, esto en versiones anteriores no pasaba así que voy a investigar todos los códigos para ver donde está el problema.

## ESTADO ACTUAL
- Trabaja con archivos de tipo Imagen y Video.
- Busca en una o más carpetas seleccionadas.
- Mueve los duplicados a una carpeta seleccionada (esto por los falsos positivos).
- Es capaz de identificar todas las copias de un archivo incluso si difieren en tamaño, compresión o metadatos.
- De todas las copias selecciona y deja la de mejor calidad, mueve las demás.
- Detecta miniaturas y las mueve a una subcarpeta dentro del destino.
- Crea un registro para errores.
- Crea un registro de la última operación realizada.
- Puede deshacer la última operación realiada utilizando ese registro.

## A FUTURO
### Imagen y Video
- Permitir configurar los parametros para mejorar el rendimiento y reducir los falsos positivos según sea necesario.
- Función que adapte esto parámetros de forma automática según el archivo que esté analizando.
- Procesamiento múltiple.
### General
- Añadir módulos para el procesamiento de Audio, Documentos y Varios.
- Permitir la elección de Mover, Eliminar u Omitir.
- Mejorar el registro de errores y operaciones para identificar mejor cada error y falsos positivos.
### Interfaz Gráfica
- Añadir una versión con interfaz gráfica.
- Permitir visualizar previamente los archivos duplicados.
- Permitir seleccionar cada uno y elegir que se debe hacer con ellos.

## CONTRIBUCIONES
Como dije al principio, este proyecto lo pensé originalmente para mi uso personal. Pero si a alguien le sirve y quiere modificarlo a su gusto y necesidad sientase libre de crear un fork de este repositorio.

## LICENCIA
Este proyecto se encuentra bajo la licencia AGPL v3.0 -Hace años ya había definido que todos mis proyectos libres iban a ser con esta licencia.
