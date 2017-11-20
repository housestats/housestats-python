import json

from housestats.schema import MetricSchema


class Metric():
    schema = MetricSchema(strict=True)

    def __init__(self, sensor_id=None,
                 sensor_type=None, tags=None, fields=None):

        self.sensor_type = sensor_type
        self.sensor_id = sensor_id
        self.tags = tags if tags else {}
        self.fields = fields if fields else {}

    def add_field(self, name, value):
        self.fields[name] = value

    def update_fields(self, fields):
        self.fields.update(fields)

    def add_tag(self, name, value):
        self.tags[name] = value

    def update_tags(self, tags):
        self.tags.update(tags)

    @classmethod
    def from_dict(cls, data):
        valid, errors = cls.schema.load(data)
        return cls(**valid)

    load = from_dict

    def to_dict(self):
        return self.schema.dump(self)[0]

    def to_json(self, **kwargs):
        return json.dumps(self.to_dict(), **kwargs)
