from flasgger import Schema, fields
from marshmallow.validate import Length


class GroupBaseSchema(Schema):
    """Schema representing data at the base level for a group"""

    id = fields.UUID(required=True, dump_only=True)
    group_name = fields.String(required=True, validate=Length(min=1, max=64))


class GroupFullSchema(GroupBaseSchema):
    """Schema representing a full group with flat structure"""

    user_id_group_leader = fields.UUID(required=True)
    user_id_replacement = fields.UUID(required=False)
    location_id = fields.UUID(required=True)


class GroupFullNestedSchema(GroupBaseSchema):
    """Schema representing a group with resolved nested fields"""

    group_leader = fields.Nested("UserFullSchema", required=True, dump_only=True)
    group_leader_replacement = fields.Nested(
        "UserFullSchema", required=False, dump_only=True
    )
    location = fields.Nested("LocationFullSchema", required=True, dump_only=True)


class GroupLocationNestedSchema(GroupBaseSchema):
    """Schema representing a group with resolved nested location field"""

    user_id_group_leader = fields.UUID(required=True)
    user_id_replacement = fields.UUID(required=False)
    location = fields.Nested("LocationFullSchema", required=True, dump_only=True)
