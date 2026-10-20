CIRCLE_POINTS = (
    (0, -8), (1, -8), (3, -8), (4, -8), (6, -7), (7, -7), (8, -6), (9, -6), (10, -5), (11, -5),
    (12, -4), (13, -3), (13, -2), (14, -2), (14, -1), (14, 0), (14, 1), (14, 2), (13, 2), (13, 3),
    (12, 4), (11, 5), (10, 5), (9, 6), (8, 6), (7, 7), (6, 7), (4, 8), (3, 8), (1, 8),
    (0, 8), (-1, 8), (-3, 8), (-4, 8), (-6, 7), (-7, 7), (-8, 6), (-9, 6), (-10, 5), (-11, 5),
    (-12, 4), (-13, 3), (-13, 2), (-14, 2), (-14, 1), (-14, 0), (-14, -1), (-14, -2), (-13, -2), (-13, -3),
    (-12, -4), (-11, -5), (-10, -5), (-9, -6), (-8, -6), (-7, -7), (-6, -7), (-4, -8), (-3, -8), (-1, -8),
)

RIM_POINTS = (
    (0, -8), (1, -8), (2, -8), (3, -8), (4, -8), (5, -7), (6, -7), (7, -7), (8, -7), (8, -6),
    (9, -6), (10, -6), (10, -5), (11, -5), (12, -4), (13, -3), (13, -2), (14, -2), (14, -1), (14, 0),
    (14, 1), (14, 2), (13, 2), (13, 3), (12, 4), (11, 5), (10, 5), (10, 6), (9, 6), (8, 6),
    (8, 7), (7, 7), (6, 7), (5, 7), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8), (-1, 8),
    (-2, 8), (-3, 8), (-4, 8), (-5, 7), (-6, 7), (-7, 7), (-8, 7), (-8, 6), (-9, 6), (-10, 6),
    (-10, 5), (-11, 5), (-12, 4), (-13, 3), (-13, 2), (-14, 2), (-14, 1), (-14, 0), (-14, -1), (-14, -2),
    (-13, -2), (-13, -3), (-12, -4), (-11, -5), (-10, -5), (-10, -6), (-9, -6), (-8, -6), (-8, -7), (-7, -7),
    (-6, -7), (-5, -7), (-4, -8), (-3, -8), (-2, -8), (-1, -8),
)

COLOMBIA_OFFSET_SECONDS = -5 * 3600
FRAME_WIDTH = 78
FRAME_HEIGHT = 24
CENTER_X = 39
CENTER_Y = 9

RESET = "\033[0m"
COLOR_TITLE = "\033[38;5;196m"
COLOR_RIM = "\033[38;5;88m"
COLOR_TICK = "\033[38;5;240m"
COLOR_MAJOR = "\033[38;5;250m"
COLOR_HOUR = "\033[97m"
COLOR_MINUTE = "\033[37m"
COLOR_SECOND = "\033[38;5;196m"
COLOR_CENTER = "\033[38;5;196m"
COLOR_CARDINAL = "\033[38;5;196m"
COLOR_STATUS = "\033[97m"
COLOR_DIM = "\033[38;5;245m"
COLOR_NUMBERS = ("\033[97m", "\033[37m", "\033[38;5;250m")


