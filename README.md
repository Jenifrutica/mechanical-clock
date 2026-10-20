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
./entrypoint.sh
```

Al abrir, el reloj inicia en marcha automática en hora Colombia (UTC-5). Las manecillas giran en una terminal a pantalla completa. La hora se muestra con décimas. El cronómetro arranca automáticamente y se muestra únicamente en el menú, donde puedes pausarlo o reiniciarlo. La esfera tiene números del 1 al 12. En pantallas anchas el reloj queda a la izquierda y la información a la derecha; en pantallas pequeñas, la información va al pie.

## Controles

- `Ctrl+C`: abrir o cerrar el menú, sin pausar el reloj.
- `1`: volver al reloj.
- `2`: avanzar 1 segundo.
- `3`: retroceder 1 segundo.
- `4`: avanzar 10 minutos.
- `5`: retroceder 10 minutos.
- `6`: reiniciar a `12:00:00`.
- `7`: redibujar.
- `8`: volver a la hora actual.
- `9`: iniciar/pausar el cronómetro.
- `10`: reiniciar el cronómetro.
- `11`: salir.

El reloj sigue avanzando mientras el menú está abierto. El cronómetro se muestra y controla en el menú, no en la pantalla principal.

Escribe el número y presiona `Enter`. Haz clic dentro de la terminal para que el teclado funcione.

## Despliegue

Los siguientes archivos son de despliegue y son ajenos al código solicitado:

- `Dockerfile`
- `.dockerignore`
- `entrypoint.sh`

El despliegue usa Docker y ttyd. Nada de esto forma parte del código Python del reloj.

Repositorio: https://github.com/Jenifrutica/mechanical-clock

Link público: https://mechanical-clock.onrender.com

Cada visitante abre su propia sesión y su propio reloj. Los cambios de un visitante no afectan a los demás. Máximo 4 sesiones simultáneas.
