"""
Summer Home Finder - AI-Powered Property Recommendation System

A Streamlit application that helps users find their perfect summer getaway
using intelligent property matching or an AI-powered chatbot.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main components for easy access 
from app.models.user import User
from app.models.property import Property
from app.services.recommender import PropertyRecommender
from app.services.chatbot import ChatbotService

# Define what gets imported with "from app import *"
__all__ = [
    "User", 
    "Property",
    "PropertyRecommender",
    "ChatbotService"
]
