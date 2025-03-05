from abc import ABC
import enum
from typing import Literal

from src.logging import LoggingMethod


class Environment(enum.Enum):
    """Represents the environment in which the application is running."""

    PRODUCTION = "production"
    """Used in production environments"""

    DEVELOPMENT = "development"
    """Used for local development"""

    MIGRATION = "migration"
    """Used for database migrations"""

    TESTING = "testing"
    """Used for testing"""


class Features(ABC):
    """Base class for configuration classes"""

    DATABASE: Literal["real", "in-memory", "none"]
    """The database to use. Can be 'real', 'in-memory', or 'none'."""

    METRICS: bool
    """Whether to enable metrics endpoint /api/metrics"""

    TESTING_MODE: bool
    """Enable testing mode for Flask"""

    CORS: bool
    """Whether to enable CORS"""

    SWAGGER: bool
    """Whether to enable Swagger for API documentation"""

    INSERT_DEFAULT_DATA: bool
    """Whether to insert default data into the database (e.g. default admin user)"""

    INSERT_MOCK_DATA: bool
    """Whether to insert mock data into the database"""

    CRONJOBS: bool
    """Whether to enable cronjobs"""

    LOGGING: LoggingMethod
    """The logging method to use"""


class ProductionFeatures(Features):
    DATABASE = "real"
    METRICS = True
    TESTING_MODE = False
    CORS = False
    SWAGGER = False
    INSERT_DEFAULT_DATA = True
    INSERT_MOCK_DATA = False
    CRONJOBS = True
    LOGGING = LoggingMethod.LOKI


class DevelopmentFeatures(Features):
    DATABASE = "real"
    METRICS = True
    TESTING_MODE = False
    CORS = True
    SWAGGER = True
    INSERT_DEFAULT_DATA = True
    INSERT_MOCK_DATA = True
    CRONJOBS = True
    LOGGING = LoggingMethod.CONSOLE


class MigrationFeatures(Features):
    DATABASE = "real"
    METRICS = False
    TESTING_MODE = False
    CORS = False
    SWAGGER = False
    INSERT_DEFAULT_DATA = False
    INSERT_MOCK_DATA = False
    CRONJOBS = False
    LOGGING = LoggingMethod.CONSOLE


class TestingFeatures(Features):
    DATABASE = "in-memory"
    METRICS = False
    TESTING_MODE = True
    CORS = False
    SWAGGER = False
    INSERT_DEFAULT_DATA = False
    INSERT_MOCK_DATA = False
    CRONJOBS = False
    LOGGING = LoggingMethod.CONSOLE


def get_features(env: Environment) -> Features:
    """Get the features for the given environment."""
    if env == Environment.PRODUCTION:
        return ProductionFeatures
    elif env == Environment.DEVELOPMENT:
        return DevelopmentFeatures
    elif env == Environment.MIGRATION:
        return MigrationFeatures
    elif env == Environment.TESTING:
        return TestingFeatures
    else:
        raise ValueError(f"Unknown environment: {env}")
