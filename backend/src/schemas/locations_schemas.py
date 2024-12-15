from flasgger import Schema, fields
from marshmallow.validate import Length


class LocationBaseSchema(Schema):
    """Schema representing data at the base level for a location"""

    id = fields.UUID(required=True, dump_only=True)
    location_name = fields.String(required=True, validate=Length(min=1, max=64))


class LocationFullSchema(LocationBaseSchema):
    """Schema representing a full location with flat structure"""

    user_id_location_leader = fields.UUID(required=True)


class LocationFullNestedSchema(LocationBaseSchema):
    """Schema representing a location with resolved nested fields"""

    location_leader = fields.Nested("UserBaseSchema", required=True, dump_only=True)
