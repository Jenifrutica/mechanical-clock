class GearTrain:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def attach(self, hand):
        if self.head is None:
            self.head = hand
        else:
            self.tail.attach_next_hand(hand)
        self.tail = hand
        self.size += 1

    def _cascade_forward(self, hand):
        while hand is not None:
            carried = hand.advance()
            if not carried:
                return
            hand = hand.next_hand

    def _cascade_backward(self, hand):
        while hand is not None:
            borrowed = hand.retreat()
            if not borrowed:
                return
            hand = hand.next_hand

    def tick_forward(self):
        if self.head is not None:
            self._cascade_forward(self.head)

    def tick_backward(self):
        if self.head is not None:
            self._cascade_backward(self.head)

    def advance_minutes(self, steps=1):
        minute_hand = self.head.next_hand
        for _ in range(steps):
            self._cascade_forward(minute_hand)

    def retreat_minutes(self, steps=1):
        minute_hand = self.head.next_hand
        for _ in range(steps):
            self._cascade_backward(minute_hand)

    def readout(self):
        values = []
        hand = self.head
        while hand is not None:
            values.append((hand.label, hand.value()))
            hand = hand.next_hand
        return values

    def validate_chain(self, expected_labels=None):
        if self.head is None:
            raise AssertionError("The gear train is empty")
        if self.tail.next_hand is not None:
            raise AssertionError("The last hand cannot have a next hand")
        labels = []
        hand = self.head
        while hand is not None:
            labels.append(hand.label)
            hand = hand.next_hand
        if len(labels) != self.size:
            raise AssertionError("The gear train size is inconsistent")
        if expected_labels is not None and tuple(labels) != tuple(expected_labels):
            raise AssertionError("The gear train order is incorrect")
        return True
