# Reloj Analógico Mecánico

## Código

El proyecto está hecho únicamente en Python. Para no dejar todo en un solo archivo, se divide en módulos y los únicos imports permitidos son los archivos locales del proyecto. No se usan bibliotecas estándar, librerías externas, archivos shell ni Docker.

Archivos:

- `dial_mark.py`
- `circular_track.py`
- `hand.py`
- `gear_train.py`
- `mechanical_clock.py`
- `clock_view.py`
- `main.py`

## Ejecución local

```text
python3 main.py
```

Al iniciar, la aplicación pide:

1. Tamaño de la terminal en columnas y filas. Por defecto `114 34`; en una consola de 80×24 escribe `80 24`.
2. Hora local en formato `HH:MM:SS`.

No se lee la hora del sistema con `/proc` ni con bibliotecas. La hora inicial la escribe el usuario y luego el reloj avanza con un temporizador interno aproximado por conteo de ciclos. La velocidad puede variar según el CPU.

La esfera tiene números del 1 al 12. El cronómetro se controla únicamente desde el menú y no arranca solo.

## Controles

- `Ctrl+C`: abrir el menú.
- `1`: volver al reloj.
- `2`: avanzar 1 segundo.
- `3`: retroceder 1 segundo.
- `4`: avanzar 10 minutos.
- `5`: retroceder 10 minutos.
- `6`: reiniciar a `12:00:00`.
- `7`: redibujar.
- `8`: ajustar manualmente la hora local.
- `9`: iniciar/pausar el cronómetro.
- `0`: reiniciar el cronómetro.

Solo se acepta un dígito del 0 al 9. No se aceptan letras ni varios números.

El menú usa `input()` bloqueante, por lo que mientras espera un comando el reloj no se redibuja. Al volver al reloj continúa desde su estado mecánico.

## Versión Linux

La versión que usa `/proc/stat` y `/proc/uptime` quedó guardada en:

https://github.com/Jenifrutica/mechanical-clock-linux
