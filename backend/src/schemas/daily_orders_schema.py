from flasgger import Schema, fields

from src.models.maindish import MainDish


class DailyOrderBaseSchema(Schema):
    """Schema representing data returned for every daily order"""

    id = fields.UUID(required=True, dump_only=True)
    date = fields.Date(required=True)
    nothing = fields.Boolean(required=True, dump_default=False)
    main_dish = fields.Enum(
        MainDish, required=False, dump_default=None, allow_none=True
    )
    salad_option = fields.Boolean(required=False, dump_default=False)
    handed_out = fields.Boolean(required=True, dump_default=False, allow_none=True)


class DailyOrderFullSchema(DailyOrderBaseSchema):
    """Schema representing a full daily order with flat structure"""

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
