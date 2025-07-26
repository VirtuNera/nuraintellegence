"""
Environment configuration and security utilities
"""

import os
import logging
from urllib.parse import urlparse

class EnvironmentConfig:
    """Secure environment configuration management"""
    
    @staticmethod
    def get_database_url():
        """Get and validate database URL from environment"""
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            logging.error("DATABASE_URL environment variable not set")
            raise ValueError("DATABASE_URL is required")
        
        # Validate URL format
        try:
            parsed = urlparse(database_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid DATABASE_URL format")
        except Exception as e:
            logging.error(f"Invalid DATABASE_URL: {e}")
            raise
        
        return database_url
    
    @staticmethod
    def get_session_secret():
        """Get session secret with fallback"""
        secret = os.environ.get('SESSION_SECRET')
        
        if not secret:
            # Generate a warning but provide a development fallback
            logging.warning("SESSION_SECRET not set, using development fallback")
            secret = 'dev-secret-key-change-in-production'
        
        return secret
    
    @staticmethod
    def get_gemini_api_key():
        """Get Gemini API key if available"""
        return os.environ.get('GEMINI_API_KEY')
    
    @staticmethod
    def is_production():
        """Check if running in production environment"""
        return os.environ.get('FLASK_ENV', 'development').lower() == 'production'
    
    @staticmethod
    def get_debug_mode():
        """Get debug mode setting"""
        if EnvironmentConfig.is_production():
            return False
        return os.environ.get('DEBUG', 'True').lower() in ['true', '1', 'yes']
    
    @staticmethod
    def validate_environment():
        """Validate all required environment variables"""
        required_vars = ['DATABASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logging.error(error_msg)
            raise EnvironmentError(error_msg)
        
        # Log configuration status
        logging.info("Environment validation successful")
        logging.info(f"Database URL configured: {'Yes' if os.environ.get('DATABASE_URL') else 'No'}")
        logging.info(f"Session secret configured: {'Yes' if os.environ.get('SESSION_SECRET') else 'No (using fallback)'}")
        logging.info(f"Gemini API configured: {'Yes' if os.environ.get('GEMINI_API_KEY') else 'No'}")
        logging.info(f"Production mode: {EnvironmentConfig.is_production()}")
        
        return True