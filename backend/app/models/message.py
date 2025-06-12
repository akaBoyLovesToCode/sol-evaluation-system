from datetime import datetime
from enum import Enum
from app import db


class MessageType(Enum):
    """Message type enumeration"""
    APPROVAL_REQUEST = 'approval_request'
    STATUS_CHANGE = 'status_change'
    SYSTEM_ANNOUNCEMENT = 'system_announcement'
    EVALUATION_ASSIGNED = 'evaluation_assigned'
    EVALUATION_COMPLETED = 'evaluation_completed'
    SYSTEM = 'system'
    REMINDER = 'reminder'
    DIGEST = 'digest'


class MessageStatus(Enum):
    """Message status enumeration"""
    UNREAD = 'unread'
    READ = 'read'


class MessagePriority(Enum):
    """Message priority enumeration"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'

class Message(db.Model):
    """
    Message model for in-app notifications and communication
    
    Used for:
    - Approval notifications
    - Status change notifications  
    - System announcements
    """
    
    __tablename__ = 'messages'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Message content
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    # Message type and priority
    message_type = db.Column(db.Enum('approval_request', 'status_change', 'system_announcement', 
                                   'evaluation_assigned', 'evaluation_completed', name='message_types'), 
                           nullable=False)
    priority = db.Column(db.Enum('low', 'normal', 'high', 'urgent', name='message_priority'), 
                        nullable=False, default='normal')
    
    # Recipient and status
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    read_at = db.Column(db.DateTime)
    
    # Related evaluation (optional)
    evaluation_id = db.Column(db.Integer, db.ForeignKey('evaluations.id'))
    
    # Sender information (optional, for system messages sender_id can be null)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    evaluation = db.relationship('Evaluation', backref='messages')
    
    def __init__(self, title, content, message_type, recipient_id, **kwargs):
        """
        Initialize message with required fields
        
        Args:
            title (str): Message title
            content (str): Message content
            message_type (str): Type of message
            recipient_id (int): ID of the recipient
        """
        self.title = title
        self.content = content
        self.message_type = message_type
        self.recipient_id = recipient_id
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
            db.session.commit()
    
    def mark_as_unread(self):
        """Mark message as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            db.session.commit()
    
    @staticmethod
    def create_approval_request(evaluation, recipient_id, approval_level):
        """
        Create approval request message
        
        Args:
            evaluation (Evaluation): Evaluation object
            recipient_id (int): ID of the approver
            approval_level (str): 'part' or 'group'
        
        Returns:
            Message: Created message object
        """
        level_text = 'Part Leader' if approval_level == 'part' else 'Group Leader'
        
        title = f'Approval Request: {evaluation.evaluation_number}'
        content = (f'Evaluation {evaluation.evaluation_number} for {evaluation.product_name} '
                  f'requires {level_text} approval.\n\n'
                  f'Evaluation Type: {evaluation.evaluation_type.replace("_", " ").title()}\n'
                  f'Part Number: {evaluation.part_number}\n'
                  f'Evaluator: {evaluation.evaluator.full_name}\n'
                  f'Start Date: {evaluation.start_date}')
        
        message = Message(
            title=title,
            content=content,
            message_type='approval_request',
            recipient_id=recipient_id,
            evaluation_id=evaluation.id,
            priority='high'
        )
        
        return message
    
    @staticmethod
    def create_status_change(evaluation, recipient_id, old_status, new_status):
        """
        Create status change notification
        
        Args:
            evaluation (Evaluation): Evaluation object
            recipient_id (int): ID of the recipient
            old_status (str): Previous status
            new_status (str): New status
        
        Returns:
            Message: Created message object
        """
        title = f'Status Update: {evaluation.evaluation_number}'
        content = (f'Evaluation {evaluation.evaluation_number} status has changed '
                  f'from "{old_status.replace("_", " ").title()}" '
                  f'to "{new_status.replace("_", " ").title()}".\n\n'
                  f'Product: {evaluation.product_name}\n'
                  f'Part Number: {evaluation.part_number}')
        
        message = Message(
            title=title,
            content=content,
            message_type='status_change',
            recipient_id=recipient_id,
            evaluation_id=evaluation.id,
            priority='normal'
        )
        
        return message
    
    @staticmethod
    def create_system_announcement(title, content, recipient_ids, priority='normal'):
        """
        Create system announcement for multiple recipients
        
        Args:
            title (str): Announcement title
            content (str): Announcement content
            recipient_ids (list): List of recipient IDs
            priority (str): Message priority
        
        Returns:
            list: List of created message objects
        """
        messages = []
        for recipient_id in recipient_ids:
            message = Message(
                title=title,
                content=content,
                message_type='system_announcement',
                recipient_id=recipient_id,
                priority=priority
            )
            messages.append(message)
        
        return messages
    
    def to_dict(self):
        """
        Convert message to dictionary
        
        Returns:
            dict: Message data dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'message_type': self.message_type,
            'priority': self.priority,
            'recipient_id': self.recipient_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'evaluation_id': self.evaluation_id,
            'sender_id': self.sender_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender_name': self.sender.full_name if self.sender else 'System',
            'evaluation_number': self.evaluation.evaluation_number if self.evaluation else None
        }
    
    def __repr__(self):
        return f'<Message {self.title} to User {self.recipient_id}>' 