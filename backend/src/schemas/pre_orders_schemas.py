from flasgger import Schema, fields  # this is a wrapper for marshmallow schemas

from src.schemas.employee_schemas import EmployeeBaseSchema
from src.models.maindish import MainDish


class OrdersFilterSchema(Schema):
    """
    Query parameters for filtering orders

    Uses ISO 8601 date format for dates (YYYY-MM-DD).
    """

    person_id = fields.UUID(data_key="person-id", required=False)
    location_id = fields.UUID(data_key="location-id", required=False)
    group_id = fields.UUID(data_key="group-id", required=False)
    date = fields.Date(data_key="date", required=False)
    date_start = fields.Date(data_key="date-start", required=False)
    date_end = fields.Date(data_key="date-end", required=False)


class PreOrderBaseSchema(Schema):
    """Schema representing data returned for every pre-order"""

    id = fields.UUID(required=True, dump_only=True)
    date = fields.Date(required=True)
    nothing = fields.Boolean(required=True, default=False)
    main_dish = fields.Enum(MainDish, required=False, default=None, allow_none=True)
    salad_option = fields.Boolean(required=False, default=False)


class PreOrderFullSchema(PreOrderBaseSchema):
    """Schema representing a full order with flat structure"""

    person_id = fields.UUID(required=True)
    location_id = fields.UUID(required=True)
    last_changed = fields.DateTime(format="timestamp", dump_only=True)


class PreOrdersByGroupLeaderGroupSchema(Schema):
    id = fields.UUID(dump_only=True)
    group_name = fields.String()
    is_home_group = fields.Boolean()
    employees = fields.List(fields.Nested(EmployeeBaseSchema))
    orders = fields.List(fields.Nested(PreOrderFullSchema))


class PreOrdersByGroupLeaderSchema(Schema):
    id = fields.UUID()
    username = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    groups = fields.List(
        fields.Nested(PreOrdersByGroupLeaderGroupSchema), dump_only=True
    )
