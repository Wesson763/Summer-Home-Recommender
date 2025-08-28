"""
Data models for the Summer Home Finder application.

Contains User and Property classes that represent the core entities
in the property recommendation system.
"""

from app.models.user import User
from app.models.property import Property

__all__ = ["User", "Property"]
