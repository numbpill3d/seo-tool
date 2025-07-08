"""
Configuration settings for SEO Rank & Content Gap Analyzer
Contains all constants, settings, and configuration parameters
"""

import os
from typing import List, Dict

# Application Information
APP_NAME = "SEO Rank & Content Gap Analyzer Pro"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Your Company Name"
APP_DESCRIPTION = "Professional tool for SEO content gap analysis and competitor keyword research"

# File and Directory Settings
DEFAULT_OUTPUT_DIR = "seo_reports"
DEFAULT_SESSION_DIR = "sessions"
DEFAULT_HISTORY_DIR = "history"
TEMP_DIR = "temp"

# Create directories if they don't exist
def create_required_directories():
    """Create required application directories with proper error handling"""
    required_dirs = [DEFAULT_OUTPUT_DIR, DEFAULT_SESSION_DIR, DEFAULT_HISTORY_DIR, TEMP_DIR]
    
    for directory in required_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            # Test write permissions by creating a test file
            test_file = os.path.join(directory, '.test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except (IOError, OSError) as e:
                print(f"Warning: Directory '{directory}' exists but is not writable: {str(e)}")
                # Try to create in user's home directory instead
                user_dir = os.path.expanduser(f"~/.seo_analyzer/{directory}")
                os.makedirs(user_dir, exist_ok=True)
                globals()[directory.upper()] = user_dir  # Update the global variable
        except Exception as e:
            print(f"Error creating directory '{directory}': {str(e)}")
            # Fall back to temporary directory
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), 'seo_analyzer', directory)
            os.makedirs(temp_dir, exist_ok=True)
            globals()[directory.upper()] = temp_dir  # Update the global variable

# Create directories with error handling
create_required_directories()

# Scraping Configuration
REQUEST_DELAY = 2.0  # Seconds between requests
REQUEST_TIMEOUT = 30  # Request timeout in seconds
MAX_RETRIES = 3  # Maximum number of retry attempts
RETRY_DELAY = 5  # Delay between retries in seconds

# User Agent Rotation for Web Scraping
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
]

# Text Processing Configuration
MIN_KEYWORD_LENGTH = 2
MAX_KEYWORD_LENGTH = 50
MIN_PHRASE_WORDS = 2
MAX_PHRASE_WORDS = 5
DEFAULT_MIN_FREQUENCY = 2

# Custom stopwords for SEO analysis (in addition to NLTK stopwords)
CUSTOM_STOPWORDS = {
    # Navigation and UI elements
    'home', 'about', 'contact', 'blog', 'news', 'search', 'menu', 'login', 'register',
    'subscribe', 'follow', 'share', 'like', 'comment', 'reply', 'click', 'here',
    'read', 'more', 'continue', 'next', 'previous', 'back', 'forward',
    
    # Common web elements
    'page', 'site', 'website', 'link', 'url', 'http', 'https', 'www', 'com', 'org',
    'net', 'email', 'mail', 'phone', 'address', 'location', 'map',
    
    # Generic business terms
    'company', 'business', 'service', 'services', 'product', 'products', 'solution',
    'solutions', 'team', 'staff', 'member', 'members', 'customer', 'customers',
    'client', 'clients', 'user', 'users',
    
    # Time and date
    'today', 'yesterday', 'tomorrow', 'week', 'month', 'year', 'time', 'date',
    'schedule', 'appointment', 'calendar',
    
    # Common adjectives that don't add SEO value
    'good', 'bad', 'great', 'best', 'better', 'worse', 'worst', 'nice', 'beautiful',
    'ugly', 'big', 'small', 'large', 'huge', 'tiny', 'new', 'old', 'fresh',
    
    # Generic verbs
    'do', 'does', 'did', 'done', 'doing', 'make', 'makes', 'made', 'making',
    'get', 'gets', 'got', 'getting', 'give', 'gives', 'gave', 'giving',
    'take', 'takes', 'took', 'taking', 'put', 'puts', 'putting'
}

# Content Gap Analysis Configuration
OPPORTUNITY_SCORE_WEIGHTS = {
    'frequency': 0.3,          # Weight for competitor frequency
    'document_frequency': 0.25, # Weight for number of sites using keyword
    'importance': 0.2,         # Weight for average importance score
    'length': 0.1,             # Weight for keyword length
    'relevance': 0.15          # Weight for content relevance
}

# Priority Classification Thresholds
PRIORITY_THRESHOLDS = {
    'high': 75,    # Opportunity score >= 75
    'medium': 50,  # Opportunity score >= 50 and < 75
    'low': 25      # Opportunity score >= 25 and < 50
}

