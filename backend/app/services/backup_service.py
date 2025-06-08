"""
Backup Service for SSD Evaluation System

This service handles data backup system as specified in Phase 4 requirements.
Manages database backups, file backups, and backup scheduling.
"""

import os
import subprocess
import gzip
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app
from app.models.system_config import SystemConfig
import tarfile


class BackupService:
    """
    Service class for managing data backups
    
    Handles:
    - Database backups
    - File system backups
    - Backup scheduling
    - Backup restoration
    - Backup cleanup
    """
    
    @staticmethod
    def create_database_backup(backup_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a database backup
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            Tuple of (success: bool, message: str, backup_path: Optional[str])
        """
        try:
            # Generate backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            if not backup_name:
                backup_name = f"ssd_evaluation_db_{timestamp}"
            
            backup_dir = current_app.config.get('BACKUP_FOLDER', 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_path = os.path.join(backup_dir, f"{backup_name}.sql.gz")
            
            # Get database configuration
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            
            # Parse database URI to extract connection details
            # Format: mysql+pymysql://user:password@host:port/database
            if 'mysql' in db_uri:
                # Extract connection details
                import re
                pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, db_uri)
                
                if not match:
                    return False, "Could not parse database URI", None
                
                user, password, host, port, database = match.groups()
                
                # Create mysqldump command
                dump_cmd = [
                    'mysqldump',
                    f'--host={host}',
                    f'--port={port}',
                    f'--user={user}',
                    f'--password={password}',
                    '--single-transaction',
                    '--routines',
                    '--triggers',
                    '--events',
                    '--add-drop-database',
                    '--create-options',
                    '--disable-keys',
                    '--extended-insert',
                    '--quick',
                    '--lock-tables=false',
                    database
                ]
                
                # Execute mysqldump and compress
                with gzip.open(backup_path, 'wt') as f:
                    result = subprocess.run(
                        dump_cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                
                if result.returncode != 0:
                    return False, f"Database backup failed: {result.stderr}", None
                
                # Create backup metadata
                metadata = {
                    'backup_name': backup_name,
                    'created_at': datetime.utcnow().isoformat(),
                    'database': database,
                    'backup_type': 'database',
                    'file_size': os.path.getsize(backup_path),
                    'compressed': True
                }
                
                metadata_path = os.path.join(backup_dir, f"{backup_name}.json")
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                current_app.logger.info(f"Database backup created: {backup_path}")
                return True, f"Database backup created successfully: {backup_name}", backup_path
            
            else:
                return False, "Unsupported database type for backup", None
                
        except Exception as e:
            current_app.logger.error(f"Error creating database backup: {str(e)}")
            return False, f"Backup failed: {str(e)}", None
    
    @staticmethod
    def create_files_backup(backup_name: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        Create a backup of uploaded files and logs
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            Tuple of (success: bool, message: str, backup_path: Optional[str])
        """
        try:
            # Generate backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            if not backup_name:
                backup_name = f"ssd_evaluation_files_{timestamp}"
            
            backup_dir = current_app.config.get('BACKUP_FOLDER', 'backups')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            backup_path = os.path.join(backup_dir, f"{backup_name}.tar.gz")
            
            # Directories to backup
            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
            log_folder = os.path.dirname(current_app.config.get('LOG_FILE', 'logs/app.log'))
            
            # Create tar.gz archive
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Add upload folder if it exists
                if os.path.exists(upload_folder):
                    tar.add(upload_folder, arcname='uploads')
                
                # Add log folder if it exists
                if os.path.exists(log_folder):
                    tar.add(log_folder, arcname='logs')
            
            # Create backup metadata
            metadata = {
                'backup_name': backup_name,
                'created_at': datetime.utcnow().isoformat(),
                'backup_type': 'files',
                'file_size': os.path.getsize(backup_path),
                'compressed': True,
                'included_folders': []
            }
            
            if os.path.exists(upload_folder):
                metadata['included_folders'].append('uploads')
            if os.path.exists(log_folder):
                metadata['included_folders'].append('logs')
            
            metadata_path = os.path.join(backup_dir, f"{backup_name}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            current_app.logger.info(f"Files backup created: {backup_path}")
            return True, f"Files backup created successfully: {backup_name}", backup_path
            
        except Exception as e:
            current_app.logger.error(f"Error creating files backup: {str(e)}")
            return False, f"Files backup failed: {str(e)}", None
    
    @staticmethod
    def create_full_backup(backup_name: Optional[str] = None) -> Tuple[bool, str, List[str]]:
        """
        Create a full system backup (database + files)
        
        Args:
            backup_name: Optional custom backup name
            
        Returns:
            Tuple of (success: bool, message: str, backup_paths: List[str])
        """
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            if not backup_name:
                backup_name = f"ssd_evaluation_full_{timestamp}"
            
            backup_paths = []
            
            # Create database backup
            db_success, db_message, db_path = BackupService.create_database_backup(f"{backup_name}_db")
            if db_success and db_path:
                backup_paths.append(db_path)
            
            # Create files backup
            files_success, files_message, files_path = BackupService.create_files_backup(f"{backup_name}_files")
            if files_success and files_path:
                backup_paths.append(files_path)
            
            # Check overall success
            if db_success and files_success:
                return True, f"Full backup created successfully: {backup_name}", backup_paths
            elif db_success:
                return True, f"Partial backup created (database only): {db_message}", backup_paths
            elif files_success:
                return True, f"Partial backup created (files only): {files_message}", backup_paths
            else:
                return False, f"Backup failed: DB - {db_message}, Files - {files_message}", backup_paths
                
        except Exception as e:
            current_app.logger.error(f"Error creating full backup: {str(e)}")
            return False, f"Full backup failed: {str(e)}", []
    
    @staticmethod
    def list_backups() -> List[Dict]:
        """
        List all available backups
        
        Returns:
            List of backup information dictionaries
        """
        try:
            backup_dir = current_app.config.get('BACKUP_FOLDER', 'backups')
            if not os.path.exists(backup_dir):
                return []
            
            backups = []
            
            # Find all metadata files
            for filename in os.listdir(backup_dir):
                if filename.endswith('.json'):
                    metadata_path = os.path.join(backup_dir, filename)
                    try:
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        
                        # Check if backup file still exists
                        backup_name = metadata.get('backup_name', '')
                        backup_type = metadata.get('backup_type', 'unknown')
                        
                        if backup_type == 'database':
                            backup_file = f"{backup_name}.sql.gz"
                        elif backup_type == 'files':
                            backup_file = f"{backup_name}.tar.gz"
                        else:
                            continue
                        
                        backup_file_path = os.path.join(backup_dir, backup_file)
                        if os.path.exists(backup_file_path):
                            metadata['file_exists'] = True
                            metadata['file_path'] = backup_file_path
                            # Update file size if different
                            current_size = os.path.getsize(backup_file_path)
                            metadata['file_size'] = current_size
                        else:
                            metadata['file_exists'] = False
                        
                        backups.append(metadata)
                        
                    except Exception as e:
                        current_app.logger.warning(f"Error reading backup metadata {filename}: {str(e)}")
                        continue
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return backups
            
        except Exception as e:
            current_app.logger.error(f"Error listing backups: {str(e)}")
            return []
    
    @staticmethod
    def delete_backup(backup_name: str) -> Tuple[bool, str]:
        """
        Delete a backup and its metadata
        
        Args:
            backup_name: Name of the backup to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            backup_dir = current_app.config.get('BACKUP_FOLDER', 'backups')
            
            # Find and delete backup files
            deleted_files = []
            
            # Check for different backup file types
            possible_extensions = ['.sql.gz', '.tar.gz', '.json']
            
            for ext in possible_extensions:
                file_path = os.path.join(backup_dir, f"{backup_name}{ext}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(f"{backup_name}{ext}")
            
            if deleted_files:
                current_app.logger.info(f"Deleted backup files: {', '.join(deleted_files)}")
                return True, f"Backup deleted successfully: {', '.join(deleted_files)}"
            else:
                return False, f"Backup not found: {backup_name}"
                
        except Exception as e:
            current_app.logger.error(f"Error deleting backup: {str(e)}")
            return False, f"Failed to delete backup: {str(e)}"
    
    @staticmethod
    def cleanup_old_backups(days_to_keep: int = 30) -> Tuple[int, str]:
        """
        Clean up old backups to save disk space
        
        Args:
            days_to_keep: Number of days to keep backups
            
        Returns:
            Tuple of (deleted_count: int, message: str)
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            backups = BackupService.list_backups()
            
            deleted_count = 0
            
            for backup in backups:
                try:
                    created_at = datetime.fromisoformat(backup['created_at'])
                    if created_at < cutoff_date:
                        success, message = BackupService.delete_backup(backup['backup_name'])
                        if success:
                            deleted_count += 1
                except Exception as e:
                    current_app.logger.warning(f"Error processing backup {backup.get('backup_name', 'unknown')}: {str(e)}")
                    continue
            
            message = f"Cleaned up {deleted_count} old backups (older than {days_to_keep} days)"
            current_app.logger.info(message)
            return deleted_count, message
            
        except Exception as e:
            current_app.logger.error(f"Error cleaning up old backups: {str(e)}")
            return 0, f"Cleanup failed: {str(e)}"
    
    @staticmethod
    def get_backup_statistics() -> Dict:
        """
        Get backup system statistics
        
        Returns:
            Dictionary with backup statistics
        """
        try:
            backups = BackupService.list_backups()
            
            stats = {
                'total_backups': len(backups),
                'database_backups': len([b for b in backups if b.get('backup_type') == 'database']),
                'files_backups': len([b for b in backups if b.get('backup_type') == 'files']),
                'total_size_bytes': sum([b.get('file_size', 0) for b in backups if b.get('file_exists', False)]),
                'oldest_backup': None,
                'newest_backup': None,
                'missing_files': len([b for b in backups if not b.get('file_exists', False)])
            }
            
            # Format total size in human readable format
            size_bytes = stats['total_size_bytes']
            if size_bytes < 1024:
                stats['total_size_formatted'] = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                stats['total_size_formatted'] = f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                stats['total_size_formatted'] = f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                stats['total_size_formatted'] = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
            # Find oldest and newest backups
            if backups:
                sorted_backups = sorted(backups, key=lambda x: x.get('created_at', ''))
                stats['oldest_backup'] = sorted_backups[0].get('created_at')
                stats['newest_backup'] = sorted_backups[-1].get('created_at')
            
            return stats
            
        except Exception as e:
            current_app.logger.error(f"Error getting backup statistics: {str(e)}")
            return {}
    
    @staticmethod
    def schedule_automatic_backup() -> bool:
        """
        Schedule automatic backup (to be called by a cron job or scheduler)
        
        Returns:
            bool: Success status
        """
        try:
            # Get backup configuration from system config
            config = SystemConfig.get_config()
            auto_backup_enabled = config.get('auto_backup_enabled', False)
            
            if not auto_backup_enabled:
                current_app.logger.info("Automatic backup is disabled")
                return True
            
            backup_frequency = config.get('backup_frequency_days', 7)
            
            # Check if we need to create a backup
            backups = BackupService.list_backups()
            
            if backups:
                # Get the most recent backup
                latest_backup = max(backups, key=lambda x: x.get('created_at', ''))
                latest_date = datetime.fromisoformat(latest_backup['created_at'])
                
                # Check if enough time has passed
                if (datetime.utcnow() - latest_date).days < backup_frequency:
                    current_app.logger.info(f"Automatic backup not needed yet (last backup: {latest_date})")
                    return True
            
            # Create automatic backup
            success, message, paths = BackupService.create_full_backup("auto_backup")
            
            if success:
                current_app.logger.info(f"Automatic backup completed: {message}")
                
                # Clean up old backups if configured
                cleanup_days = config.get('backup_retention_days', 30)
                BackupService.cleanup_old_backups(cleanup_days)
                
                return True
            else:
                current_app.logger.error(f"Automatic backup failed: {message}")
                return False
                
        except Exception as e:
            current_app.logger.error(f"Error in automatic backup: {str(e)}")
            return False 