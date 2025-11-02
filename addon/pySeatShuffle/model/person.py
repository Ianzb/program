"""
Person Model
"""


class Person:
    def __init__(self, id: int, properties: dict, key: str):
        self.id = str(id)
        self.key = key
        self.properties = properties

    def get_property(self, property_name: str):
        return self.properties.get(property_name)

    def get_properties(self):
        return self.properties

    def get_id(self):
        return self.id

    @property
    def name(self):
        name = self.properties.get(self.key)
        return name if name else self.key

    def get_name(self):
        return self.name

    def is_dummy(self):
        return False

    def __str__(self):
        return f"Person(id={self.id}, name={self.name}, properties={self.properties})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "properties": self.properties
        }

    def __getitem__(self, item):
        return self.properties[item]


class DummyPerson(Person):
    def __init__(self, id: int):
        super().__init__(id, {}, "Dummy")

    def is_dummy(self):
        return True
