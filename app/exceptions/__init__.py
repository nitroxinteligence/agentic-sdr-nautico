"""
Custom Exceptions for the SDR IA SolarPrime System
Centralized exception handling for better error management
"""


class BaseSDRException(Exception):
    """Base exception for all SDR IA SolarPrime exceptions"""
    def __init__(
            self, message: str, error_code: str = None, details: dict = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class KommoAPIException(BaseSDRException):
    """Exception raised for Kommo API errors"""
    pass


class GoogleCalendarException(BaseSDRException):
    """Exception raised for Google Calendar API errors"""
    pass


class NetworkException(BaseSDRException):
    """Exception raised for network connectivity issues"""
    pass


class DatabaseException(BaseSDRException):
    """Exception raised for database operation errors"""
    pass


class RateLimitException(BaseSDRException):
    """Exception raised when rate limits are exceeded"""
    pass


class AuthenticationException(BaseSDRException):
    """Exception raised for authentication failures"""
    pass


class ValidationException(BaseSDRException):
    """Exception raised for data validation errors"""
    pass


class HandoffException(BaseSDRException):
    """Exception raised for human handoff errors"""
    pass


class ConversationException(BaseSDRException):
    """Exception raised for conversation processing errors"""
    pass


class LLMResponseError(BaseSDRException):
    """Exception raised for errors in LLM response generation or parsing."""
    pass


class ToolExecutionError(BaseSDRException):
    """Exception raised when a tool fails to execute."""
    pass


class DataExtractionError(BaseSDRException):
    """Exception raised when data extraction from text fails."""
    pass


class HandoffActiveException(BaseSDRException):
    """Exception raised when an operation is attempted on a lead under human handoff."""
    pass
