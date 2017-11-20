import itertools
import math
import random

from housestats.metric import Metric
from housestats.sensor.base import BaseSensor


def sineiter():
    theta = math.radians(random.randint(0, 360))
    while True:
        yield math.sin(theta)
        theta += 0.1
        if theta >= (math.pi * 2):
            theta = 0


class ExampleSensor(BaseSensor):
    sensor_type = 'example'

    def __init__(self, config):
        super().__init__(config)
        self.sine = itertools.cycle(sineiter())

    def sample(self):
        return next(self.sine) * self.config.get('amplitude', 1)

    def fetch(self):
        return [Metric.load(dict(
            sensor_type=self.sensor_type,
            sensor_id=str(self.config.get('id', 0)),
            tags=self.config.get('tags', {}),
            fields=dict(value=self.sample(),
                        amplitude=self.config.get('amplitude', 1)),
        ))]
