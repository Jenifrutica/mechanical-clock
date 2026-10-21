# Reloj Analógico Mecánico

## Código

El proyecto está hecho únicamente en Python. Los únicos imports permitidos son los archivos locales del proyecto. No se usan bibliotecas estándar, librerías externas ni archivos shell.


## Ejecución local

```text
python3 main.py
```

Al iniciar aparece un reloj de bienvenida y se pide la hora local en formato `HH:MM:SS`. La hora inicial la escribe el usuario.

El ritmo lo controla `clock_pacing.py`, un módulo propio sin imports. Como no se puede leer el reloj del sistema, la velocidad se puede calibrar manualmente:

Sin calibrar, la velocidad es aproximada y puede variar según el computador.

La resolución por defecto es `114 34`. Se puede cambiar desde Configuración.


## Temporizador

Dentro de la opción `9`:

- La funcionalidad añadida, es un temporizador, con tiempos predefinidos, y personalizados (en segundos).

Al elegir una duración, vuelve automáticamente a la pantalla del reloj y empieza la cuenta. Al llegar a cero aparece la alerta visual `¡TIEMPO CUMPLIDO!`, que se cierra con `Enter`; el temporizador queda terminado.

Solo se acepta un dígito del 0 al 9 en el menú principal. El menú es bloqueante, así que mientras espera un comando el reloj no se redibuja.

## Versión Linux

Antes de esta, existió una version, hecha 100% python, pero adaptada solo a un OS Linux, que es el que uso, esta usa `/proc/stat` y `/proc/uptime` quedó guardada como respaldo en:
https://github.com/Jenifrutica/mechanical-clock-linux

Pero no es confiable para todos los OS, tonces se modificó. 
