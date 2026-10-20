# Reloj Analógico Mecánico

## Código

El proyecto está hecho únicamente en Python. Para no dejar todo en un solo archivo, se divide en módulos y los únicos imports permitidos son los archivos locales del proyecto. No se usan bibliotecas estándar ni librerías externas, ni archivos shell, ni Docker.

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

Al abrir, el reloj inicia en marcha automática en hora Colombia (UTC-5). La esfera tiene números del 1 al 12. El cronómetro se controla únicamente desde el menú y no arranca solo.

## Controles

- `Ctrl+C`: abrir el menú.
- `1`: volver al reloj.
- `2`: avanzar 1 segundo.
- `3`: retroceder 1 segundo.
- `4`: avanzar 10 minutos.
- `5`: retroceder 10 minutos.
- `6`: reiniciar a `12:00:00`.
- `7`: redibujar.
- `8`: volver a la hora actual.
- `9`: iniciar/pausar el cronómetro.
- `0`: reiniciar el cronómetro.

Solo se acepta un dígito del 0 al 9. No se aceptan letras ni varios números.

El menú usa `input()` bloqueante, por lo que mientras espera un comando el reloj no se redibuja. Al volver al reloj continúa desde su estado mecánico. El tamaño de la terminal se toma de `LINES` y `COLUMNS` si están definidas; por defecto usa 114×34.
