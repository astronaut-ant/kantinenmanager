from flasgger import Schema, fields


class DishPriceBaseSchema(Schema):
    """Schema representing data returned for every dish price"""

    date = fields.Date(required=True)
    main_dish_price = fields.Float(required=True)
    salad_price = fields.Float(required=True)


class DishPriceFullSchema(DishPriceBaseSchema):
    """Schema representing a full dish price with flat structure"""

    pass
