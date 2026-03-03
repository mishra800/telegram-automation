"""
Database Backup and Recovery System
"""

import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from bot.config import Config
from bot.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseBackup:
    """Automated database backup and recovery"""
    
    def __init__(self):
        self.backup_dir = os.path.join(Config.BASE_DIR, 'backups')
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.databases = [
            Config.DB_PATH,
            Config.DB_PATH.replace('analytics.db', 'funnel.db'),
            Config.DB_PATH.replace('analytics.db', 'affiliates.db'),
            Config.DB_PATH.replace('analytics.db', 'conversations.db'),
            Config.DB_PATH.replace('analytics.db', 'content_history.db')
        ]
    
    def backup_all_databases(self):
        """Backup all databases"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_count = 0
        
        for db_path in self.databases:
            if not os.path.exists(db_path):
                continue
            
            try:
                db_name = os.path.basename(db_path)
                backup_name = f"{db_name}.{timestamp}.backup"
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                # Use SQLite backup API for safe backup
                source_conn = sqlite3.connect(db_path)
                backup_conn = sqlite3.connect(backup_path)
                
                source_conn.backup(backup_conn)
                
                source_conn.close()
                backup_conn.close()
                
                logger.info(f"Backed up {db_name} to {backup_name}")
                backup_count += 1
                
            except Exception as e:
                logger.error(f"Error backing up {db_path}: {e}")
        
        logger.info(f"Backup completed: {backup_count} databases backed up")
        
        # Cleanup old backups
        self.cleanup_old_backups(days=30)
        
        return backup_count
    
    def cleanup_old_backups(self, days=30):
        """Remove backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for filename in os.listdir(self.backup_dir):
            if not filename.endswith('.backup'):
                continue
            
            filepath = os.path.join(self.backup_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_time < cutoff_date:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting old backup {filename}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old backups")
    
    def restore_database(self, db_name, backup_timestamp=None):
        """Restore database from backup"""
        if backup_timestamp:
            backup_name = f"{db_name}.{backup_timestamp}.backup"
        else:
            # Find most recent backup
            backups = [f for f in os.listdir(self.backup_dir) 
                      if f.startswith(db_name) and f.endswith('.backup')]
            if not backups:
                logger.error(f"No backups found for {db_name}")
                return False
            
            backups.sort(reverse=True)
            backup_name = backups[0]
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        # Find original database path
        original_path = None
        for db_path in self.databases:
            if os.path.basename(db_path) == db_name:
                original_path = db_path
                break
        
        if not original_path:
            logger.error(f"Unknown database: {db_name}")
            return False
        
        try:
            # Create backup of current database before restore
            if os.path.exists(original_path):
                emergency_backup = f"{original_path}.pre_restore.backup"
                shutil.copy2(original_path, emergency_backup)
                logger.info(f"Created emergency backup: {emergency_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, original_path)
            logger.info(f"Restored {db_name} from {backup_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return False
    
    def verify_database_integrity(self, db_path):
        """Verify database integrity"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('PRAGMA integrity_check')
            result = cursor.fetchone()
            
            conn.close()
            
            if result and result[0] == 'ok':
                logger.info(f"Database integrity OK: {os.path.basename(db_path)}")
                return True
            else:
                logger.error(f"Database integrity FAILED: {os.path.basename(db_path)}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking database integrity: {e}")
            return False
    
    def verify_all_databases(self):
        """Verify integrity of all databases"""
        results = {}
        
        for db_path in self.databases:
            if os.path.exists(db_path):
                db_name = os.path.basename(db_path)
                results[db_name] = self.verify_database_integrity(db_path)
        
        return results
