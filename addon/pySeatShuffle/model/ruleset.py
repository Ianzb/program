"""
Ruleset Model
"""

from .rule import *

class Ruleset:
    def __init__(self, rules: list[Rule], relations=None):  # TODO: relations
        self.rules = rules
        self.relations = relations

    def check(self, seat_groups):
        for rule in self.rules:
            if not rule.check(seat_groups):
                return False
        return True

