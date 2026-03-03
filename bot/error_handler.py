"""
Robust Error Handling and Recovery System
"""

import time
import traceback
from functools import wraps
from datetime import datetime, timedelta
from bot.logger import setup_logger

logger = setup_logger(__name__)

class ErrorHandler:
    """Centralized error handling with retry logic"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = {}
        self.circuit_breakers = {}
    
    def retry_with_backoff(self, max_retries=3, base_delay=1, max_delay=60, 
                          exponential=True, exceptions=(Exception,)):
        """Decorator for retry logic with exponential backoff"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                retries = 0
                delay = base_delay
                
                while retries < max_retries:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        retries += 1
                        
                        if retries >= max_retries:
                            logger.error(f"{func.__name__} failed after {max_retries} attempts: {e}")
                            self._record_error(func.__name__, e)
                            raise
                        
                        logger.warning(f"{func.__name__} failed (attempt {retries}/{max_retries}): {e}")
                        logger.info(f"Retrying in {delay} seconds...")
                        
                        time.sleep(delay)
                        
                        if exponential:
                            delay = min(delay * 2, max_delay)
                        else:
                            delay = min(delay + base_delay, max_delay)
                
                return None
            return wrapper
        return decorator
    
    def circuit_breaker(self, failure_threshold=5, timeout=300):
        """Circuit breaker pattern to prevent cascading failures"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                func_name = func.__name__
                
                # Check if circuit is open
                if func_name in self.circuit_breakers:
                    breaker = self.circuit_breakers[func_name]
                    if breaker['state'] == 'open':
                        # Check if timeout has passed
                        if datetime.now() - breaker['opened_at'] < timedelta(seconds=timeout):
                            logger.warning(f"Circuit breaker OPEN for {func_name}, skipping call")
                            return None
                        else:
                            # Try half-open state
                            logger.info(f"Circuit breaker entering HALF-OPEN state for {func_name}")
                            breaker['state'] = 'half-open'
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Success - close circuit
                    if func_name in self.circuit_breakers:
                        self.circuit_breakers[func_name] = {
                            'state': 'closed',
                            'failures': 0,
                            'opened_at': None
                        }
                    
                    return result
                    
                except Exception as e:
                    # Record failure
                    if func_name not in self.circuit_breakers:
                        self.circuit_breakers[func_name] = {
                            'state': 'closed',
                            'failures': 0,
                            'opened_at': None
                        }
                    
                    self.circuit_breakers[func_name]['failures'] += 1
                    
                    # Open circuit if threshold reached
                    if self.circuit_breakers[func_name]['failures'] >= failure_threshold:
                        self.circuit_breakers[func_name]['state'] = 'open'
                        self.circuit_breakers[func_name]['opened_at'] = datetime.now()
                        logger.error(f"Circuit breaker OPENED for {func_name} after {failure_threshold} failures")
                    
                    raise
            
            return wrapper
        return decorator
    
    def _record_error(self, func_name, error):
        """Record error for monitoring"""
        if func_name not in self.error_counts:
            self.error_counts[func_name] = 0
        
        self.error_counts[func_name] += 1
        self.last_errors[func_name] = {
            'error': str(error),
            'timestamp': datetime.now(),
            'traceback': traceback.format_exc()
        }
    
    def get_error_stats(self):
        """Get error statistics"""
        return {
            'error_counts': self.error_counts,
            'last_errors': self.last_errors,
            'circuit_breakers': self.circuit_breakers
        }
    
    def safe_execute(self, func, *args, fallback=None, **kwargs):
        """Safely execute function with fallback"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            self._record_error(func.__name__, e)
            return fallback

# Global error handler instance
error_handler = ErrorHandler()
