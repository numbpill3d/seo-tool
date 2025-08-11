"""
Logging configuration for SEO Analyzer
"""

import logging
import logging.handlers
import os
from datetime import datetime
import config


def setup_logging():
    """Setup logging configuration for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOGGING_CONFIG['level']))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # Main application log file
    main_log_file = os.path.join(log_dir, config.LOGGING_CONFIG['file'])
    file_handler = logging.handlers.RotatingFileHandler(
        main_log_file,
        maxBytes=config.LOGGING_CONFIG['max_size'],
        backupCount=config.LOGGING_CONFIG['backup_count'],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Scraping activity log
    scraping_log_file = os.path.join(log_dir, "scraping.log")
    scraping_handler = logging.handlers.RotatingFileHandler(
        scraping_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    scraping_handler.setLevel(logging.INFO)
    scraping_handler.setFormatter(detailed_formatter)
    
    # Add scraping handler to scraper logger
    scraper_logger = logging.getLogger('scraper')
    scraper_logger.addHandler(scraping_handler)
    
    # Performance log
    performance_log_file = os.path.join(log_dir, "performance.log")
    performance_handler = logging.handlers.RotatingFileHandler(
        performance_log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(detailed_formatter)
    
    # Add performance handler to specific loggers
    performance_logger = logging.getLogger('performance')
    performance_logger.addHandler(performance_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('nltk').setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log level: {config.LOGGING_CONFIG['level']}")
    root_logger.info(f"Log directory: {log_dir}")


def get_performance_logger():
    """Get performance logger for timing operations"""
    return logging.getLogger('performance')


class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.logger = get_performance_logger()
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed operation: {self.operation_name} in {duration:.2f} seconds")
        else:
            self.logger.error(f"Failed operation: {self.operation_name} after {duration:.2f} seconds - {exc_val}")