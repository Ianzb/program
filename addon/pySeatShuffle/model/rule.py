"""
Rule Model
"""

import bidict


class Rule:
    """
    Available rule types:
    - identical_in_group: provide 1 property, returns True if the property value is identical for ALL people in the group, otherwise False
    - unique_in_group: provide 1 property, returns True if everyone has different property values in the group, otherwise False

    :param t: rule type
    :param prop: list of property names to check
    :param reversed: if True, reverses the rule logic
    """
    rule_names = bidict.bidict({"identical_in_group": "相同",
                                "unique_in_group": "不同"})

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
                # Check if the specified property is identical for all users in the group
                if not self._check_identical_in_group(group):
                    return self.reversed
            elif self.t == 'unique_in_group':
                # Check if the specified property has unique values for all users in the group
                if not self._check_unique_in_group(group):
                    return self.reversed
            else:
                raise Exception('Invalid rule type')

        # All groups satisfy the rule
        return not self.reversed

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
