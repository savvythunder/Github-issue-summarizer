"""
Configuration settings for GitHub Issue Summarizer.
"""

import os
from typing import Dict, Any, Optional

class Config:
    """Base configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # GitHub API configuration
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GITHUB_API_BASE_URL = 'https://api.github.com'
    GITHUB_REQUEST_TIMEOUT = int(os.environ.get('GITHUB_REQUEST_TIMEOUT', '30'))
    
    # AI Model configuration
    HUGGINGFACE_MODEL = os.environ.get('HUGGINGFACE_MODEL', 'facebook/bart-large-cnn')
    MAX_SUMMARY_LENGTH = int(os.environ.get('MAX_SUMMARY_LENGTH', '150'))
    MIN_SUMMARY_LENGTH = int(os.environ.get('MIN_SUMMARY_LENGTH', '30'))
    AI_BATCH_SIZE = int(os.environ.get('AI_BATCH_SIZE', '5'))
    
    # Caching configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', '1800'))  # 30 minutes
    CACHE_KEY_PREFIX = os.environ.get('CACHE_KEY_PREFIX', 'github_summarizer_')
    
    # Redis configuration (if using Redis cache)
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    CACHE_REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))
    CACHE_REDIS_DB = int(os.environ.get('REDIS_DB', '0'))
    CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # Application limits
    MAX_ISSUES_PER_REQUEST = int(os.environ.get('MAX_ISSUES_PER_REQUEST', '100'))
    MAX_PAGES_PER_REQUEST = int(os.environ.get('MAX_PAGES_PER_REQUEST', '1000'))
    REQUEST_TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT', '300'))  # 5 minutes
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Rate limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'False').lower() == 'true'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """
        Get cache configuration based on environment.
        
        Returns:
            Dictionary of cache configuration
        """
        if cls.CACHE_TYPE.lower() == 'redis':
            return {
                'CACHE_TYPE': 'redis',
                'CACHE_REDIS_URL': cls.CACHE_REDIS_URL,
                'CACHE_DEFAULT_TIMEOUT': cls.CACHE_DEFAULT_TIMEOUT,
                'CACHE_KEY_PREFIX': cls.CACHE_KEY_PREFIX
            }
        elif cls.CACHE_TYPE.lower() == 'filesystem':
            return {
                'CACHE_TYPE': 'filesystem',
                'CACHE_DIR': os.environ.get('CACHE_DIR', '/tmp/flask_cache'),
                'CACHE_DEFAULT_TIMEOUT': cls.CACHE_DEFAULT_TIMEOUT,
                'CACHE_KEY_PREFIX': cls.CACHE_KEY_PREFIX
            }
        else:
            # Simple in-memory cache (default)
            return {
                'CACHE_TYPE': 'simple',
                'CACHE_DEFAULT_TIMEOUT': cls.CACHE_DEFAULT_TIMEOUT
            }
    
    @classmethod
    def validate_config(cls) -> Dict[str, str]:
        """
        Validate configuration and return any warnings or errors.
        
        Returns:
            Dictionary of configuration issues
        """
        issues = {}
        
        # Check if GitHub token is provided
        if not cls.GITHUB_TOKEN:
            issues['github_token'] = 'No GitHub token provided. API rate limits will be lower.'
        
        # Validate model name
        if not cls.HUGGINGFACE_MODEL:
            issues['ai_model'] = 'No AI model specified. Using default model.'
        
        # Check summary length settings
        if cls.MAX_SUMMARY_LENGTH <= cls.MIN_SUMMARY_LENGTH:
            issues['summary_length'] = 'Max summary length must be greater than min summary length.'
        
        # Validate cache settings
        if cls.CACHE_TYPE.lower() == 'redis':
            try:
                import redis
                # Try to connect to Redis
                r = redis.from_url(cls.CACHE_REDIS_URL)
                r.ping()
            except ImportError:
                issues['redis'] = 'Redis cache selected but redis library not available.'
            except Exception:
                issues['redis'] = 'Cannot connect to Redis server.'
        
        return issues

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    CACHE_TYPE = 'simple'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'redis')
    RATELIMIT_ENABLED = True
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    CACHE_TYPE = 'simple'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration based on environment.
    
    Args:
        config_name: Configuration name or None for auto-detection
        
    Returns:
        Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_map.get(config_name or 'development', DevelopmentConfig)
