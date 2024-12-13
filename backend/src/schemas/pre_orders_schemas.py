from marshmallow import Schema, fields

from src.schemas.employee_schemas import EmployeeBaseSchema
from src.models.maindish import MainDish


class PreOrderBaseSchema(Schema):
    id = fields.UUID(dump_only=True)
    date = fields.Date()
    nothing = fields.Boolean()
    main_dish = fields.Enum(MainDish)
    salad_option = fields.Boolean()


class PreOrderFullSchema(PreOrderBaseSchema):
    person_id = fields.UUID()
    location_id = fields.UUID()
    last_changed = fields.DateTime(format="timestamp")


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