class ClockCanvasApp:
    def __init__(self, clock):
        self.clock = clock
        self._use_proc_uptime = True
        self._fallback_seconds = 0.0

    def run(self):
        self._enter_screen()
        try:
            self._synchronize_clock()
            while True:
                try:
                    self._run_auto()
                except KeyboardInterrupt:
                    self.clock.pause()
                    try:
                        action = self._show_menu()
                    except KeyboardInterrupt:
                        break
                    if action == 8:
                        break
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass
        finally:
            self._leave_screen()

    def _enter_screen(self):
        print(
            "\033[?1049h\033[2J\033[H\033[?25l\033]0;Reloj Mecanico\007",
            end="",
            flush=True,
        )

    def _leave_screen(self):
        print("\033[0m\033[?25h\033[?1049l", end="", flush=True)

    def _now(self):
        if self._use_proc_uptime:
            try:
                with open("/proc/uptime", "r") as file:
                    return float(file.read().split()[0])
            except OSError:
                self._use_proc_uptime = False
        return None

    def _read_epoch(self):
        boot_time = None
        try:
            with open("/proc/stat", "r") as file:
                for line in file:
                    if line.startswith("btime "):
                        boot_time = int(line.split()[1])
                        break
        except OSError:
            return None
        uptime = self._now()
        if boot_time is None or uptime is None:
            return None
        return boot_time + uptime

    def _synchronize_clock(self):
        epoch = self._read_epoch()
        if epoch is None:
            return
        local_seconds = int(epoch) + COLOMBIA_OFFSET_SECONDS
        seconds_of_day = local_seconds % 86400
        hour_24 = seconds_of_day // 3600
        minute = (seconds_of_day % 3600) // 60
        second = seconds_of_day % 60
        hour_12 = hour_24 % 12
        if hour_12 == 0:
            hour_12 = 12
        self.clock.set_time(hour_12, minute, second)

    def _wait_until(self, target):
        while True:
            current = self._now()
            if current is None:
                for _ in range(1000000):
                    pass
                return
            if current >= target:
                return
            for _ in range(2000):
                pass

    def _run_auto(self):
        self.clock.start()
        print("\033[2J\033[H", end="", flush=True)
        now = self._now()
        if now is None:
            now = self._fallback_seconds
        epoch = self._read_epoch()
        if epoch is not None:
            next_tick = now + (1.0 - (epoch - int(epoch)))
        else:
            next_tick = now + 1.0
        if next_tick <= now:
            next_tick = now + 1.0
        while True:
            now = self._now()
            if now is None:
                self._fallback_seconds += 0.1
                now = self._fallback_seconds
            while now >= next_tick:
                self.clock.tick_forward()
                next_tick += 1.0
            fraction = now - (next_tick - 1.0)
            if fraction < 0.0:
                fraction = 0.0
            elif fraction > 1.0:
                fraction = 1.0
            self._render_auto(fraction)
            self._wait_until(now + 0.1)

    def _show_menu(self):
        while True:
            self._render_menu()
            try:
                choice = input("Opción (Enter = iniciar): ").strip()
            except EOFError:
                return 8
            if choice == "" or choice == "1":
                return 1
            if choice == "2":
                self.clock.tick_forward()
            elif choice == "3":
                self.clock.tick_backward()
            elif choice == "4":
                self.clock.fast_adjust_minutes(10)
            elif choice == "5":
                self.clock.fast_adjust_minutes(-10)
            elif choice == "6":
                self.clock.reset_midnight()
            elif choice == "7":
                pass
            elif choice == "8":
                return 8
            else:
                continue

    def _angles(self, fraction):
        data = self.clock.readout()
        hour = data["hours"]
        minute = data["minutes"]
        second = data["seconds"]
        hour_base = 0 if hour == 12 else hour
        second_position = (second + fraction) % 60.0
        minute_position = (minute + (second + fraction) / 60.0) % 60.0
        hour_position = (
            (hour_base + minute / 60.0 + (second + fraction) / 3600.0) * 5.0
        ) % 60.0
        return (
            second_position * 6.0,
            minute_position * 6.0,
            hour_position * 6.0,
            second_position,
            minute_position,
            hour_position,
        )

    def _point_at(self, position):
        position = position % 60.0
        index = int(position)
        fraction = position - index
        first = CIRCLE_POINTS[index]
        second = CIRCLE_POINTS[(index + 1) % 60]
        return (
            first[0] + (second[0] - first[0]) * fraction,
            first[1] + (second[1] - first[1]) * fraction,
        )

    def _put_text(self, grid, colors, x, y, text, color=None):
        for character in text:
            if 0 <= x < FRAME_WIDTH and 0 <= y < FRAME_HEIGHT:
                grid[y][x] = character
                colors[y][x] = color
            x += 1

    def _draw_line(self, grid, colors, x0, y0, x1, y1, character, color):
        delta_x = abs(x1 - x0)
        step_x = 1 if x0 < x1 else -1
        delta_y = -abs(y1 - y0)
        step_y = 1 if y0 < y1 else -1
        error = delta_x + delta_y
        while True:
            if 0 <= x0 < FRAME_WIDTH and 0 <= y0 < FRAME_HEIGHT:
                grid[y0][x0] = character
                colors[y0][x0] = color
            if x0 == x1 and y0 == y1:
                break
            doubled_error = 2 * error
            if doubled_error >= delta_y:
                error += delta_y
                x0 += step_x
            if doubled_error <= delta_x:
                error += delta_x
                y0 += step_y

    def _draw_hand(self, grid, colors, position, length, character, color, thickness):
        point_x, point_y = self._point_at(position)
        end_x = CENTER_X + round(point_x * length)
        end_y = CENTER_Y + round(point_y * length)
        self._draw_line(
            grid, colors, CENTER_X, CENTER_Y, end_x, end_y, character, color
        )
        if thickness > 1:
            if abs(point_y) >= abs(point_x):
                offset_x = 1 if -point_y >= 0 else -1
                offset_y = 0
            else:
                offset_x = 0
                offset_y = 1 if point_x >= 0 else -1
            self._draw_line(
                grid,
                colors,
                CENTER_X + offset_x,
                CENTER_Y + offset_y,
                end_x + offset_x,
                end_y + offset_y,
                character,
                color,
            )

    def _set_point(self, grid, colors, point, scale, character, color):
        x = CENTER_X + round(point[0] * scale)
        y = CENTER_Y + round(point[1] * scale)
        if 0 <= x < FRAME_WIDTH and 0 <= y < FRAME_HEIGHT:
            grid[y][x] = character
            colors[y][x] = color

    def _draw_dial(self, grid, colors, second_position, minute_position, hour_position):
        for point in RIM_POINTS:
            self._set_point(grid, colors, point, 1.0, "▓", COLOR_RIM)

        for index, point in enumerate(CIRCLE_POINTS):
            if index % 5 == 0:
                self._set_point(grid, colors, point, 0.90, "+", COLOR_MAJOR)
            else:
                self._set_point(grid, colors, point, 0.90, "·", COLOR_TICK)

        self._draw_hand(
            grid, colors, hour_position, 0.56, "█", COLOR_HOUR, 2
        )
        self._draw_hand(
            grid, colors, minute_position, 0.80, "▓", COLOR_MINUTE, 1
        )
        self._draw_hand(
            grid, colors, second_position, 0.97, "·", COLOR_SECOND, 1
        )

        for index in range(12):
            value = 12 if index == 0 else index
            point = CIRCLE_POINTS[index * 5]
            x = CENTER_X + round(point[0] * 0.78)
            y = CENTER_Y + round(point[1] * 0.78)
            label = str(value)
            if len(label) == 2:
                x -= 1
            if value in (12, 3, 6, 9):
                number_color = COLOR_CARDINAL
            else:
                number_color = COLOR_NUMBERS[index % len(COLOR_NUMBERS)]
            self._put_text(grid, colors, x, y, label, number_color)

        grid[CENTER_Y][CENTER_X] = "●"
        colors[CENTER_Y][CENTER_X] = COLOR_CENTER

    def _build_grid(self, fraction, menu_mode):
        grid = [[" "] * FRAME_WIDTH for _ in range(FRAME_HEIGHT)]
        colors = [[None] * FRAME_WIDTH for _ in range(FRAME_HEIGHT)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, second_position, minute_position, hour_position = (
            self._angles(fraction)
        )

        title = "RELOJ ANALÓGICO MECÁNICO"
        self._put_text(
            grid,
            colors,
            (FRAME_WIDTH - len(title)) // 2,
            0,
            title,
            COLOR_TITLE,
        )
        self._draw_dial(grid, colors, second_position, minute_position, hour_position)

        mode = "MARCHA" if data["running"] else "PAUSA"
        self._put_text(
            grid,
            colors,
            2,
            18,
            f"HORA {data['hours']:02d}:{data['minutes']:02d}:{data['seconds']:02d}    COLOMBIA (UTC-5)    MODO {mode}",
            COLOR_STATUS,
        )
        self._put_text(
            grid,
            colors,
            2,
            19,
            f"ÁNGULOS: SEG {second_angle:6.1f}°   MIN {minute_angle:6.1f}°   HORA {hour_angle:6.1f}°",
            COLOR_DIM,
        )

        if menu_mode:
            self._put_text(
                grid,
                colors,
                2,
                20,
                "1 Iniciar/Reanudar (o Enter)   2 +1s   3 -1s   4 +10min",
                COLOR_STATUS,
            )
            self._put_text(
                grid,
                colors,
                2,
                21,
                "5 -10min   6 Reiniciar   7 Redibujar   8 Salir",
                COLOR_STATUS,
            )
        else:
            self._put_text(
                grid,
                colors,
                2,
                20,
                "Pistas 60 / 60 / 12 marcas | Acarreo Segundero -> Minutero -> Horario",
                COLOR_DIM,
            )
            self._put_text(
                grid,
                colors,
                2,
                21,
                "Ctrl+C: pausar y abrir el menú",
                COLOR_SECOND,
            )
            self._put_text(
                grid,
                colors,
                2,
                22,
                "Luego escribe 2-8 y pulsa ENTER | 1 o Enter reanuda",
                COLOR_STATUS,
            )
            self._put_text(
                grid,
                colors,
                2,
                23,
                "Haz clic dentro de la terminal para usar el teclado",
                COLOR_DIM,
            )
        return grid, colors

    def _rows(self, grid, colors):
        rows = []
        for y in range(FRAME_HEIGHT):
            parts = []
            current_color = None
            for x in range(FRAME_WIDTH):
                color = colors[y][x]
                if color != current_color:
                    if current_color is not None:
                        parts.append(RESET)
                    if color is not None:
                        parts.append(color)
                    current_color = color
                parts.append(grid[y][x])
            if current_color is not None:
                parts.append(RESET)
            rows.append("".join(parts))
        return rows

    def _write_frame(self, rows, clear=False, newline=False):
        prefix = "\033[2J\033[H" if clear else "\033[H"
        text = prefix + "\n".join(rows)
        if newline:
            text += "\n"
        print(text, end="", flush=True)

    def _render_auto(self, fraction):
        grid, colors = self._build_grid(fraction, False)
        self._write_frame(self._rows(grid, colors))

    def _render_menu(self):
        grid, colors = self._build_grid(0.0, True)
        self._write_frame(self._rows(grid, colors)[:22], clear=True, newline=True)
