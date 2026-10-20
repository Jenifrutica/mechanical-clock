class DialMark:
    def __init__(self, value, angle):
        self.value = value
        self.angle = angle
        self.previous = self
        self.next = self

    def link_previous(self, mark):
        self.previous = mark

    def link_next(self, mark):
        self.next = mark

    def advance(self):
        return self.next

    def retreat(self):
        return self.previous

    def __repr__(self):
        return f"DialMark(value={self.value}, angle={self.angle})"
