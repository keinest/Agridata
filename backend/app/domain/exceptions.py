"""Custom domain exceptions"""


class AgrDataException(Exception):
    """Base exception for AgriData"""
    pass


class TenantNotFoundError(AgrDataException):
    """Tenant not found"""
    pass


class UserNotFoundError(AgrDataException):
    """User not found"""
    pass


class ExploitationNotFoundError(AgrDataException):
    """Exploitation not found"""
    pass


class UnauthorizedError(AgrDataException):
    """User not authorized"""
    pass


class InvalidCredentialsError(AgrDataException):
    """Invalid credentials"""
    pass


class DataValidationError(AgrDataException):
    """Data validation error"""
    pass


class MultiTenantViolationError(AgrDataException):
    """Multi-tenant isolation violation detected"""
    pass


class DataNotFoundError(AgrDataException):
    """Data not found"""
    pass
