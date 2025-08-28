"""
Business logic services for the Summer Home Finder application.

Contains the recommendation engine, chatbot service, and other
core business logic components.
"""

from app.services.recommender import PropertyRecommender, SearchCriteria
from app.services.chatbot import ChatbotService
from app.services.auth import (
    create_user_account, 
    authenticate_user, 
    create_user_from_input,
    validate_user_credentials,
    get_user_by_email
)

__all__ = [
    "PropertyRecommender",
    "SearchCriteria", 
    "ChatbotService",
    "create_user_account",
    "authenticate_user",
    "create_user_from_input",
    "validate_user_credentials",
    "get_user_by_email"
]
