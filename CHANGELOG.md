## v2-2.2.1.0.0 [2024-02-02]
Cambios menores y mayores en todos los módulos del programa.
Gracias a estos cambios tenemos un nuevo tipo de archivo para procesar, mejoras en el manejo de erroes, reducción de los falsos positivos y mayor eficiencia en la utilización de recursos al procesar.
### General
- Adición de la función deshacer.
- Correciones en los textos mostrados.
- Añadido el forzamiento de codificación UTF-8 en los registros para evitar errores por caracteres no reconocidos.
### Menú
- Adición del módulo "audio.py".
- Adición de la extensión ".m4a".
- Eliminada librería innecesaria.
### Imagenes
- Adición de funciones que permiten manejar imagenes truncadas, corruptas o abiertas por otros procesos.
- Adición de la función "mover_a_problematicos" que mueve a una subcarpeta todos los archivos que no se pudieron procesar por errores.
- Se mejoró el procesamiento de múltiples hashes según el umbral proporcionado.
- Nueva configuración del umbral, reduce los falsos positivos a un máximo de 1 cada 100 archivos según las últimas pruebas.
- Mejora en el análisis por similitud. Ahora también compara por su histograma.
### Videos
- Adición de la función "mover_a_problematicos" que mueve a una subcarpeta todos los archivos que no se pudieron procesar por errores.
- Adición de las "configuraciones dinámicas", un par de funciones que permiten al módulo elegir la mejor configuración según el archivo que va a procesar.
- Eliminación de la configuración estática del backend.
### Audio
- Creación del módulo "audio.py"
