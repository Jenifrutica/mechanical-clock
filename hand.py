class Hand:
    def __init__(self, track, label):
        self.track = track
        self.label = label
        self.current_mark = track.zero_mark
        self.next_hand = None

    def advance(self):
        self.current_mark = self.current_mark.next
        return self.current_mark is self.track.zero_mark

    def retreat(self):
        previous_mark = self.current_mark
        self.current_mark = self.current_mark.previous
        return previous_mark is self.track.zero_mark

    def set_value(self, value):
        self.current_mark = self.track.mark_for_value(value)

    def reset(self):
        self.current_mark = self.track.zero_mark

    def value(self):
        return self.current_mark.value

    def angle(self):
        return self.current_mark.angle

    def attach_next_hand(self, hand):
        if self.next_hand is not None:
            raise ValueError(f"{self.label} already has a linked hand")
        self.next_hand = hand
