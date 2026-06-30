from enum import Enum

class RepeatMode(Enum):
    OFF = 0
    ONE = 1
    ALL = 2
    def next(self):
        # converted all enum values to list
        cls_members = list(self.__class__)
        current_index = cls_members.index(self)
        # next value
        next_index = (current_index + 1) % len(cls_members)
        return cls_members[next_index]