"""
Seat Table Model
"""
import logging
import random

try:
    from core.constants import *
except:
    from pySeatShuffle.core.constants import *


class Seat:
    def __init__(self, pos: tuple[int, int], name: str = None):
        self.pos = pos  # row, col
        self.name = name
        self.user = None
        self.parent = None  # SeatGroup

    def is_empty(self):
        return self.user is None or self.user.is_dummy()

    def is_available(self):
        return self.user is None

    def get_pos(self):
        """
        :return: row, column
        """
        return self.pos

    def get_user(self):
        return self.user

    def set_user(self, user):
        self.user = user

    def clear_user(self):
        self.user = None

    def get_seat_group(self):
        return self.parent

    def __str__(self):
        return f"Seat({self.pos}, {self.name}, {self.user})"

    def to_dict(self):
        return {
            "pos": self.pos,
            "name": self.name,
            "user": self.user.to_dict() if self.user is not None else None
        }

    def __hash__(self):
        return hash((self.pos, self.name, self.user))


class SeatGroup:
    def __init__(self, seats: list[Seat], name=None):
        for seat in seats:
            seat.parent = self
        self.seats = seats
        self.name = name
        self.parent = None  # SeatTable

        self._cursor = 0

    def get_seats(self):
        return self.seats

    def get_name(self):
        return self.name

    def count_seats(self):
        return len(self.seats)

    def count_available_seats(self):
        return len([seat for seat in self.seats if seat.is_available()])

    def get_next_available_seat(self, config):
        if config.seat_sequence_mode == 0:
            return next((seat for seat in self.seats if seat.is_available()), None)
        elif config.seat_sequence_mode == 1:
            available_seats = [seat for seat in self.seats if seat.is_available()]
            return random.choice(available_seats) if available_seats else None
        return None

    def reset_cursor(self):
        self._cursor = 0

    def __str__(self):
        return f"SeatGroup({self.name}, {self.count_seats()}, [" + ", ".join([str(seat) for seat in self.seats]) + "])"

    def to_dict(self):
        return {
            "name": self.name,
            "seats": [seat.to_dict() for seat in self.seats]
        }

    def __hash__(self):
        return hash((self.name, tuple(self.seats)))


class SeatTable:
    def __init__(self, seat_groups: list[SeatGroup], size, name=None, metadata=None, create_cache=True):
        """
        :param seat_groups: list of SeatGroup
        :param size: row, column
        :param name:
        :param metadata:
        """
        for seat_group in seat_groups:
            seat_group.parent = self
        self.seat_groups = seat_groups
        self.size = size
        self.name = name

        if metadata is None:
            self.metadata = SeatTableMetadata("unknown", "")
        else:
            self.metadata = metadata

        self.cache = {}
        if create_cache:
            self._create_cache()

        self._cursor = 0

    def get_offset(self):
        """
        :return: row, column
        """
        min_r = min([seat.get_pos()[0] for group in self.seat_groups for seat in group.get_seats()])
        min_c = min([seat.get_pos()[1] for group in self.seat_groups for seat in group.get_seats()])
        return min_r, min_c

    def set_user_in_pos(self, pos: tuple[int, int], user):
        """
        Set user in the specified position.
        :param pos: (row, column)
        :param user: User object
        :return: True if successful, False otherwise
        """
        if self.cache and pos in self.cache:
            self.cache[pos] = user
            return True

        for seat_group in self.seat_groups:
            for seat in seat_group.get_seats():
                if seat.get_pos() == pos:
                    seat.set_user(user)
                    return True
        return False

    def remove_user_in_pos(self, pos: tuple[int, int]):
        """
        Remove user in the specified position.
        :param pos: (row, column)
        :return: True if successful, False otherwise
        """
        if self.cache is not None and pos in self.cache:
            self.cache[pos] = None
            return True

        for seat_group in self.seat_groups:
            for seat in seat_group.get_seats():
                if seat.get_pos() == pos:
                    seat.clear_user()
                    return True
        return False

    def clear_all_users(self):
        """
        Clear all users in the seat table.
        """
        self.reset_cursor()

        for seat_group in self.seat_groups:
            seat_group._cursor = 0
            for seat in seat_group.get_seats():
                seat.clear_user()

    def reset_cursor(self):
        self._cursor = -1
        for seat_group in self.seat_groups:
            seat_group.reset_cursor()

    def get_seat_groups(self):
        return self.seat_groups

    def get_size(self):
        """
        :return: rows, columns
        """
        return self.size

    def get_name(self):
        return self.name

    def count_seats(self):
        return sum([seat_group.count_seats() for seat_group in self.seat_groups])

    def count_available_seats(self):
        return sum([seat_group.count_available_seats() for seat_group in self.seat_groups])

    def get_next_available_seat(self, config):
        if self._cursor == -1:
            if config.seat_group_sequence_mode == 0:
                self._cursor += 1
            elif config.seat_group_sequence_mode == 1:
                self._cursor = random.randrange(len(self.seat_groups))
        if self._cursor < self.count_seats():
            if config.seat_sequence_mode == 2:
                candidate = self.get_random_seat(True)
            else:
                candidate = self.seat_groups[self._cursor].get_next_available_seat(config)
            if candidate is None:
                if config.seat_group_sequence_mode == 0:
                    self._cursor += 1
                elif config.seat_group_sequence_mode == 1:
                    self._cursor = random.randrange(len(self.seat_groups))

                return self.get_next_available_seat(config)
            return candidate
        self._cursor = -1
        return None

    def _create_cache(self):
        for seat_group in self.seat_groups:
            for seat in seat_group.get_seats():
                self.cache[tuple(seat.get_pos())] = seat

    def get_random_seat(self, is_available=True):
        return random.choice([seat for seat_group in self.seat_groups
                              for seat in seat_group.get_seats()
                              if (seat.is_available() if is_available else True)])

    def get_random_group(self, not_full=True):
        return random.choice([seat_group for seat_group in self.seat_groups
                              if (seat_group.count_available_seats() < seat_group.count_seats() if not_full else True)])

    def __str__(self):
        return f"SeatTable({self.name}, {self.size}, \n" + "\n".join([str(seat_group) for seat_group in self.seat_groups]) + "\n)"

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "seat_groups": [seat_group.to_dict() for seat_group in self.seat_groups]
        }


class SeatTableMetadata:
    def __init__(self, format, file_path):
        self.format = format
        self.file_path = file_path

    def __str__(self):
        return f"SeatTableMetadata(format={self.format}, file_path={self.file_path})"


class SeatTableMetadataXlsx(SeatTableMetadata):
    def __init__(self, file_path):
        super().__init__(F_XLSX, file_path)
        self.gen_time_cell_pos = None  # 存储格式为 (column, row)，都从1开始
        self.offset_row = 0
        self.offset_col = 0


class SeatTableMetadataJson(SeatTableMetadata):
    def __init__(self, file_path):
        super().__init__(F_JSON, file_path)
