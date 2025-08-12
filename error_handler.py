"""
Comprehensive error handling system for SEO Analyzer
Provides structured error handling, logging, and user-friendly error messages
"""

import logging
import traceback
import sys
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
from functools import wraps
import json


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    PROCESSING = "processing"
    VALIDATION = "validation"
    DEPENDENCY = "dependency"
    GUI = "gui"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    technical_details: str
    user_message: str
    suggested_actions: list
    error_code: str = ""
    context: dict = None


class ErrorHandler:
    """
    Centralized error handling with logging, user notifications, and recovery suggestions
    """
    
    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self.error_definitions = self._define_error_mappings()
    
    def _define_error_mappings(self) -> Dict[type, ErrorInfo]:
        """Define mappings from exception types to structured error information"""
        return {
            # Network errors
            ConnectionError: ErrorInfo(
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.HIGH,
                message="Network connection failed",
                technical_details="Unable to establish network connection",
                user_message="Cannot connect to the internet. Please check your network connection and try again.",
                suggested_actions=[
                    "Check your internet connection",
                    "Try again in a few moments",
                    "Check if any firewall is blocking the connection"
                ],
                error_code="NET_001"
            ),
            
            # File system errors
            FileNotFoundError: ErrorInfo(
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                message="File not found",
                technical_details="Specified file does not exist",
                user_message="The specified file could not be found. Please check the file path and try again.",
                suggested_actions=[
                    "Verify the file path is correct",
                    "Check if the file exists",
                    "Ensure you have proper file permissions"
                ],
                error_code="FILE_001"
            ),
            
            PermissionError: ErrorInfo(
                category=ErrorCategory.FILE_SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                message="Permission denied",
                technical_details="Insufficient permissions for file operation",
                user_message="Permission denied. You don't have the required permissions for this operation.",
                suggested_actions=[
                    "Run the application as administrator",
                    "Check file and folder permissions",
                    "Choose a different location with write access"
                ],
                error_code="FILE_002"
            ),
            
            # Processing errors
            ValueError: ErrorInfo(
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.MEDIUM,
                message="Invalid value",
                technical_details="Invalid or unexpected value provided",
                user_message="Invalid input provided. Please check your input and try again.",
                suggested_actions=[
                    "Verify the input format",
                    "Check for special characters",
                    "Ensure all required fields are filled"
                ],
                error_code="PROC_001"
            ),
            
            KeyError: ErrorInfo(
                category=ErrorCategory.PROCESSING,
                severity=ErrorSeverity.LOW,
                message="Missing data key",
                technical_details="Expected data key not found",
                user_message="Some expected data is missing. The analysis may be incomplete.",
                suggested_actions=[
                    "Try the analysis again",
                    "Check if the data source is complete",
                    "Contact support if the issue persists"
                ],
                error_code="PROC_002"
            ),
            
            # Import errors
            ImportError: ErrorInfo(
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.HIGH,
                message="Missing dependency",
                technical_details="Required module not available",
                user_message="A required component is missing. Some features may not be available.",
                suggested_actions=[
                    "Install missing dependencies",
                    "Run the dependency check",
                    "Reinstall the application"
                ],
                error_code="DEP_001"
            ),
        }
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
        """
        Handle an error with comprehensive logging and structured information
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            ErrorInfo object with structured error details
        """
        error_type = type(error)
        error_info = self.error_definitions.get(error_type)
        
        if not error_info:
            error_info = ErrorInfo(
                category=ErrorCategory.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                message="Unexpected error",
                technical_details=str(error),
                user_message="An unexpected error occurred. Please try again.",
                suggested_actions=[
                    "Try the operation again",
                    "Restart the application",
                    "Contact support if the issue persists"
                ],
                error_code="UNK_001"
            )
        
        # Add context information
        if context:
            error_info.context = context
        
        # Log the error
        self._log_error(error, error_info)
        
        return error_info
    
    def _log_error(self, error: Exception, error_info: ErrorInfo):
        """Log error with appropriate level and details"""
        log_message = f"[{error_info.error_code}] {error_info.message}: {str(error)}"
        
        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message, exc_info=True)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message, exc_info=True)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def create_error_report(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a comprehensive error report for debugging"""
        error_info = self.handle_error(error, context)
        
        return {
            'error_code': error_info.error_code,
            'category': error_info.category.value,
            'severity': error_info.severity.value,
            'message': error_info.message,
            'technical_details': error_info.technical_details,
            'user_message': error_info.user_message,
            'suggested_actions': error_info.suggested_actions,
            'context': error_info.context or {},
            'traceback': traceback.format_exc(),
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform
            }
        }


def handle_exceptions(category: ErrorCategory = ErrorCategory.UNKNOWN, 
                     severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                     user_message: str = None,
                     return_value: Any = None):
    """
    Decorator for comprehensive error handling
    
    Args:
        category: Error category
        severity: Error severity level
        user_message: Custom user-friendly message
        return_value: Value to return on error
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler(func.__module__)
                error_info = handler.handle_error(e, {
                    'function': func.__name__,
                    'args': str(args)[:200],  # Limit length
                    'kwargs': str(kwargs)[:200]
                })
                
                # Override user message if provided
                if user_message:
                    error_info.user_message = user_message
                
                # Log and potentially re-raise or return default
                if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
                    raise e
                
                return return_value
        return wrapper
    return decorator


class NetworkErrorHandler(ErrorHandler):
    """Specialized error handler for network operations"""
    
    def __init__(self):
        super().__init__("network")
        self.retry_config = {
            'max_retries': 3,
            'backoff_factor': 1.5,
            'max_backoff': 60
        }
    
    def handle_network_error(self, error: Exception, url: str = None, retry_count: int = 0) -> ErrorInfo:
        """Handle network-specific errors with retry logic"""
        context = {
            'url': url,
            'retry_count': retry_count,
            'max_retries': self.retry_config['max_retries']
        }
        
        error_info = self.handle_error(error, context)
        
        # Add specific network error handling
        if 'timeout' in str(error).lower():
            error_info.user_message = "Request timed out. The server may be busy or unreachable."
            error_info.suggested_actions.extend([
                "Check if the website is accessible in your browser",
                "Wait a few minutes and try again",
                "Try a different network if possible"
            ])
        elif 'connection refused' in str(error).lower():
            error_info.user_message = "Connection was refused. The server may be down."
            error_info.suggested_actions.extend([
                "Verify the URL is correct",
                "Check if the website is online",
                "Try again later"
            ])
        
        return error_info


class FileErrorHandler(ErrorHandler):
    """Specialized error handler for file operations"""
    
    def __init__(self):
        super().__init__("file")
    
    def handle_file_error(self, error: Exception, file_path: str = None, operation: str = "access") -> ErrorInfo:
        """Handle file-specific errors"""
        context = {
            'file_path': file_path,
            'operation': operation
        }
        
        error_info = self.handle_error(error, context)
        
        # Add file-specific guidance
        if isinstance(error, FileNotFoundError):
            error_info.suggested_actions.extend([
                f"Create the directory: {'/'.join(file_path.split('/')[:-1]) if file_path else 'required directory'}",
                "Check file path spelling and format"
            ])
        elif isinstance(error, PermissionError):
            error_info.suggested_actions.extend([
                "Close any programs using the file",
                "Run as administrator if necessary",
                f"Check permissions for: {file_path or 'the file'}"
            ])
        
        return error_info


# Global error handler instances
global_error_handler = ErrorHandler()
network_error_handler = NetworkErrorHandler()
file_error_handler = FileErrorHandler()


# Convenience functions
def handle_error(error: Exception, context: Dict[str, Any] = None) -> ErrorInfo:
    """Global error handling function"""
    return global_error_handler.handle_error(error, context)


def create_error_report(error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create error report function"""
    return global_error_handler.create_error_report(error, context)


def log_error(message: str, error: Exception = None, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Simple error logging function"""
    logger = logging.getLogger(__name__)
    
    if severity == ErrorSeverity.CRITICAL:
        logger.critical(message, exc_info=error)
    elif severity == ErrorSeverity.HIGH:
        logger.error(message, exc_info=error)
    elif severity == ErrorSeverity.MEDIUM:
        logger.warning(message)
    else:
        logger.info(message)