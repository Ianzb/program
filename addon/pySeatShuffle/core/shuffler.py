"""
Shuffler
"""
import logging

from ..model import *

import random


class Shuffler:
    def __init__(self, people: list[Person], seat_table: SeatTable, ruleset: Ruleset):
        self.people = people
        self.seat_table = seat_table
        self.ruleset = ruleset

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

    def try_arranging_one(self):
        if len(self.candidates) <= 0:
            raise NoValidArrangementError

        person = random.choice(self.candidates)
        self.candidates.remove(person)

        if self.seat_table.count_available_seats() > 0:
            seat: Seat = self.seat_table.get_next_available_seat()
            seat.set_user(person)
            if self.ruleset.check(self.seat_table.seat_groups):  # if this arrange PASS the rules
                self.people.remove(person)
                self.candidates = self.people.copy()
                return IterationResult(True, self.seat_table, seat, person)
            seat.clear_user()
            return IterationResult(False, self.seat_table, seat, person)
        else:
            return IterationResult(False, self.seat_table, None, person)


class IterationResult:
    def __init__(self, success, seat_table: SeatTable, seat: Seat | None = None, person: Person | None = None):
        self.success = success
        self.seat = seat
        self.person = person
        self.seat_table = seat_table


class NoValidArrangementError(Exception):
    pass
