"""API package for Solution Evaluation System (simplified).

Contains the public, auth-less evaluation endpoints.
"""

from .evaluation import evaluation_bp

__all__ = ["evaluation_bp"]
