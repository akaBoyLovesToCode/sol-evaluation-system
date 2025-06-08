#!/usr/bin/env python3
"""
Simple test script to check imports
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    from app import create_app
    print("✓ app.create_app imported successfully")
    
    # Test model imports
    from app.models import User, Evaluation, SystemConfig
    print("✓ Models imported successfully")
    
    # Test enum imports
    from app.models.evaluation import EvaluationStatus, EvaluationType
    print("✓ Evaluation enums imported successfully")
    
    from app.models.user import UserRole
    print("✓ User enums imported successfully")
    
    from app.models.operation_log import OperationType
    print("✓ Operation enums imported successfully")
    
    from app.models.message import MessageType, MessageStatus
    print("✓ Message enums imported successfully")
    
    # Test service imports
    from app.services.workflow_service import WorkflowService
    print("✓ Workflow service imported successfully")
    
    # Test API imports
    from app.api.workflow import workflow_bp
    print("✓ Workflow API imported successfully")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 