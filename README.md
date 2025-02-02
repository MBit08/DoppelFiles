# DoppelFiles
Programa encargado de encontrar duplicados dentro de una o más carpetas designadas, y mover todas las copias a una carpeta destino.
Actualmente trabajando con imagenes, video y audio. Próximamente más tipos de archivos y funciones.

![Banner](assets/Banner.jpg)

## Índice
1. [Introducción](#introducción)
2. [Instalación](#instalación)
3. [Uso](#uso)
4. [Problemas conocidos y soluciones](#problemas-conocidos-y-soluciones)
5. [Estado actual](#estado-actual)
6. [Ideas a futuro](#a-futuro)
7. [Contribuciones](#contribuciones)
8. [Licencia](#licencia)

## INTRODUCCIÓN
Trabajo con un enorme volumen de archivos y discos, muchas veces por falta de tiempo he tenido que mover documentos entre discos sin verificar si ya existián.
Esto a largo plazo me dejó con un desorden importante, por eso necesitaba un programa que me permitiera manejar toda esa cantidad y limpiar los duplicados.
Entiendo que existen ya programas para esto sin embargo las mejores opciones son de pago y/o no me generan mucha confianza, en especial aquellas que utilizan llamadas a servidor.
Siendo una razón más para crear mi propio programa.

En mi inocencia creí que iba a ser algo pequeño y simple, al final resultó un quebradero de cabeza con la cantidad de errores que fueron apareciendo. Entonces decidí compartir el progreso,
por si a alguien más le servía de ayuda o inspiración.

### Versionado
Si bien existen estandares ya establecidos, para este programa en esta estapa prefiero usar mi propio esquema que es el siguiente:
~~~
Menú-Imagenes.Videos.Audio.Documentos.Otros
~~~
Por ejemplo actualmente sería v2-2.2.1.0.0, marcando así la versión de cada módulo.
Esto sería solo para la edición de consola, la versión gráfica (planeada para cuando todo esté completo) si va a seguir el estandar:
~~~
MAYOR.MENOR.PARCHE
~~~

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
### Filtro estricto
No es un problema en sí pero según como se configuré cada módulo puede ser más exigente o más permisivo en cuanto a la similitud de cada archivo. Actualmente está en un punto intermedio donde
en las prubas no arrojó ningún falso positivo pero sí dejó varias copias similares, más no identicas, sin procesar.

## ESTADO ACTUAL
- Trabaja con archivos de tipo imagen, video y audio.
- Busca en una o más carpetas a la vez (compara todos los archivos de todas las carpetas).
- Mueve los duplicados a una carpeta destino seleccionada.
- Es capaz de identificar todas las copias de un archivo incluso si difieren en tamaño, compresión o metadatos.
- [CÓDIGO] Se puede ajustar la sensibilidad en la identificación de imagenes y videos.
- [VIDEOS] Cuenta con configuraciones dinámicas para el "backend" y el "intervalo de frames".
- De todas las copias selecciona y deja la de mejor calidad, mueve las demás.
- Detecta miniaturas y las mueve a una subcarpeta dentro del destino.
- Crea un registro para errores.
- [VIDEOS] Crea una subcarpeta "Problematicos" y mueve todos los videos que no se pudieron procesar.
- Crea un registro de la última operación realizada.
- Puede deshacer la última operación realiada utilizando ese registro.
- Muestra una barra de progreso.

## A FUTURO
### Módulos de procesamiento
- Permitir configurar los parametros de análisis y procesamiento previo a ejecutar la búsqueda.
### General
- Añadir módulos para el procesamiento de documentos y varios.
- Permitir la elección de Mover, Eliminar u Omitir.
- Mejorar el registro de errores y operaciones para identificar mejor cada error y falsos positivos.
### Interfaz Gráfica
- Añadir una versión con interfaz gráfica.
- Permitir visualizar previamente los archivos duplicados.
- Permitir seleccionar cada uno y que se debe hacer con ellos.

## CONTRIBUCIONES
Como dije al principio, este proyecto lo pensé originalmente para mi uso personal. Pero si a alguien le sirve y quiere modificarlo a su gusto y necesidad sientase libre de crear un fork de este repositorio.

## LICENCIA
Este proyecto se encuentra bajo la licencia AGPL v3.0 -Hace años ya había definido que todos mis proyectos libres iban a ser con esta licencia.
