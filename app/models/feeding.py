class FeedingModel(object):
    def __init__(self, id, date, starter_name, jar_name, jar_distance):
        self.id = id
        self.date = date
        self.starter_name = starter_name
        self.jar_name = jar_name
        self.jar_distance = jar_distance

    @classmethod
    def from_dict(cls, dict_):
        cls.validate_dict(dict_)
        date_time = dict_["date"].split("T")
        time_zone = date_time[1].split(".")
        date = f"{date_time[0]} {time_zone[0]}"

        return FeedingModel(
            dict_["id"],
            date,
            dict_["starter_name"][0],
            dict_["jar_name"][0],
            dict_["jar_distance"][0],
        )

    @classmethod
    def validate_dict(self, dict_):
        fields = ["id", "date", "starter_name", "jar_name", "jar_distance"]
        for field in fields:
            if field not in dict_:
                raise KeyError(f"Missing field '{field}' from dict: {dict_}")
