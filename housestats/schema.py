from marshmallow import Schema, pre_load, validates_schema, validates, ValidationError
from marshmallow.fields import String, Integer, Boolean, List, Dict
from marshmallow.validate import Regexp


def numeric(v):
    '''Convert a string value into an appropriate numeric representation.'''
    if isinstance(v, (float, int)):
        return v
    else:
        return float(v) if '.' in v else int(v)


class MetricSchema(Schema):
    def __init__(self, tag_keys=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tag_keys = tag_keys if tag_keys else {}

    sensor_id = String(required=True)
    sensor_type = String(required=True)
    tags = Dict()
    fields = Dict(required=True)

    @validates('fields')
    def validate_fields(self, data):
        for k in data.keys():
            try:
                data[k] = numeric(data[k])
            except ValueError:
                raise ValidationError('Field values must be numeric')
