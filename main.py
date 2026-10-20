from mechanical_clock import MechanicalClock
from clock_view import ClockCanvasApp


def main():
    clock = MechanicalClock()
    app = ClockCanvasApp(clock)
    app.run()


if __name__ == "__main__":
    main()
