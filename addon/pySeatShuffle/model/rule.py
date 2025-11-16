"""
Rule Model

Available rule types:

- **identical_in_group:** provide 1 property, returns True if the property value is identical for ALL people in the group, otherwise False
- **unique_in_group:** provide 1 property, returns True if everyone has different property values in the group, otherwise False
- **check_sum_constraint:** provide 3 property, prop_key, op (==, !=, <, >, <=, >=) and value, return True if the sum of the specific prop meets the constraint
- **check_average_constraint:** provide 3 property, prop_key, op (==, !=, <, >, <=, >=) and value, return True if the average of the specific prop meets the constraint
- **check_sd_constraint:** provide 3 property, prop_key, op (==, !=, <, >, <=, >=) and value, return True if the standard deviation of the specific prop meets the constraint
"""

import math
from functools import lru_cache
import bidict


class Rule:
    """
    Rule model class

    :param t: rule type
    :param prop: list of property names to check
    :param reversed: if True, reverses the rule logic
    """
    rule_names = bidict.bidict({"identical_in_group": "相同",
                                "unique_in_group": "不同",
                                "check_sum_constraint": "和满足条件",
                                "check_average_constraint": "均值满足条件",
                                "check_sd_constraint": "标准差满足条件"})

    def __init__(self, t, prop: list, reversed=False):
        self.t = t
        self.prop = prop
        self.reversed = reversed

    def check(self, groups):
        """
        Check if the rule is satisfied for all groups

        :param groups: list of SeatGroup objects from SeatTable
        :return: True if rule is satisfied, False otherwise
        """
        for group in groups:
            if self.t == 'identical_in_group':
                if not self._check_identical_in_group(group):
                    return self.reversed
            elif self.t == 'unique_in_group':
                if not self._check_unique_in_group(group):
                    return self.reversed
            elif self.t == 'check_sum_constraint':
                if not self._check_sum_constraint(group):
                    return self.reversed
            elif self.t == 'check_average_constraint':
                if not self._check_average_constraint(group):
                    return self.reversed
            elif self.t == 'check_sd_constraint':
                if not self._check_sd_constraint(group):
                    return self.reversed
            else:
                raise Exception('Invalid rule type')

        # All groups satisfy the rule
        return not self.reversed

    @lru_cache(128)
    def _check_identical_in_group(self, seat_group):
        """
        Check if all users in the group have the same value for the specified property

        :param seat_group: SeatGroup object to check
        :return: True if all users have identical property values, False otherwise
        """
        property_values = set()

        for seat in seat_group.get_seats():
            if seat.user is not None:  # Only check seats with users
                prop_value = seat.user.get_property(self.prop[0])
                if prop_value is not None:  # Only process users with the property
                    property_values.add(prop_value)

        # Return True if group has no users or all users have identical property values
        return len(property_values) <= 1

    @lru_cache(128)
    def _check_unique_in_group(self, seat_group):
        """
        Check if all users in the group have unique values for the specified property

        :param seat_group: SeatGroup object to check
        :return: True if all users have unique property values, False otherwise
        """
        property_values = []

        for seat in seat_group.get_seats():
            if seat.user is not None:  # Only check seats with users
                prop_value = seat.user.get_property(self.prop[0])
                if prop_value is not None:  # Only process users with the property
                    if prop_value in property_values:
                        return False  # Duplicate value found
                    property_values.append(prop_value)

        # No duplicate values found
        return True

    def __check_constraint(self, value, invoker):
        if self.prop[1] == '==':
            return value == self.prop[2]
        elif self.prop[1] == '!=':
            return value != self.prop[2]
        elif self.prop[1] == '<':
            return value < self.prop[2]
        elif self.prop[1] == '>':
            return value > self.prop[2]
        elif self.prop[1] == '<=':
            return value <= self.prop[2]
        else:
            return ValueError(f"Invalid rule prop {self.prop[1]} for {invoker}!")

    @lru_cache(128)
    def _check_sum_constraint(self, seat_group):
        """
        Check if the sum of the specified property values for all users in the group is within a specified range

        :param seat_group: SeatGroup object to check
        :return: True if the sum is within the range, False otherwise
        """
        try:
            prop_sum = sum(seat.user.get_property(self.prop[0])
                           for seat in seat_group.get_seats()
                           if seat.user is not None
                           and seat.user.get_property(self.prop[0]) is not None)
        except TypeError as e:
            raise ValueError(f"Failed to summate the prop {self.prop[0]}, caused by: {e}")

        return self.__check_constraint(prop_sum, 'check_sum_constraint')

    @lru_cache(128)
    def _check_average_constraint(self, seat_group):
        """
        Check if the average of the specified property values for all users in the group is within a specified range

        :param seat_group: SeatGroup object to check
        :return: True if the average is within the range, False otherwise
        """
        try:
            prop_sum = sum(seat.user.get_property(self.prop[0])
                           for seat in seat_group.get_seats()
                           if seat.user is not None
                           and seat.user.get_property(self.prop[0]) is not None)
            prop_count = len(seat_group.get_seats())
            prop_average = prop_sum / prop_count
        except TypeError as e:
            raise ValueError(f"Failed to calculate the average of the prop {self.prop[0]}, caused by: {e}")

        return self.__check_constraint(prop_average, 'check_average_constraint')

    @lru_cache(128)
    def _check_sd_constraint(self, seat_group):
        """
        Check if the standard deviation of the specified property values for all users in the group is within a specified range

        :param seat_group: SeatGroup object to check
        :return: True if the standard deviation is within the range, False otherwise
        """
        try:
            prop_sum = sum(seat.user.get_property(self.prop[0])
                           for seat in seat_group.get_seats()
                           if seat.user is not None
                           and seat.user.get_property(self.prop[0]) is not None)
            prop_count = len(seat_group.get_seats())
            prop_average = prop_sum / prop_count
            prop_sd = math.sqrt(sum((seat.user.get_property(self.prop[0]) - prop_average) ** 2
                                    for seat in seat_group.get_seats()
                                    if seat.user is not None
                                    and seat.user.get_property(self.prop[0]) is not None) / prop_count)
        except TypeError as e:
            raise ValueError(f"Failed to calculate the standard deviation of the prop {self.prop[0]}, caused by: {e}")

        return self.__check_constraint(prop_sd, 'check_sd_constraint')

    def __repr__(self):
        return f"Rule(t={self.t}, prop={self.prop}, reversed={self.reversed})"
