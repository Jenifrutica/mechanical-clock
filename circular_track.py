from dial_mark import DialMark


class CircularTrack:
    def __init__(self, name, values, zero_value):
        self.name = name
        self.values = tuple(values)
        if not self.values:
            raise ValueError("A circular track needs at least one mark")
        if zero_value not in self.values:
            raise ValueError("The zero value must exist in the track")
        self.size = len(self.values)
        self.zero_value = zero_value
        self.marks = []
        for index, value in enumerate(self.values):
            angle = index * 360.0 / self.size
            self.marks.append(DialMark(value, angle))
        self.first = self.marks[0]
        self.last = self.marks[-1]
        self._weave()
        self.zero_mark = self.mark_for_value(zero_value)

    def _weave(self):
        for index, mark in enumerate(self.marks):
            previous_mark = self.marks[index - 1]
            next_mark = self.marks[(index + 1) % self.size]
            mark.link_previous(previous_mark)
            mark.link_next(next_mark)
        self.first.link_previous(self.last)
        self.last.link_next(self.first)

    def mark_for_value(self, value):
        mark = self.first
        for _ in range(self.size):
            if mark.value == value:
                return mark
            mark = mark.next
        raise ValueError(f"Value {value} is not part of the {self.name} track")

    def mark_at(self, position):
        while position < 0:
            position += self.size
        while position >= self.size:
            position -= self.size
        mark = self.first
        for _ in range(position):
            mark = mark.next
        return mark

    def step_forward(self, mark):
        return mark.next

    def step_backward(self, mark):
        return mark.previous

    def iter_forward(self, count=None):
        mark = self.first
        remaining = self.size if count is None else count
        for _ in range(remaining):
            yield mark
            mark = mark.next

    def validate(self):
        if len(self.marks) != self.size:
            raise AssertionError("Track size does not match its marks")
        for mark in self.marks:
            if mark.previous is None or mark.next is None:
                raise AssertionError("A circular mark cannot point to None")
            if mark.next.previous is not mark:
                raise AssertionError("The forward link is not doubly consistent")
            if mark.previous.next is not mark:
                raise AssertionError("The backward link is not doubly consistent")
        if self.first.previous is not self.last:
            raise AssertionError("The first mark does not point back to the last")
        if self.last.next is not self.first:
            raise AssertionError("The last mark does not point forward to the first")
        if self.zero_mark.value != self.zero_value:
            raise AssertionError("The zero mark is incorrect")
        return True

    def __len__(self):
        return self.size
