"""
Person Model
"""


class Person:
    def __init__(self, name: str, properties: dict):
        self.name = name
        self.properties = properties

    def get_property(self, property_name: str):
        return self.properties.get(property_name)

    def get_properties(self):
        return self.properties

    def get_name(self):
        return self.name

    def __str__(self):
        return f"Person(name={self.name}, properties={self.properties})"

    def to_dict(self):
        return {
            "name": self.name,
            "properties": self.properties
        }

    def __getitem__(self, item):
        if item == "name":
            return self.name
        else:
            return self.properties[item]
