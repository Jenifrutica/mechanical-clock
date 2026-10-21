from circular_track import CircularTrack
from hand import Hand
from gear_train import GearTrain


class CountdownTimer:
    def __init__(self):
        self.duration = 0.0
        self.remaining = 0.0
        self.started_at = None
        self.running = False
        self.finished = False

    def set_duration(self, seconds):
        self.duration = float(seconds)
        self.remaining = float(seconds)
        self.started_at = None
        self.running = False
        self.finished = False

    def start(self, now):
        if self.duration <= 0.0:
            return
        if self.remaining <= 0.0:
            self.remaining = self.duration
        self.started_at = now
        self.running = True
        self.finished = False

    def pause(self, now):
        if self.running:
            self.update(now)
            self.running = False
            self.started_at = None

    def toggle(self, now):
        if self.running:
            self.pause(now)
        else:
            self.start(now)

    def reset(self):
        self.remaining = self.duration
        self.running = False
        self.started_at = None
        self.finished = False

    def clear(self):
        self.duration = 0.0
        self.remaining = 0.0
        self.running = False
        self.started_at = None
        self.finished = False

    def update(self, now):
        if not self.running:
            return
        value = self.remaining - (now - self.started_at)
        if value <= 0.0:
            self.remaining = 0.0
            self.running = False
            self.started_at = None
            self.finished = True
        else:
            self.remaining = value
            self.started_at = now

    def value(self, now):
        if not self.running:
            return self.remaining
        value = self.remaining - (now - self.started_at)
        if value < 0.0:
            return 0.0
        return value


class MechanicalClock:
    def __init__(self):
        self.seconds_track = CircularTrack("seconds", range(60), 0)
        self.minutes_track = CircularTrack("minutes", range(60), 0)
        self.hours_track = CircularTrack(
            "hours",
            (12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
            12,
        )
        self.second_hand = Hand(self.seconds_track, "Segundero")
        self.minute_hand = Hand(self.minutes_track, "Minutero")
        self.hour_hand = Hand(self.hours_track, "Horario")
        self.gear_train = GearTrain()
        self.gear_train.attach(self.second_hand)
        self.gear_train.attach(self.minute_hand)
        self.gear_train.attach(self.hour_hand)
        self.is_running = False
        self.timer = CountdownTimer()
        self.reset_midnight()

    def start(self):
        self.is_running = True

    def pause(self):
        self.is_running = False

    def toggle_running(self):
        self.is_running = not self.is_running

    def tick_forward(self):
        self.gear_train.tick_forward()

    def tick_backward(self):
        self.gear_train.tick_backward()

    def fast_adjust_minutes(self, delta):
        if delta > 0:
            self.gear_train.advance_minutes(delta)
        elif delta < 0:
            self.gear_train.retreat_minutes(-delta)

    def reset_midnight(self):
        self.second_hand.reset()
        self.minute_hand.reset()
        self.hour_hand.reset()

    def set_time(self, hour, minute, second):
        if hour < 1 or hour > 12:
            raise ValueError("Hour must be between 1 and 12")
        if minute < 0 or minute > 59:
            raise ValueError("Minute must be between 0 and 59")
        if second < 0 or second > 59:
            raise ValueError("Second must be between 0 and 59")
        self.hour_hand.set_value(hour)
        self.minute_hand.set_value(minute)
        self.second_hand.set_value(second)

    def readout(self):
        return {
            "hours": self.hour_hand.value(),
            "minutes": self.minute_hand.value(),
            "seconds": self.second_hand.value(),
            "hour_angle": self.hour_hand.angle(),
            "minute_angle": self.minute_hand.angle(),
            "second_angle": self.second_hand.angle(),
            "running": self.is_running,
        }

    def validate(self):
        self.seconds_track.validate()
        self.minutes_track.validate()
        self.hours_track.validate()
        self.gear_train.validate_chain(
            ("Segundero", "Minutero", "Horario")
        )
        if len(self.seconds_track) != 60:
            raise AssertionError("The seconds track must have 60 marks")
        if len(self.minutes_track) != 60:
            raise AssertionError("The minutes track must have 60 marks")
        if len(self.hours_track) != 12:
            raise AssertionError("The hours track must have 12 marks")
        if self.hours_track.zero_value != 12:
            raise AssertionError("The hour track must start at 12")
        return True