# Export Configuration
DEFAULT_EXPORT_FORMATS = ['csv', 'json']
PDF_EXPORT_ENABLED = True
MAX_KEYWORDS_IN_PDF = 50
MAX_COMPETITORS_IN_REPORT = 25

# GUI Configuration
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 800

# Theme and Colors
APP_COLORS = {
    'primary': '#2196F3',      # Blue
    'secondary': '#4CAF50',    # Green
    'accent': '#FF9800',       # Orange
    'danger': '#F44336',       # Red
    'warning': '#FFC107',      # Amber
    'success': '#4CAF50',      # Green
    'info': '#2196F3',         # Blue
    'light': '#F8F9FA',        # Light gray
    'dark': '#343A40'          # Dark gray
}

# Analysis Limits (for performance and rate limiting)
MAX_SEARCH_RESULTS = 20
MAX_CONTENT_LENGTH = 100000  # Maximum characters per webpage
MAX_CONCURRENT_REQUESTS = 3
MAX_ANALYSIS_KEYWORDS = 1000

# Caching Configuration
ENABLE_CACHING = True
CACHE_DURATION_HOURS = 24
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# API Configuration (for future premium features)
API_RATE_LIMITS = {
    'free_tier': {
        'daily_searches': 10,
        'monthly_searches': 100,
        'max_keywords_per_search': 500
    },
    'pro_tier': {
        'daily_searches': 100,
        'monthly_searches': 2000,
        'max_keywords_per_search': 2000
    },
    'enterprise_tier': {
        'daily_searches': 1000,
        'monthly_searches': 20000,
        'max_keywords_per_search': 10000
    }
}

# SerpAPI Configuration (optional)
SERPAPI_CONFIG = {
    'enabled': False,
    'api_key': os.getenv('SERPAPI_KEY', ''),
    'engine': 'google',
    'num_results': 10,
    'location': 'United States'
}

# SEMrush API Configuration (optional)
SEMRUSH_CONFIG = {
    'enabled': False,
    'api_key': os.getenv('SEMRUSH_KEY', ''),
    'database': 'us',
    'export_columns': 'Ph,Po,Pp,Pd,Nq,Cp,Ur,Tr,Tc,Co,Nr,Td'
}

# Ahrefs API Configuration (optional)
AHREFS_CONFIG = {
    'enabled': False,
    'api_key': os.getenv('AHREFS_KEY', ''),
    'mode': 'domain',
    'limit': 1000
}

# Database Configuration (for future multi-user features)
DATABASE_CONFIG = {
    'enabled': False,
    'type': 'sqlite',  # 'sqlite', 'postgresql', 'mysql'
    'filename': 'seo_analyzer.db',
    'host': 'localhost',
    'port': 5432,
    'database': 'seo_analyzer',
    'username': '',
    'password': ''
}

# Email Configuration (for reports)
EMAIL_CONFIG = {
    'enabled': False,
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'username': os.getenv('EMAIL_USERNAME', ''),
    'password': os.getenv('EMAIL_PASSWORD', ''),
    'use_tls': True
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'seo_analyzer.log',
    'max_size': 10485760,  # 10MB
    'backup_count': 5
}

# Advanced Features Configuration
ADVANCED_FEATURES = {
    'named_entity_recognition': True,
    'sentiment_analysis': False,
    'topic_modeling': False,
    'competitor_monitoring': False,
    'automated_reporting': False,
    'multi_language_support': False
}

# Keyword Classification Configuration
KEYWORD_CLASSIFICATION = {
    'commercial_indicators': {
        'buy', 'purchase', 'order', 'shop', 'sale', 'deal', 'discount',
        'cheap', 'best', 'top', 'review', 'compare', 'vs', 'versus',
        'price', 'cost', 'pricing', 'affordable', 'budget'
    },
    'informational_indicators': {
        'how', 'what', 'why', 'when', 'where', 'guide', 'tutorial',
        'tips', 'learn', 'understand', 'explain', 'definition',
        'meaning', 'example', 'examples', 'step', 'steps'
    },
    'local_indicators': {
        'near', 'local', 'nearby', 'around', 'close', 'in', 'at',
        'location', 'address', 'directions', 'map', 'area'
    },
    'transactional_indicators': {
        'buy', 'purchase', 'order', 'book', 'hire', 'contact',
        'quote', 'estimate', 'signup', 'register', 'subscribe',
        'download', 'install', 'get', 'start'
    }
}

