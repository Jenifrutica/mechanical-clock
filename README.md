# Reloj Analógico Mecánico

## Código

El proyecto está hecho únicamente en Python. Los únicos imports permitidos son los archivos locales del proyecto. No se usan bibliotecas estándar, librerías externas, archivos shell ni Docker.

Archivos:

- `dial_mark.py`
- `circular_track.py`
- `hand.py`
- `gear_train.py`
- `mechanical_clock.py`
- `clock_view.py`
- `clock_pacing.py`
- `main.py`

## Ejecución local

```text
python3 main.py
```

Al iniciar aparece un reloj de bienvenida y se pide la hora local en formato `HH:MM:SS`. La hora inicial la escribe el usuario.

El ritmo lo controla `clock_pacing.py`, un módulo propio sin imports. Como no se puede leer el reloj del sistema, la velocidad se puede calibrar manualmente:

- Menú `Ctrl+C` → opción `0` Configuración.
- Opción `2` Calibrar velocidad.
- Mide 10 segundos reales con un teléfono o reloj.
- Al terminar pulsa `Ctrl+C`.
- Indica los segundos reales; la app ajusta los ciclos por frame.

Sin calibrar, la velocidad es aproximada y puede variar según el computador.

La resolución por defecto es `114 34`. Se puede cambiar desde Configuración.

## Controles

- `Ctrl+C`: abrir el menú.
- `1`: volver al reloj.
- `2`: avanzar 1 segundo.
- `3`: retroceder 1 segundo.
- `4`: avanzar 10 minutos.
- `5`: retroceder 10 minutos.
- `6`: reiniciar el reloj a `12:00:00`.
- `8`: ajustar manualmente la hora local.
- `9`: abrir el temporizador.
- `0`: configuración de resolución y velocidad.

## Temporizador

Dentro de la opción `9`:

- `1`: 10 minutos.
- `2`: 1 minuto.
- `3`: 30 segundos.
- `4`: tiempo personalizado en segundos.
- `5`: iniciar/pausar.
- `6`: reiniciar.
- `7`: volver al menú.

Al elegir una duración, vuelve automáticamente a la pantalla del reloj y empieza la cuenta. Al llegar a cero aparece la alerta visual `¡TIEMPO CUMPLIDO!`, que se cierra con `Enter`; el temporizador queda terminado.

No se reproduce sonido: sin bibliotecas, el pitido depende del terminal y no es confiable.

Solo se acepta un dígito del 0 al 9 en el menú principal. El menú es bloqueante, así que mientras espera un comando el reloj no se redibuja.

## Versión Linux

La versión que usa `/proc/stat` y `/proc/uptime` quedó guardada como respaldo en:

https://github.com/Jenifrutica/mechanical-clock-linux
