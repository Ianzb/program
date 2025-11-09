"""
Shuffler
"""
from enum import IntEnum

try:
    from model import *
except:
    from pySeatShuffle.model import *
import random


class SeatSequenceMode(IntEnum):
    SEQUENTIAL = 0
    RANDOM_IN_GROUP = 1
    RANDOM_IN_TABLE = 2


class SeatGroupSequenceMode(IntEnum):
    SEQUENTIAL = 0
    RANDOM = 1


class ShufflerConfig:
    def __init__(self,
                 seat_sequence_mode=SeatSequenceMode.SEQUENTIAL,
                 seat_group_sequence_mode=SeatGroupSequenceMode.SEQUENTIAL,
                 skip_unavailable=False):
        self.seat_sequence_mode = seat_sequence_mode
        self.seat_group_sequence_mode = seat_group_sequence_mode
        self.skip_unavailable = skip_unavailable


class Shuffler:
    def __init__(self, people: list[Person], seat_table: SeatTable, ruleset: Ruleset, config: ShufflerConfig = None):
        self.people = people
        self.seat_table = seat_table
        self.ruleset = ruleset
        if config is None:
            self.config = ShufflerConfig()
        else:
            self.config = config

        self.candidates = people.copy()

    def __iter__(self):
        return self

    def __next__(self):
        logging.log(logging.INFO, f"剩余人数：{len(self.people)}，座位数：{self.seat_table.count_available_seats()}")
        if len(self.people) <= 0 or self.seat_table.count_available_seats() <= 0:
            raise StopIteration
        else:
            return self.try_arranging_one()

    def shuffle_people(self):
        random.shuffle(self.people)

    def _choose_person(self):
        if len(self.candidates) <= 0:
            if self.config.skip_unavailable:
                return get_fake_person()
            raise NoValidArrangementError

        person = random.choice(self.candidates)
        self.candidates.remove(person)
        return person

    def try_arranging_one(self):
        person = self._choose_person()

        if self.seat_table.count_available_seats() > 0:
            seat: Seat = self.seat_table.get_next_available_seat(self.config)
            seat.set_user(person)

            if person.is_dummy():
                self.candidates = self.people.copy()
                return IterationResult(True, self.seat_table, seat, person, True)

            if self.ruleset.check(self.seat_table.seat_groups):  # if this arrange PASS the rules
                self.people.remove(person)
                self.candidates = self.people.copy()
                return IterationResult(True, self.seat_table, seat, person)
            seat.clear_user()
            return IterationResult(False, self.seat_table, seat, person)
        else:
            return IterationResult(False, self.seat_table, None, person)


class ShufflerBuilder:
    def __init__(self):
        self.people = []
        self.seat_table = None
        self.ruleset = None
        self.config = ShufflerConfig()

    def set_people(self, people: list[Person]):
        self.people = people
        return self

    def set_seat_table(self, seat_table: SeatTable):
        self.seat_table = seat_table
        return self

    def set_ruleset(self, ruleset: Ruleset):
        self.ruleset = ruleset
        return self

    def set_config(self, config: ShufflerConfig):
        self.config = config
        return self

    def build(self):
        return Shuffler(self.people, self.seat_table, self.ruleset, self.config)


class IterationResult:
    def __init__(self, success, seat_table: SeatTable, seat: Seat | None = None, person: Person | None = None, skipped=False):
        self.success = success
        self.seat = seat
        self.person = person
        self.seat_table = seat_table
        self.skipped = skipped


class NoValidArrangementError(Exception):
    pass
