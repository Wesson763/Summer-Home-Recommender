"""
Chatbot service for the Summer Home Finder application.

Provides AI-powered location recommendations through conversational interface.
"""

from openai import OpenAI
import json
from typing import Optional, Dict, Any

class ChatbotService:
    """Service class for handling AI chatbot interactions"""
    
    def __init__(self, api_key: str, properties: list = None, base_url: str = "https://openrouter.ai/api/v1"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0
        )
        self.properties = properties or []
    
    def get_location_recommendation(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        """
        Get specific property recommendation from AI based on user conversation and available properties.
        
        Args:
            user_prompt: User's description of what they're looking for
            
        Returns:
            Dictionary with specific property recommendation data or None if failed
        """
        try:
            if not self.properties:
                return None
                
            # Create a summary of available properties for the AI
            property_summary = self._create_property_summary()
            
            # Prepare the AI prompt
            system_prompt = f"""You are a helpful travel advisor specializing in summer home recommendations. 
            You have access to a database of {len(self.properties)} available properties.
            
            Based on the user's description, you need to recommend ONE specific property from the available database that best matches their preferences.
            
            You must return a JSON response with the following structure:
            {{
                "property_id": "ID of the recommended property",
                "location": "City/Location of the property",
                "property_type": "Type of property (house, apartment, villa, etc.)",
                "price_per_night": number,
                "bedrooms": number,
                "features": ["feature1", "feature2", "feature3"],
                "tags": ["tag1", "tag2", "tag3"],
                "reasoning": "Detailed explanation of why this specific property is perfect for the user"
            }}
            
            Available properties summary:
            {property_summary}
            
            Important rules:
            1. Choose ONE specific property from the available database
            2. Match the property_id exactly as shown in the summary
            3. Use the actual price_per_night from the property
            4. Use the actual features and tags from the property
            5. Provide specific reasoning based on the property's actual attributes
            6. Return ONLY valid JSON, no additional text"""
            
            user_prompt_enhanced = f"""User request: {user_prompt}
            
            Please analyze this request and recommend the single best property from the available database. Consider:
            - Group size and composition (match with bedrooms)
            - Location preferences
            - Budget constraints (match with price_per_night)
            - Feature preferences (match with actual property features)
            - Property type preferences
            
            Return only the JSON response."""
            
            # Make AI request
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-3.3-70b-instruct:free",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_enhanced}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = completion.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Find JSON in the response (in case AI adds extra text)
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = ai_response[start_idx:end_idx]
                    property_data = json.loads(json_str)
                    
                    # Validate required fields
                    required_fields = ['property_id', 'location', 'property_type', 'price_per_night', 'bedrooms', 'features', 'tags', 'reasoning']
                    if all(field in property_data for field in required_fields):
                        return property_data
                    else:
                        return None
                else:
                    return None
                    
            except json.JSONDecodeError:
                return None
                
        except Exception:
            return None
            
    def _create_property_summary(self) -> str:
        """Create a summary of available properties for the AI prompt"""
        if not self.properties:
            return "No properties available"
            
        # Sample a subset of properties to avoid overwhelming the AI
        sample_size = min(50, len(self.properties))
        sample_properties = self.properties[:sample_size]
        
        summary_lines = []
        for prop in sample_properties:
            summary_lines.append(
                f"ID: {prop.property_id}, Location: {prop.location}, "
                f"Type: {prop.property_type}, Price: ${prop.price_per_night}/night, "
                f"Bedrooms: {prop.bedrooms or 'N/A'}, "
                f"Features: {', '.join(prop.features[:3])}, "
                f"Tags: {', '.join(prop.tags[:3])}"
            )
        
        if len(self.properties) > sample_size:
            summary_lines.append(f"... and {len(self.properties) - sample_size} more properties")
            
        return "\n".join(summary_lines)


