# 🔌 API Documentation - Summer Home Finder

## Overview
The Summer Home Finder application uses several internal APIs and external services for property recommendations and user management.

## External APIs

### OpenAI/OpenRouter API
- **Purpose**: AI-powered location recommendations
- **Endpoint**: https://openrouter.ai/api/v1
- **Model**: meta-llama/llama-3.3-70b-instruct:free
- **Rate Limit**: 1 request per minute (free tier)
- **Authentication**: API key required

## Internal Services

### Property Recommender Service
```python
from app.services.recommender import PropertyRecommender, SearchCriteria

# Create search criteria
criteria = SearchCriteria(
    group_size=4,
    preferred_environment="mountain",
    min_budget=150,
    max_budget=300,
    location="banff",
    user_preferences="cozy cabin with fireplace"
)

# Get recommendations
recommender = PropertyRecommender(properties)
recommendations = recommender.get_detailed_recommendations(criteria, top_k=5)
```

### Chatbot Service
```python
from app.services.chatbot import ChatbotService

# Initialize service
chatbot = ChatbotService(api_key="your_api_key")

# Get location recommendation
location_rec = chatbot.get_location_recommendation(
    "I want a mountain retreat for 4 people, budget $200-300/night"
)
```

### Authentication Service
```python
from app.services.auth import create_user_account, authenticate_user

# Create account
user, message = create_user_account("John Doe", "john@example.com", "SecurePass123!")

# Authenticate user
user = authenticate_user("john@example.com", "SecurePass123!")
```

## Data Models

### User Model
```python
from app.models.user import User

# User properties
user.user_id      # Unique identifier
user.name         # Full name
user.email        # Email address
user.password     # Hashed password

# User methods
user.update_profile(**kwargs)  # Update profile
user.check_password(password)  # Verify password
```

### Property Model
```python
from app.models.property import Property

# Property properties
property.property_id      # Unique identifier
property.location         # City/location
property.property_type    # Type (cabin, villa, etc.)
property.price_per_night  # Price per night
property.features         # List of features
property.bedrooms         # Number of bedrooms
property.coordinates      # GPS coordinates
```

## File Structure
```
app/
├── models/          # Data models (User, Property)
├── services/        # Business logic (Recommender, Chatbot, Auth)
├── utils/           # Helper functions
└── data/            # Data files (properties.json)
```

## Error Handling
All services return `None` or appropriate error messages on failure. Check return values before proceeding.

## Rate Limiting
- OpenAI API: 1 request/minute (free tier)
- Consider implementing caching for production use
```