# Content Strategy Templates
CONTENT_STRATEGY_TEMPLATES = {
    'informational': {
        'content_types': ['blog_post', 'guide', 'tutorial', 'faq'],
        'recommended_length': '1500-3000 words',
        'focus': 'educational value and comprehensive coverage'
    },
    'commercial': {
        'content_types': ['product_page', 'comparison', 'review', 'landing_page'],
        'recommended_length': '800-1500 words',
        'focus': 'conversion optimization and trust building'
    },
    'local': {
        'content_types': ['location_page', 'local_guide', 'service_area'],
        'recommended_length': '500-1200 words',
        'focus': 'local relevance and geographic targeting'
    },
    'transactional': {
        'content_types': ['landing_page', 'product_page', 'checkout_flow'],
        'recommended_length': '300-800 words',
        'focus': 'clear call-to-action and conversion elements'
    }
}

# Performance Monitoring
PERFORMANCE_METRICS = {
    'track_analysis_time': True,
    'track_scraping_success_rate': True,
    'track_keyword_discovery_rate': True,
    'track_export_usage': True,
    'track_user_engagement': True
}

# Security Configuration
SECURITY_CONFIG = {
    'max_file_size': 10485760,  # 10MB max upload
    'allowed_file_types': ['.txt', '.html', '.htm', '.csv'],
    'sanitize_inputs': True,
    'rate_limit_enabled': True,
    'max_requests_per_minute': 30
}

# Monetization Configuration (for SaaS features)
MONETIZATION_CONFIG = {
    'stripe_enabled': False,
    'stripe_public_key': os.getenv('STRIPE_PUBLIC_KEY', ''),
    'stripe_secret_key': os.getenv('STRIPE_SECRET_KEY', ''),
    'pricing_tiers': {
        'free': {
            'price': 0,
            'monthly_analyses': 5,
            'max_keywords': 100,
            'export_formats': ['csv']
        },
        'pro': {
            'price': 29,
            'monthly_analyses': 100,
            'max_keywords': 2000,
            'export_formats': ['csv', 'json', 'pdf'],
            'api_access': True
        },
        'enterprise': {
            'price': 99,
            'monthly_analyses': 1000,
            'max_keywords': 10000,
            'export_formats': ['csv', 'json', 'pdf'],
            'api_access': True,
            'white_label': True,
            'priority_support': True
        }
    }
}

# Feature Flags (for A/B testing and gradual rollouts)
FEATURE_FLAGS = {
    'ai_keyword_suggestions': False,
    'real_time_competitor_monitoring': False,
    'advanced_nlp_analysis': False,
    'automated_content_generation': False,
    'multi_tenant_support': False,
    'api_rate_limiting': True,
    'advanced_export_options': True
}

# Default Settings for New Users
DEFAULT_USER_SETTINGS = {
    'min_keyword_frequency': 2,
    'exclude_common_words': True,
    'max_results_to_analyze': 10,
    'preferred_export_format': 'csv',
    'auto_save_sessions': True,
    'show_advanced_options': False,
    'enable_notifications': True,
    'dark_mode': False
}

# Validation Rules
VALIDATION_RULES = {
    'keyword_min_length': 1,
    'keyword_max_length': 100,
    'location_max_length': 100,
    'url_max_length': 2000,
    'content_max_length': 100000,
    'custom_stopwords_max': 100
}

def get_config_value(key: str, default=None):
    """
    Get configuration value with optional default
    
    Args:
        key: Configuration key in dot notation (e.g., 'database.host')
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    try:
        # Split key by dots and traverse the config
        current = globals()
        for part in key.split('.'):
            current = current[part]
        return current
    except (KeyError, TypeError):
        return default

def update_config_value(key: str, value):
    """
    Update configuration value
    
    Args:
        key: Configuration key in dot notation
        value: New value to set
    """
    try:
        # This is a simplified implementation
        # In production, you might want more sophisticated config management
        parts = key.split('.')
        if len(parts) == 1:
            globals()[parts[0]] = value
        # For nested configs, you'd need more complex logic
    except Exception as e:
        print(f"Error updating config value {key}: {e}")

def validate_config():
    """
    Validate current configuration settings
    
    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        # Check required directories exist
        for directory in [DEFAULT_OUTPUT_DIR, DEFAULT_SESSION_DIR, CACHE_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                
        # Validate numeric settings
        assert REQUEST_DELAY >= 0, "REQUEST_DELAY must be non-negative"
        assert REQUEST_TIMEOUT > 0, "REQUEST_TIMEOUT must be positive"
        assert MAX_RETRIES >= 0, "MAX_RETRIES must be non-negative"
        
        # Validate user agents list
        assert len(USER_AGENTS) > 0, "USER_AGENTS list cannot be empty"
        
        return True
        
    except Exception as e:
        print(f"Configuration validation error: {e}")
        return False

# Initialize configuration validation
if __name__ == "__main__":
    if validate_config():
        print("Configuration validation passed")
    else:
        print("Configuration validation failed")