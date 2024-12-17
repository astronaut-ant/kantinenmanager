from flasgger import Schema, fields
from uuid import UUID

from src.models.maindish import MainDish


class DailyOrderBaseSchema(Schema):
    """Schema representing data returned for every daily order"""

    id = fields.UUID(required=True, dump_only=True)
    date = fields.Date(required=True)
    nothing = fields.Boolean(required=True, default=False)
    main_dish = fields.Enum(MainDish, required=False, default=None, allow_none=True)
    salad_option = fields.Boolean(required=False, default=False)
    handed_out = fields.Boolean(required=True, default=False, allow_none=True)


class DailyOrderFullSchema(DailyOrderBaseSchema):
    """Schema representing a full daily order with flat structure"""

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)


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
