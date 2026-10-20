CIRCLE_POINTS = (
    (0, -6), (3, -6), (5, -6), (8, -6), (10, -5), (12, -5), (15, -5), (17, -4), (19, -4), (20, -4),
    (22, -3), (23, -2), (24, -2), (24, -1), (25, -1), (25, 0), (25, 1), (24, 1), (24, 2), (23, 2),
    (22, 3), (20, 4), (19, 4), (17, 4), (15, 5), (12, 5), (10, 5), (8, 6), (5, 6), (3, 6),
    (0, 6), (-3, 6), (-5, 6), (-8, 6), (-10, 5), (-13, 5), (-15, 5), (-17, 4), (-19, 4), (-20, 4),
    (-22, 3), (-23, 2), (-24, 2), (-24, 1), (-25, 1), (-25, 0), (-25, -1), (-24, -1), (-24, -2), (-23, -2),
    (-22, -3), (-20, -4), (-19, -4), (-17, -4), (-15, -5), (-13, -5), (-10, -5), (-8, -6), (-5, -6), (-3, -6),
)

COLOMBIA_OFFSET_SECONDS = -5 * 3600
FRAME_WIDTH = 78
FRAME_HEIGHT = 24
CENTER_X = 39
CENTER_Y = 8


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
                    if self._show_menu() == 8:
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
        print("\033[?25h\033[?1049l", end="", flush=True)

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
                choice = input("Opción: ").strip()
            except EOFError:
                return 8
            if choice == "1":
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

    def _put_text(self, grid, x, y, text):
        for character in text:
            if 0 <= x < FRAME_WIDTH and 0 <= y < FRAME_HEIGHT:
                grid[y][x] = character
            x += 1

    def _draw_line(self, grid, x0, y0, x1, y1, character):
        delta_x = abs(x1 - x0)
        step_x = 1 if x0 < x1 else -1
        delta_y = -abs(y1 - y0)
        step_y = 1 if y0 < y1 else -1
        error = delta_x + delta_y
        while True:
            if 0 <= x0 < FRAME_WIDTH and 0 <= y0 < FRAME_HEIGHT:
                grid[y0][x0] = character
            if x0 == x1 and y0 == y1:
                break
            doubled_error = 2 * error
            if doubled_error >= delta_y:
                error += delta_y
                x0 += step_x
            if doubled_error <= delta_x:
                error += delta_x
                y0 += step_y

    def _draw_hand(self, grid, position, length, character):
        point_x, point_y = self._point_at(position)
        end_x = CENTER_X + round(point_x * length)
        end_y = CENTER_Y + round(point_y * length)
        self._draw_line(grid, CENTER_X, CENTER_Y, end_x, end_y, character)

    def _draw_dial(self, grid, second_position, minute_position, hour_position):
        for index, point in enumerate(CIRCLE_POINTS):
            character = "o" if index % 5 == 0 else "."
            x = CENTER_X + point[0]
            y = CENTER_Y + point[1]
            if 0 <= x < FRAME_WIDTH and 0 <= y < FRAME_HEIGHT:
                grid[y][x] = character

        self._draw_hand(grid, hour_position, 0.56, "H")
        self._draw_hand(grid, minute_position, 0.78, "M")
        self._draw_hand(grid, second_position, 0.98, "S")

        for index in range(12):
            value = 12 if index == 0 else index
            point = CIRCLE_POINTS[index * 5]
            x = CENTER_X + round(point[0] * 0.82)
            y = CENTER_Y + round(point[1] * 0.82)
            label = str(value)
            if len(label) == 2:
                x -= 1
            self._put_text(grid, x, y, label)

        grid[CENTER_Y][CENTER_X] = "+"

    def _build_grid(self, fraction, menu_mode):
        grid = [[" "] * FRAME_WIDTH for _ in range(FRAME_HEIGHT)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, second_position, minute_position, hour_position = (
            self._angles(fraction)
        )

        title = "RELOJ ANALÓGICO MECÁNICO"
        self._put_text(grid, (FRAME_WIDTH - len(title)) // 2, 0, title)
        self._draw_dial(grid, second_position, minute_position, hour_position)

        mode = "MARCHA" if data["running"] else "PAUSA"
        self._put_text(
            grid,
            2,
            16,
            f"HORA {data['hours']:02d}:{data['minutes']:02d}:{data['seconds']:02d}    MODO {mode}",
        )
        self._put_text(
            grid,
            2,
            17,
            f"SEG {second_angle:6.1f}°   MIN {minute_angle:6.1f}°   HORA {hour_angle:6.1f}°",
        )
        self._put_text(
            grid,
            2,
            18,
            "Pistas 60 / 60 / 12 marcas | Acarreo Segundero -> Minutero -> Horario",
        )

        if menu_mode:
            self._put_text(grid, 2, 19, "Hora Colombia (UTC-5) | Reloj pausado")
            self._put_text(grid, 2, 20, "1 Iniciar/Reanudar   2 +1s   3 -1s   4 +10min")
            self._put_text(grid, 2, 21, "5 -10min   6 Reiniciar   7 Redibujar   8 Salir")
        else:
            self._put_text(grid, 2, 19, "Hora Colombia (UTC-5) | Modo automático")
            self._put_text(grid, 2, 20, "Ctrl+C: pausar y abrir el menú")
            self._put_text(grid, 2, 21, "Menú: 1 Iniciar/Pausar  2/3 +/-1s  4/5 +/-10min")
            self._put_text(grid, 2, 22, "6 Reiniciar  7 Redibujar  8 Salir")
        return grid

    def _rows(self, grid):
        return ["".join(row) for row in grid]

    def _write_frame(self, rows, clear=False, newline=False):
        prefix = "\033[2J\033[H" if clear else "\033[H"
        text = prefix + "\n".join(rows)
        if newline:
            text += "\n"
        print(text, end="", flush=True)

    def _render_auto(self, fraction):
        grid = self._build_grid(fraction, False)
        self._write_frame(self._rows(grid))

    def _render_menu(self):
        grid = self._build_grid(0.0, True)
        self._write_frame(self._rows(grid)[:22], clear=True, newline=True)
