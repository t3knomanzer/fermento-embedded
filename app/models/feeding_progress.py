class FeedingProgressModel(object):

    def __init__(
        self,
        feeding,
        temperature,
        humidity,
        co2,
        gas_resistance,
        starting_distance,
        current_distance,
    ):
        self.feeding = [feeding]
        self.temperature = temperature
        self.humidity = humidity
        self.co2 = co2
        self.gas_resistance = gas_resistance
        self.starting_distance = starting_distance
        self.current_distance = current_distance

    def to_dict(self):
        return {
            "feeding": self.feeding,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2": self.co2,
            "gas_resistance": self.gas_resistance,
            "starting_distance": self.starting_distance,
            "current_distance": self.current_distance,
        }
