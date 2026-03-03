import logging
import os
from datetime import datetime
from bot.config import Config

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Ensure logs directory exists
        os.makedirs(Config.LOGS_DIR, exist_ok=True)
        
        log_file = os.path.join(
            Config.LOGS_DIR,
            f"{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
