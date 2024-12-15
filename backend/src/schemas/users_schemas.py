from flasgger import Schema, fields
from marshmallow.validate import Length

from src.models.user import UserGroup


class UserBaseSchema(Schema):
    """Schema representing data at the base level for a user"""

    id = fields.UUID(required=True, dump_only=True)
    first_name = fields.String(required=True, validate=Length(min=1, max=64))
    last_name = fields.String(required=True, validate=Length(min=1, max=64))
    username = fields.String(required=True, validate=Length(min=1, max=64))
    user_group = fields.Enum(UserGroup, required=True)


class UserFullSchema(UserBaseSchema):
    """Schema representing a full user with flat structure"""

    location_id = fields.UUID(required=False)
    created = fields.DateTime(format="timestamp", required=True, dump_only=True)
    last_login = fields.DateTime(format="timestamp", required=True, dump_only=True)
    blocked = fields.Boolean(required=True, dump_only=True)


class GroupLeaderNestedSchema(UserBaseSchema):
    """Schema representing a group leader with resolved nested fields"""

    own_group = fields.Nested(
        "GroupFullSchema", required=False, dump_only=True, attribute="leader_of_group"
    )
    replacement_groups = fields.List(
        fields.Nested("GroupFullSchema"),
        required=False,
        dump_only=True,
        attribute="replacement_leader_of_groups",
    )


class LocationLeaderNestedSchema(UserBaseSchema):
    """Schema representing a location leader with resolved nested fields"""

    leader_of_location = fields.Nested(
        "LocationBaseSchema", required=False, dump_only=True
    )
