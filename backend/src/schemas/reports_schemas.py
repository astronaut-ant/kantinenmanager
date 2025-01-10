from flasgger import Schema, fields
from uuid import UUID


class CountOrdersObject:
    def __init__(self, location_id: UUID, rot: int, blau: int, salad_option: int):
        self.location_id = location_id
        self.rot = rot
        self.blau = blau
        self.salad_option = salad_option


class CountOrdersSchema(Schema):
    location_id = fields.UUID(required=True)
    rot = fields.Integer(required=True)
    blau = fields.Integer(required=True)
    salad_option = fields.Integer(required=True)
