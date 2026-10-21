class PacingClock:
    def __init__(self, frame_delta=0.1, spin_per_frame=5500000):
        self.frame_delta = frame_delta
        self.spin_per_frame = spin_per_frame
        self.seconds = 0.0

    def now(self):
        return self.seconds

    def advance(self):
        self.seconds += self.frame_delta

    def wait_frame(self):
        for _ in range(self.spin_per_frame):
            pass

    def calibrate(self, real_seconds, internal_seconds):
        if real_seconds <= 0.0 or internal_seconds <= 0.0:
            return
        self.spin_per_frame = int(
            self.spin_per_frame * internal_seconds / real_seconds
        )
