PI = 3.141592653589793

RESET = "\033[0m"
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


def _sin_deg(degrees):
    radians = degrees * PI / 180.0
    while radians > PI:
        radians -= 2.0 * PI
    while radians < -PI:
        radians += 2.0 * PI
    term = radians
    result = radians
    n = 1
    while n < 8:
        term *= -radians * radians / ((2 * n) * (2 * n + 1))
        result += term
        n += 1
    return result


def _cos_deg(degrees):
    return _sin_deg(degrees + 90.0)


class ClockCanvasApp:
    def __init__(self, clock):
        self.clock = clock
        self._use_proc_uptime = True
        self._fallback_seconds = 0.0
        self.terminal_lines = self._read_environment_int("LINES", 24)
        self.terminal_columns = self._read_environment_int("COLUMNS", 80)
        self.frame_width = min(78, max(40, self.terminal_columns - 1))
        self.center_x = self.frame_width // 2
        self.full_layout = self.terminal_lines >= 40
        if self.full_layout:
            self.frame_height = 40
            self.center_y = 19
            self.radius_x = min(29, max(10, (self.frame_width - 4) // 2))
            self.radius_y = max(6, round(self.radius_x * 17 / 29))
            self.footer_y = 39
        else:
            self.frame_height = 24
            self.center_y = 11
            self.radius_x = min(19, max(8, (self.frame_width - 4) // 2))
            self.radius_y = max(4, round(self.radius_x * 11 / 19))
            self.footer_y = 23
        self.top_padding = max(0, (self.terminal_lines - self.frame_height) // 2)

    def _read_environment_int(self, name, default):
        prefix = (name + "=").encode()
        try:
            with open("/proc/self/environ", "rb") as file:
                entries = file.read().split(b"\0")
        except OSError:
            return default
        for entry in entries:
            if entry.startswith(prefix):
                try:
                    return int(entry[len(prefix):].decode())
                except ValueError:
                    return default
        return default

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
            "\033[?1049h\033[2J\033[H\033[?25l\033]0;Reloj\007",
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
        local_seconds = int(epoch) - 5 * 3600
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
        angle = position * 6.0
        return (
            self.radius_x * _sin_deg(angle),
            -self.radius_y * _cos_deg(angle),
        )

    def _put_text(self, grid, colors, x, y, text, color=None):
        for character in text:
            if 0 <= x < self.frame_width and 0 <= y < self.frame_height:
                grid[y][x] = character
                colors[y][x] = color
            x += 1

    def _centered_text(self, grid, colors, y, text, color=None):
        self._put_text(
            grid, colors, (self.frame_width - len(text)) // 2, y, text, color
        )

    def _draw_line(self, grid, colors, x0, y0, x1, y1, character, color):
        delta_x = abs(x1 - x0)
        step_x = 1 if x0 < x1 else -1
        delta_y = -abs(y1 - y0)
        step_y = 1 if y0 < y1 else -1
        error = delta_x + delta_y
        while True:
            if 0 <= x0 < self.frame_width and 0 <= y0 < self.frame_height:
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
        end_x = self.center_x + round(point_x * length)
        end_y = self.center_y + round(point_y * length)
        self._draw_line(
            grid, colors, self.center_x, self.center_y, end_x, end_y, character, color
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
                self.center_x + offset_x,
                self.center_y + offset_y,
                end_x + offset_x,
                end_y + offset_y,
                character,
                color,
            )

    def _set_angle_point(self, grid, colors, angle, scale, character, color):
        x = self.center_x + round(self.radius_x * scale * _sin_deg(angle))
        y = self.center_y - round(self.radius_y * scale * _cos_deg(angle))
        if 0 <= x < self.frame_width and 0 <= y < self.frame_height:
            grid[y][x] = character
            colors[y][x] = color

    def _draw_dial(self, grid, colors, second_position, minute_position, hour_position):
        for angle in range(0, 360, 2):
            self._set_angle_point(grid, colors, angle, 1.0, "▓", COLOR_RIM)
        for index in range(60):
            angle = index * 6
            if index % 5 == 0:
                self._set_angle_point(grid, colors, angle, 0.90, "+", COLOR_MAJOR)
            else:
                self._set_angle_point(grid, colors, angle, 0.90, "·", COLOR_TICK)

        self._draw_hand(
            grid, colors, hour_position, 0.55, "█", COLOR_HOUR, 2
        )
        self._draw_hand(
            grid, colors, minute_position, 0.78, "▓", COLOR_MINUTE, 1
        )
        self._draw_hand(
            grid, colors, second_position, 0.97, "·", COLOR_SECOND, 1
        )

        for index in range(12):
            value = 12 if index == 0 else index
            angle = index * 30
            x = self.center_x + round(self.radius_x * 0.76 * _sin_deg(angle))
            y = self.center_y - round(self.radius_y * 0.76 * _cos_deg(angle))
            label = str(value)
            if len(label) == 2:
                x -= 1
            if value in (12, 3, 6, 9):
                number_color = COLOR_CARDINAL
            else:
                number_color = COLOR_NUMBERS[index % len(COLOR_NUMBERS)]
            self._put_text(grid, colors, x, y, label, number_color)

        grid[self.center_y][self.center_x] = "●"
        colors[self.center_y][self.center_x] = COLOR_CENTER

    def _build_grid(self, fraction):
        grid = [[" "] * self.frame_width for _ in range(self.frame_height)]
        colors = [[None] * self.frame_width for _ in range(self.frame_height)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, second_position, minute_position, hour_position = (
            self._angles(fraction)
        )

        self._draw_dial(grid, colors, second_position, minute_position, hour_position)

        mode = "MARCHA" if data["running"] else "PAUSA"
        time_text = f"{data['hours']:02d}:{data['minutes']:02d}:{data['seconds']:02d}"
        footer = (
            f"{time_text} Colombia {mode} | "
            f"S {round(second_angle)}° M {round(minute_angle)}° H {round(hour_angle)}° | "
            "Ctrl+C"
        )
        self._centered_text(grid, colors, self.footer_y, footer, COLOR_DIM)
        footer_x = (self.frame_width - len(footer)) // 2
        mode_x = footer_x + footer.index(mode)
        self._put_text(
            grid,
            colors,
            mode_x,
            self.footer_y,
            mode,
            COLOR_SECOND if data["running"] else COLOR_DIM,
        )
        return grid, colors

    def _render_menu(self):
        grid = [[" "] * self.frame_width for _ in range(self.frame_height)]
        colors = [[None] * self.frame_width for _ in range(self.frame_height)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, _, _, _ = self._angles(0.0)
        mode = "MARCHA" if data["running"] else "PAUSA"
        time_text = f"{data['hours']:02d}:{data['minutes']:02d}:{data['seconds']:02d}"

        if self.full_layout:
            status_y = 12
            angles_y = 13
            title_y = 16
            first_option_y = 19
            instruction_y = 30
        else:
            status_y = 5
            angles_y = 6
            title_y = 9
            first_option_y = 12
            instruction_y = 20

        status = f"HORA {time_text}    COLOMBIA (UTC-5)    MODO {mode}"
        self._centered_text(grid, colors, status_y, status, COLOR_STATUS)
        status_x = (self.frame_width - len(status)) // 2
        self._put_text(
            grid,
            colors,
            status_x + status.index(mode),
            status_y,
            mode,
            COLOR_SECOND if data["running"] else COLOR_DIM,
        )
        self._centered_text(
            grid,
            colors,
            angles_y,
            f"SEG {second_angle:5.1f}°    MIN {minute_angle:5.1f}°    HORA {hour_angle:5.1f}°",
            COLOR_DIM,
        )
        self._centered_text(grid, colors, title_y, "MENÚ", COLOR_SECOND)

        if self.full_layout:
            options = (
                "1 Iniciar/Reanudar",
                "2 +1s",
                "3 -1s",
                "4 +10min",
                "5 -10min",
                "6 Reiniciar",
                "7 Redibujar",
                "8 Salir",
            )
            for offset, option in enumerate(options):
                self._centered_text(
                    grid, colors, first_option_y + offset, option, COLOR_STATUS
                )
        else:
            options = (
                "1 Iniciar/Reanudar",
                "2 +1s        3 -1s",
                "4 +10min     5 -10min",
                "6 Reiniciar",
                "7 Redibujar",
                "8 Salir",
            )
            for offset, option in enumerate(options):
                self._centered_text(
                    grid, colors, first_option_y + offset, option, COLOR_STATUS
                )

        self._centered_text(
            grid,
            colors,
            instruction_y,
            "Escribe el número y pulsa ENTER",
            COLOR_DIM,
        )
        self._centered_text(
            grid,
            colors,
            instruction_y + 1,
            "ENTER solo = iniciar/reanudar",
            COLOR_DIM,
        )
        self._write_frame(
            self._rows(grid, colors)[:self.frame_height - 1],
            clear=True,
            newline=True,
        )

    def _rows(self, grid, colors):
        rows = []
        for y in range(self.frame_height):
            parts = []
            current_color = None
            for x in range(self.frame_width):
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
        if self.top_padding:
            rows = [""] * self.top_padding + list(rows)
        text = prefix + "\n".join(row + "\033[K" for row in rows)
        if newline:
            text += "\n"
        text += "\033[J"
        print(text, end="", flush=True)

    def _render_auto(self, fraction):
        grid, colors = self._build_grid(fraction)
        self._write_frame(self._rows(grid, colors))
