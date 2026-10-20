# Reloj Analógico Mecánico

## Código

El proyecto está hecho únicamente en Python. Para no dejar todo en un solo archivo, se divide en módulos y los únicos imports permitidos son los archivos locales del proyecto. No se usan librerías externas.

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

El reloj inicia automáticamente en hora Colombia (UTC-5). Las manecillas giran en una terminal a pantalla completa.

## Controles

- `Ctrl+C`: pausar y abrir el menú.
- `1`: iniciar o reanudar la marcha.
- `2`: avanzar 1 segundo.
- `3`: retroceder 1 segundo.
- `4`: avanzar 10 minutos.
- `5`: retroceder 10 minutos.
- `6`: reiniciar a `12:00:00`.
- `7`: redibujar.
- `8`: salir.

## Despliegue

Los siguientes archivos son de despliegue y son ajenos al código solicitado:

- `Dockerfile`
- `.dockerignore`

El despliegue usa Docker y ttyd. Nada de esto forma parte del código Python del reloj.

Repositorio: https://github.com/Jenifrutica/mechanical-clock

Link público: https://PENDIENTE-DE-RENDER

Cada visitante abre su propia sesión y su propio reloj. Los cambios de un visitante no afectan a los demás. Máximo 4 sesiones simultáneas.
