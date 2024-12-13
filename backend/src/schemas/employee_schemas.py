from marshmallow import Schema, fields


class EmployeeBaseSchema(Schema):
    id = fields.UUID()
    first_name = fields.String()
    last_name = fields.String()
    employee_number = fields.Integer()
