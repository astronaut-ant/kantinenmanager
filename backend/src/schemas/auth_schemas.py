from flasgger import Schema, fields
from marshmallow.validate import Length


class AuthLoginSchema(Schema):
    """Schema to validate Login request body"""

    username = fields.Str(required=True, validate=Length(min=1, max=64))
    password = fields.Str(required=True, validate=Length(min=1, max=256))


class AuthPasswordChangeSchema(Schema):
    """Schema to validate Password Change request body"""

    old_password = fields.Str(required=True, validate=Length(min=1, max=256))
    new_password = fields.Str(required=True, validate=Length(min=8, max=256))
