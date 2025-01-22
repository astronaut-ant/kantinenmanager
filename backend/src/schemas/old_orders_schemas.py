from flasgger import Schema, fields
from uuid import UUID
from marshmallow.validate import Length

from src.models.maindish import MainDish


class OldOrderFilterSchema(Schema):
    """
    Schema for the GET /api/old-orders endpoint
    Uses ISO 8601-formatted date strings (YYYY-MM-DD)
    """

    person_id = fields.UUID(data_key="person-id", required=False)
    location_id = fields.UUID(data_key="location-id", required=False)
    group_id = fields.UUID(data_key="group-id", required=False)
    date = fields.Date(data_key="date", required=False)
    date_start = fields.Date(data_key="date-start", required=False)
    date_end = fields.Date(data_key="date-end", required=False)


class OldOrderBaseSchema(Schema):
    """Schema representing data returned for every old-order"""

    id = fields.UUID(required=True, dumb_only=True)
    date = fields.Date(required=True)
    nothing = fields.Boolean(required=True, default=False)
    main_dish = fields.Enum(MainDish, required=False, allow_none=True)
    salad_option = fields.Boolean(required=False)


class OldOrderFullSchema(OldOrderBaseSchema):
    """Schema representing a full old-order with flat structure"""

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    handed_out = fields.Boolean(required=True)
