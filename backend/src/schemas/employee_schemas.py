from flasgger import Schema, fields
from marshmallow.validate import Length


class EmployeeBaseSchema(Schema):
    """Employee Base Schema"""

    id = fields.UUID(required=True, dump_only=True)
    first_name = fields.String(required=True, validate=Length(min=1, max=64))
    last_name = fields.String(required=True, validate=Length(min=1, max=64))
    employee_number = fields.Integer(required=True)


class EmployeeFullSchema(EmployeeBaseSchema):
    """Employee Full Schema"""

    group_id = fields.UUID(required=True)
    created = fields.DateTime(required=True, format="timestamp", dump_only=True)


class EmployeeChangeSchema(EmployeeBaseSchema):
    """Employee Create Schema"""

    group_name = fields.String(
        required=True, validate=Length(min=1, max=64), load_only=True
    )
    location_name = fields.String(
        required=True, validate=Length(min=1, max=64), load_only=True
    )


class EmployeeFullNestedSchema(EmployeeBaseSchema):
    """Employee Full Nested Schema"""

    group = fields.Nested("GroupLocationNestedSchema", required=True, dump_only=True)
    created = fields.DateTime(required=True, format="timestamp", dump_only=True)
