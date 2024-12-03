"""This module contains the Environment enum."""

import enum


class Environment(enum.Enum):
    """Represents the environment in which the application is running."""

    DEVELOPMENT = "development"
    MIGRATION = "migration"
    PRODUCTION = "production"
