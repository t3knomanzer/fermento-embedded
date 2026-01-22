class JarModel(object):
    def __init__(self, name, distance):
        self.name = name
        self.distance = distance

    @classmethod
    def from_dict(cls, dict_):
        cls.validate_dict(dict_)
        return JarModel(dict_["name"], dict_["distance"])

    def to_dict(self):
        return {"name": self.name, "distance": self.distance}

    @classmethod
    def validate_dict(self, dict_):
        fields = ["name", "distance"]
        for field in fields:
            if field not in dict_:
                raise KeyError(f"Missing field '{field}' from dict: {dict_}")
