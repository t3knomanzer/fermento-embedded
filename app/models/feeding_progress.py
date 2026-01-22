class FeedingProgressModel(object):
    def __init__(
        self, feeding, temperature, humidity, starting_distance, current_distance
    ):
        self.feeding = [feeding]
        self.temperature = temperature
        self.humidity = humidity
        self.starting_distance = starting_distance
        self.current_distance = current_distance

    def to_dict(self):
        return {
            "feeding": self.feeding,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "starting_distance": self.starting_distance,
            "current_distance": self.current_distance,
        }
