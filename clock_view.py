from clock_pacing import PacingClock

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
        self.menu_mode = False
        self.menu_error = ""
        self.terminal_columns = 114
        self.terminal_lines = 34
        self.pacing = PacingClock()
        self._configure_layout()

    def _ask_terminal_size(self):
        text = input("Tamaño de terminal (columnas filas) [114 34]: ").strip()
        if not text:
            return
        parts = text.split()
        if len(parts) != 2:
            return
        try:
            columns = int(parts[0])
            lines = int(parts[1])
        except ValueError:
            return
        if columns < 40 or lines < 20:
            return
        self.terminal_columns = columns
        self.terminal_lines = lines
        self._configure_layout()

    def _ask_time(self):
        while True:
            text = input("Hora local (HH:MM:SS): ").strip()
            parts = text.split(":")
            if len(parts) not in (2, 3):
                print("Formato inválido. Usa HH:MM:SS")
                continue
            if not all(part.isdigit() for part in parts):
                print("Formato inválido. Usa solo números")
                continue
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2]) if len(parts) == 3 else 0
            if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                print("Hora inválida")
                continue
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            self.clock.set_time(hour_12, minute, second)
            return

    def _configure_layout(self):
        self.frame_width = max(40, self.terminal_columns - 1)
        self.side_layout = self.terminal_columns >= 100 and self.terminal_lines >= 34
        self.full_layout = self.terminal_lines >= 34 and not self.side_layout
        if self.side_layout:
            self.frame_height = 34
            self.center_x = 29
            self.center_y = 17
            self.radius_x = 25
            self.radius_y = 14
            self.footer_y = 33
            self.separator_x = 59
            self.panel_x = 62
        elif self.full_layout:
            self.frame_height = 34
            self.center_x = self.frame_width // 2
            self.center_y = 17
            self.radius_x = min(25, max(10, (self.frame_width - 6) // 2))
            self.radius_y = max(6, round(self.radius_x * 14 / 25))
            self.footer_y = 33
            self.separator_x = None
            self.panel_x = None
        else:
            self.frame_height = 24
            self.center_x = self.frame_width // 2
            self.center_y = 11
            self.radius_x = min(19, max(8, (self.frame_width - 4) // 2))
            self.radius_y = max(4, round(self.radius_x * 11 / 19))
            self.footer_y = 23
            self.separator_x = None
            self.panel_x = None
        self.top_padding = max(0, (self.terminal_lines - self.frame_height - 2) // 2)

    def _welcome(self):
        print("\033[2J\033[H")
        print("        .-\"\"\"-." )
        print("       /  _ _  \\")
        print("      |  (o o)  |")
        print("       \\   ^   /")
        print("        '-...-'")
        print("         /| |\\")
        print("        /_| |_\\")
        print("")
        print("¡Hola! Soy tu reloj.")
        print("Antes de comenzar, necesito la hora local en formato HH:MM:SS.")
        print("")
        self._ask_time()
        print("")
        print("Perfecto. ¡Vamos!")

    def run(self):
        self._welcome()
        self.clock.start()
        self._enter_screen()
        try:
            self._run_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self._leave_screen()

    def _run_loop(self):
        print("\033[2J\033[H", end="", flush=True)
        next_tick = 1.0
        while True:
            try:
                fraction = self.pacing.now() - (next_tick - 1.0)
                if fraction < 0.0:
                    fraction = 0.0
                elif fraction > 1.0:
                    fraction = 1.0
                self._render_auto(fraction)
                self.pacing.wait_frame()
                self.pacing.advance()
                while self.pacing.now() >= next_tick:
                    self.clock.tick_forward()
                    next_tick += 1.0
                self.clock.timer.update(self.pacing.now())
                if self.clock.timer.finished:
                    self._timer_alert()
            except KeyboardInterrupt:
                self._blocking_menu()

    def _format_timer(self, seconds):
        total = int(seconds + 0.999)
        hours = total // 3600
        minutes = (total % 3600) // 60
        secs = total % 60
        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    def _timer_alert(self):
        print("\033[2J\033[H", end="", flush=True)
        print("        .-\"\"\"-." )
        print("       /  ! !  \\")
        print("      |  (o o)  |")
        print("       \\   ^   /")
        print("        '-...-'")
        print("")
        print("        ¡TIEMPO CUMPLIDO!")
        print("")
        try:
            input("Presiona Enter para cerrar la alerta: ")
        except (EOFError, KeyboardInterrupt):
            pass
        self.clock.timer.clear()
        print("\033[2J\033[H", end="", flush=True)

    def _timer_menu(self):
        while True:
            timer = self.clock.timer
            value = timer.value(self._time_now())
            print("\033[2J\033[H", end="", flush=True)
            print("TEMPORIZADOR")
            print("Duración:", self._format_timer(timer.duration) if timer.duration else "--:--")
            print("Restante:", self._format_timer(value) if timer.duration else "--:--")
            if timer.running:
                print("Estado: ACTIVO")
            elif timer.duration:
                print("Estado: PAUSADO")
            else:
                print("Estado: SIN CONFIGURAR")
            print("")
            print("1 10 minutos")
            print("2 1 minuto")
            print("3 30 segundos")
            print("4 Tiempo personalizado")
            print("5 Iniciar/Pausar")
            print("6 Reiniciar")
            print("7 Volver al menú")
            choice = input("Opción (1-7): ").strip()
            if len(choice) != 1 or choice not in "1234567":
                print("Solo se permite un número del 1 al 7")
                input("Enter para continuar...")
                continue
            if choice == "1":
                timer.set_duration(600)
                timer.start(self._time_now())
                self.menu_mode = False
                return
            elif choice == "2":
                timer.set_duration(60)
                timer.start(self._time_now())
                self.menu_mode = False
                return
            elif choice == "3":
                timer.set_duration(30)
                timer.start(self._time_now())
                self.menu_mode = False
                return
            elif choice == "4":
                text = input("Duración en segundos: ").strip()
                if text.isdigit() and int(text) > 0:
                    timer.set_duration(int(text))
                    timer.start(self._time_now())
                    self.menu_mode = False
                    return
                print("Duración inválida")
                input("Enter para continuar...")
            elif choice == "5":
                if timer.duration <= 0:
                    print("Primero configura una duración")
                    input("Enter para continuar...")
                else:
                    if timer.running:
                        timer.pause(self._time_now())
                    else:
                        timer.start(self._time_now())
                        self.menu_mode = False
                        return
            elif choice == "6":
                timer.reset()
            elif choice == "7":
                return

    def _config_menu(self):
        while True:
            print("\033[2J\033[H", end="", flush=True)
            print("CONFIGURACIÓN")
            print(f"Resolución: {self.terminal_columns} x {self.terminal_lines}")
            print(f"Velocidad: {self.pacing.spin_per_frame} ciclos/frame")
            print("")
            print("1 Cambiar resolución")
            print("2 Calibrar velocidad")
            print("3 Volver")
            choice = input("Opción (1-3): ").strip()
            if len(choice) != 1 or choice not in "123":
                print("Solo se permite un número del 1 al 3")
                input("Enter para continuar...")
                continue
            if choice == "1":
                text = input("Nuevo tamaño (columnas filas): ").strip()
                parts = text.split()
                if len(parts) == 2:
                    try:
                        columns = int(parts[0])
                        lines = int(parts[1])
                    except ValueError:
                        columns = 0
                        lines = 0
                    if columns >= 40 and lines >= 20:
                        self.terminal_columns = columns
                        self.terminal_lines = lines
                        self._configure_layout()
                        input("Resolución aplicada. Enter para continuar...")
            elif choice == "2":
                print("")
                print("Mide 10 segundos reales y pulsa Ctrl+C al terminar.")
                print("Usa un reloj o el teléfono como referencia.")
                input("Enter para comenzar la calibración...")
                start = self.pacing.now()
                try:
                    while True:
                        elapsed = self.pacing.now() - start
                        print(f"\rTiempo interno: {elapsed:5.1f} s", end="", flush=True)
                        self.pacing.wait_frame()
                        self.pacing.advance()
                except KeyboardInterrupt:
                    elapsed = self.pacing.now() - start
                    print("")
                    text = input("Segundos reales transcurridos [10]: ").strip()
                    if not text:
                        real = 10.0
                    else:
                        try:
                            real = float(text)
                        except ValueError:
                            real = 10.0
                    self.pacing.calibrate(real, elapsed)
                    print(f"Velocidad ajustada: {self.pacing.spin_per_frame} ciclos/frame")
                    input("Enter para continuar...")
            elif choice == "3":
                return

    def _blocking_menu(self):
        self.menu_mode = True
        self.menu_error = ""
        try:
            while True:
                self._render_menu(0.0)
                try:
                    choice = input("Opción (0-9): ").strip()
                except KeyboardInterrupt:
                    self.menu_mode = False
                    return
                if len(choice) != 1 or choice not in "0123456789":
                    self.menu_error = "Solo se permite un número del 0 al 9"
                    continue
                self.menu_error = ""
                self._handle_command(choice)
                if not self.menu_mode:
                    return
        finally:
            self.menu_mode = False

    def _handle_command(self, choice):
        if choice == "1":
            self.menu_mode = False
            self.clock.start()
        elif choice == "2":
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
            self._ask_time()
            self.clock.start()
            self.menu_mode = False
        elif choice == "9":
            self._timer_menu()
        elif choice == "0":
            self._config_menu()

    def _enter_screen(self):
        print(
            "\033[?1049h\033[2J\033[H\033[?25l\033]0;Reloj\007",
            end="",
            flush=True,
        )

    def _leave_screen(self):
        print("\033[0m\033[?25h\033[?1049l", end="", flush=True)

    def _time_now(self):
        return self.pacing.now()

    def _format_clock_time(self, data, fraction):
        hour = 0 if data["hours"] == 12 else data["hours"]
        total = hour * 3600 + data["minutes"] * 60 + data["seconds"] + fraction
        total = total % 43200
        seconds = int(total) % 60
        minutes = (int(total) // 60) % 60
        hours = int(total) // 3600
        if hours == 0:
            hours = 12
        tenths = int((total - int(total)) * 10)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{tenths}"

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

    def _panel_x_for(self, text):
        panel_width = self.frame_width - self.panel_x
        return self.panel_x + max(0, (panel_width - len(text)) // 2)

    def _panel_text(self, grid, colors, y, text, color=None):
        self._put_text(grid, colors, self._panel_x_for(text), y, text, color)

    def _panel_mode(self, grid, colors, y, mode, running):
        text = f"MODO {mode}"
        x = self._panel_x_for(text)
        self._put_text(grid, colors, x, y, "MODO ", COLOR_STATUS)
        self._put_text(
            grid,
            colors,
            x + 5,
            y,
            mode,
            COLOR_SECOND if running else COLOR_DIM,
        )

    def _draw_separator(self, grid, colors):
        for y in range(2, self.frame_height - 2):
            grid[y][self.separator_x] = "│"
            colors[y][self.separator_x] = COLOR_RIM

    def _build_side_grid(self, fraction):
        grid = [[" "] * self.frame_width for _ in range(self.frame_height)]
        colors = [[None] * self.frame_width for _ in range(self.frame_height)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, second_position, minute_position, hour_position = (
            self._angles(fraction)
        )
        self._draw_dial(grid, colors, second_position, minute_position, hour_position)
        self._draw_separator(grid, colors)

        mode = "MARCHA" if data["running"] else "PAUSA"
        time_text = self._format_clock_time(data, fraction)
        self._panel_text(grid, colors, 3, time_text, COLOR_STATUS)
        self._panel_text(grid, colors, 4, "Hora local", COLOR_DIM)
        self._panel_mode(grid, colors, 6, mode, data["running"])

        self._panel_text(grid, colors, 9, "ÁNGULOS", COLOR_SECOND)
        self._panel_text(
            grid, colors, 10, f"SEG  {round(second_angle)}°", COLOR_STATUS
        )
        self._panel_text(
            grid, colors, 11, f"MIN  {round(minute_angle)}°", COLOR_STATUS
        )
        self._panel_text(
            grid, colors, 12, f"HORA {round(hour_angle)}°", COLOR_STATUS
        )

        timer_value = self.clock.timer.value(self._time_now())
        if self.clock.timer.duration:
            timer_label = self._format_timer(timer_value)
            if self.clock.timer.running:
                timer_state = "ACTIVO"
            else:
                timer_state = "PAUSADO"
            timer_duration = self._format_timer(self.clock.timer.duration)
        else:
            timer_label = "--:--"
            timer_state = "SIN CONFIGURAR"
            timer_duration = "--:--"
        self._panel_text(grid, colors, 15, "TEMPORIZADOR", COLOR_SECOND)
        self._panel_text(grid, colors, 16, timer_label, COLOR_STATUS)
        self._panel_text(grid, colors, 17, timer_state, COLOR_DIM)
        self._panel_text(grid, colors, 18, f"Duración {timer_duration}", COLOR_DIM)

        self._panel_text(grid, colors, 21, "CONTROLES", COLOR_SECOND)
        self._panel_text(grid, colors, 22, "Ctrl+C menú", COLOR_STATUS)
        self._panel_text(grid, colors, 23, "2/3  ±1s", COLOR_DIM)
        self._panel_text(grid, colors, 24, "4/5  ±10min", COLOR_DIM)
        self._panel_text(grid, colors, 25, "6  reiniciar reloj", COLOR_DIM)
        self._panel_text(grid, colors, 26, "8  ajustar hora", COLOR_DIM)
        return grid, colors

    def _render_side_menu(self, fraction):
        grid = [[" "] * self.frame_width for _ in range(self.frame_height)]
        colors = [[None] * self.frame_width for _ in range(self.frame_height)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, second_position, minute_position, hour_position = (
            self._angles(fraction)
        )
        self._draw_dial(grid, colors, second_position, minute_position, hour_position)
        self._draw_separator(grid, colors)
        mode = "MARCHA" if data["running"] else "PAUSA"
        time_text = self._format_clock_time(data, fraction)
        self._panel_text(grid, colors, 3, f"HORA {time_text}", COLOR_STATUS)
        self._panel_text(grid, colors, 4, "Hora local", COLOR_DIM)
        self._panel_mode(grid, colors, 5, mode, data["running"])
        self._panel_text(grid, colors, 7, "MENÚ", COLOR_SECOND)
        options = (
            "1 Volver al reloj",
            "2 +1s",
            "3 -1s",
            "4 +10min",
            "5 -10min",
            "6 Reiniciar reloj",
            "8 Ajustar hora",
            "9 Temporizador",
            "0 Configuración",
        )
        for offset, option in enumerate(options):
            self._panel_text(grid, colors, 9 + offset, option, COLOR_STATUS)
        self._panel_text(grid, colors, 20, "Escribe el número", COLOR_DIM)
        self._panel_text(grid, colors, 21, "y pulsa ENTER", COLOR_DIM)
        timer_value = self.clock.timer.value(self._time_now())
        timer_label = self._format_timer(timer_value) if self.clock.timer.duration else "--:--"
        if self.clock.timer.running:
            timer_state = "ACTIVO"
        elif self.clock.timer.duration:
            timer_state = "PAUSADO"
        else:
            timer_state = "SIN CONFIGURAR"
        self._panel_text(
            grid, colors, 23, f"TEMPORIZADOR {timer_state}", COLOR_SECOND
        )
        self._panel_text(grid, colors, 24, timer_label, COLOR_STATUS)
        self._panel_text(
            grid,
            colors,
            26,
            f"SEG {round(second_angle)}°  MIN {round(minute_angle)}°  HORA {round(hour_angle)}°",
            COLOR_DIM,
        )
        self._panel_text(grid, colors, 28, "La hora sigue avanzando", COLOR_DIM)
        if self.menu_error:
            self._panel_text(grid, colors, 30, self.menu_error, COLOR_SECOND)
        return self._rows(grid, colors)[: self.frame_height - 1]

    def _build_grid(self, fraction):
        if self.side_layout:
            return self._build_side_grid(fraction)
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
            f"{time_text} Local {mode} | "
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

    def _render_menu(self, fraction):
        if self.side_layout:
            self._write_frame(self._render_side_menu(fraction), clear=True)
            return
        grid = [[" "] * self.frame_width for _ in range(self.frame_height)]
        colors = [[None] * self.frame_width for _ in range(self.frame_height)]
        data = self.clock.readout()
        second_angle, minute_angle, hour_angle, _, _, _ = self._angles(fraction)
        mode = "MARCHA" if data["running"] else "PAUSA"
        time_text = self._format_clock_time(data, fraction)

        if self.full_layout:
            status_y = 9
            angles_y = 10
            title_y = 13
            first_option_y = 15
            instruction_y = 27
        else:
            status_y = 5
            angles_y = 6
            title_y = 9
            first_option_y = 12
            instruction_y = 20

        status = f"HORA {time_text}    HORA LOCAL    MODO {mode}"
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
                "1 Volver al reloj",
                "2 +1s",
                "3 -1s",
                "4 +10min",
                "5 -10min",
                "6 Reiniciar reloj",
                "8 Ajustar hora",
                "9 Temporizador",
                "0 Configuración",
            )
            for offset, option in enumerate(options):
                self._centered_text(
                    grid, colors, first_option_y + offset, option, COLOR_STATUS
                )
        else:
            options = (
                "1 Volver al reloj",
                "2 +1s        3 -1s",
                "4 +10min     5 -10min",
                "6 Reiniciar reloj",
                "8 Ajustar hora",
                "9 Temporizador  0 Configuración",
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
            "La hora sigue avanzando",
            COLOR_DIM,
        )
        if self.menu_error:
            self._centered_text(
                grid, colors, instruction_y + 2, self.menu_error, COLOR_SECOND
            )
        self._write_frame(self._rows(grid, colors)[:self.frame_height - 1], clear=True)

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
        prefix = "\033[?1049h\033[2J\033[H" if clear else "\033[?1049h\033[H"
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
