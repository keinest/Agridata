"""Custom domain exceptions for AgriData."""


class AgrDataException(Exception):
    """Base exception for AgriData"""


class TenantNotFoundError(AgrDataException):
    """Tenant not found"""


class UserNotFoundError(AgrDataException):
    """User not found"""


class ExploitationNotFoundError(AgrDataException):
    """Exploitation not found"""


class UnauthorizedError(AgrDataException):
    """User not authorized"""


class InvalidCredentialsError(AgrDataException):
    """Invalid credentials"""


class DataValidationError(AgrDataException):
    """Data validation error"""


class MultiTenantViolationError(AgrDataException):
    """Multi-tenant isolation violation detected"""


class DataNotFoundError(AgrDataException):
    """Data not found"""
