import enum


class MainDish(enum.Enum):
    """Enum to represent the two different main dishes in the application"""

    # The values need to be lowercase for validation to work
    rot = "rot"
    blau = "blau"
