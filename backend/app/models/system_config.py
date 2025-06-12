from datetime import datetime
from app import db
import json

class SystemConfig(db.Model):
    """
    System configuration model for storing application settings
    
    Used for:
    - System parameters
    - Feature toggles
    - Backup settings
    - Notification settings
    """
    
    __tablename__ = 'system_configs'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Configuration key and value
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.Enum('string', 'integer', 'float', 'boolean', 'json', name='config_types'), 
                           nullable=False, default='string')
    
    # Metadata
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')  # 'general', 'backup', 'notification', etc.
    is_public = db.Column(db.Boolean, default=False)  # Whether config can be read by non-admin users
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, config_key, config_value, config_type='string', **kwargs):
        """
        Initialize system config with required fields
        
        Args:
            config_key (str): Unique configuration key
            config_value: Configuration value
            config_type (str): Type of the configuration value
        """
        self.config_key = config_key
        self.set_value(config_value, config_type)
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_value(self, value, config_type=None):
        """
        Set configuration value with proper type conversion
        
        Args:
            value: Value to set
            config_type (str): Type of the value
        """
        if config_type:
            self.config_type = config_type
        
        if self.config_type == 'json':
            self.config_value = json.dumps(value) if not isinstance(value, str) else value
        elif self.config_type == 'boolean':
            self.config_value = str(bool(value)).lower()
        else:
            self.config_value = str(value)
    
    def get_value(self):
        """
        Get configuration value with proper type conversion
        
        Returns:
            Properly typed configuration value
        """
        if self.config_type == 'integer':
            return int(self.config_value)
        elif self.config_type == 'float':
            return float(self.config_value)
        elif self.config_type == 'boolean':
            return self.config_value.lower() in ('true', '1', 'yes', 'on')
        elif self.config_type == 'json':
            return json.loads(self.config_value)
        else:
            return self.config_value
    
    @staticmethod
    def get_config(key, default=None):
        """
        Get configuration value by key
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        config = SystemConfig.query.filter_by(config_key=key).first()
        return config.get_value() if config else default
    
    @staticmethod
    def set_config(key, value, config_type='string', description=None, category='general', is_public=False):
        """
        Set configuration value
        
        Args:
            key (str): Configuration key
            value: Configuration value
            config_type (str): Type of the value
            description (str): Description of the configuration
            category (str): Configuration category
            is_public (bool): Whether config is publicly readable
        
        Returns:
            SystemConfig: Configuration object
        """
        config = SystemConfig.query.filter_by(config_key=key).first()
        
        if config:
            # Update existing configuration
            config.set_value(value, config_type)
            if description:
                config.description = description
            config.category = category
            config.is_public = is_public
        else:
            # Create new configuration
            config = SystemConfig(
                config_key=key,
                config_value=value,
                config_type=config_type,
                description=description,
                category=category,
                is_public=is_public
            )
            db.session.add(config)
        
        db.session.commit()
        return config
    
    @staticmethod
    def get_configs_by_category(category, public_only=False):
        """
        Get all configurations in a category
        
        Args:
            category (str): Configuration category
            public_only (bool): Whether to return only public configs
        
        Returns:
            dict: Dictionary of configuration key-value pairs
        """
        query = SystemConfig.query.filter_by(category=category)
        
        if public_only:
            query = query.filter_by(is_public=True)
        
        configs = query.all()
        return {config.config_key: config.get_value() for config in configs}
    
    @staticmethod
    def initialize_default_configs():
        """Initialize default system configurations"""
        default_configs = [
            # General settings
            ('system_name', 'Product Evaluation System', 'string', 'System name', 'general', True),
            ('system_version', '1.0.0', 'string', 'System version', 'general', True),
            ('default_language', 'en', 'string', 'Default system language', 'general', True),
            ('timezone', 'UTC', 'string', 'System timezone', 'general', True),
            
            # Backup settings
            ('backup_enabled', True, 'boolean', 'Enable automatic backup', 'backup', False),
            ('backup_frequency', 'daily', 'string', 'Backup frequency (daily/weekly)', 'backup', False),
            ('backup_retention_days', 30, 'integer', 'Backup retention period in days', 'backup', False),
            ('backup_time', '02:00', 'string', 'Daily backup time (HH:MM)', 'backup', False),
            
            # Notification settings
            ('notifications_enabled', True, 'boolean', 'Enable in-app notifications', 'notification', False),
            ('email_notifications', False, 'boolean', 'Enable email notifications', 'notification', False),
            ('notification_retention_days', 90, 'integer', 'Notification retention period', 'notification', False),
            
            # Evaluation settings
            ('evaluation_number_prefix', 'EVAL', 'string', 'Evaluation number prefix', 'evaluation', False),
            ('auto_approval_enabled', False, 'boolean', 'Enable automatic approval for certain conditions', 'evaluation', False),
            ('max_evaluations_per_user', 50, 'integer', 'Maximum active evaluations per user', 'evaluation', False),
            
            # Security settings
            ('session_timeout_minutes', 480, 'integer', 'Session timeout in minutes (8 hours)', 'security', False),
            ('password_min_length', 8, 'integer', 'Minimum password length', 'security', False),
            ('max_login_attempts', 5, 'integer', 'Maximum login attempts before lockout', 'security', False),
            
            # UI settings
            ('items_per_page', 20, 'integer', 'Default items per page in lists', 'ui', True),
            ('theme', 'light', 'string', 'Default UI theme', 'ui', True),
            ('date_format', 'YYYY-MM-DD', 'string', 'Default date format', 'ui', True),
        ]
        
        for key, value, config_type, description, category, is_public in default_configs:
            if not SystemConfig.query.filter_by(config_key=key).first():
                SystemConfig.set_config(key, value, config_type, description, category, is_public)
    
    def to_dict(self, include_value=True):
        """
        Convert configuration to dictionary
        
        Args:
            include_value (bool): Whether to include the configuration value
        
        Returns:
            dict: Configuration data dictionary
        """
        data = {
            'id': self.id,
            'config_key': self.config_key,
            'config_type': self.config_type,
            'description': self.description,
            'category': self.category,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_value:
            data['config_value'] = self.get_value()
        
        return data
    
    def __repr__(self):
        return f'<SystemConfig {self.config_key}>' 