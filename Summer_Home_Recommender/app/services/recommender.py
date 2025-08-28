"""
Property Recommender System with Vectorized Matching
Uses weighted scoring based on user search criteria with budget as highest priority
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from app.models.property import Property
import math

@dataclass
class SearchCriteria:
    """User search criteria with weights"""
    group_size: int
    preferred_environment: str
    min_budget: float
    max_budget: float
    location: str = ""
    user_preferences: str = ""
    
    # Weights for different criteria (location has highest weight)
    LOCATION_WEIGHT = 0.35    # Highest priority (destination matters most)
    BUDGET_WEIGHT = 0.25      # Important but not dominant
    FEATURES_WEIGHT = 0.20    # Third priority
    GROUP_SIZE_WEIGHT = 0.13  # Fourth priority
    ENVIRONMENT_WEIGHT = 0.07 # Lowest priority
    
    
    def get_adaptive_weights(self):
        """Get adaptive weights based on whether location is specified"""
        if self.location and self.location.strip():
            # User specified location - prioritize it even more
            return {
                'location': 0.40,  # Higher weight when location specified
                'budget': 0.225,
                'features': 0.175,
                'group_size': 0.13,
                'environment': 0.07
            }
        else:
            # No location specified - use default weights
            return {
                'location': 0.35,
                'budget': 0.25,
                'features': 0.20,
                'group_size': 0.13,
                'environment': 0.07
            }

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def distance_to_score(distance_km: float) -> float:
    """Convert distance in kilometers to a 0-1 score (closer = higher score)"""
    if distance_km == 0:
        return 1.0  # Same location
    
    # Score based on distance tiers (intuitive for users)
    if distance_km <= 5:
        return 1.0      # Same city/area (0-5 km)
    elif distance_km <= 25:
        return 0.9      # Nearby city (5-25 km)
    elif distance_km <= 100:
        return 0.7      # Regional (25-100 km)
    elif distance_km <= 500:
        return 0.4      # State/province level (100-500 km)
    else:
        return 0.1      # Very far (>500 km)

class PropertyRecommender:
    """Property recommender with vectorized matching"""
    
    def __init__(self, properties: List[Property]):
        self.properties = properties
        self._build_feature_vectors()
    
    def _build_feature_vectors(self):
        """Build feature vectors for all properties"""
        # Extract unique features and tags across all properties
        all_features = set()
        all_tags = set()
        all_locations = set()
        all_property_types = set()
        
        for prop in self.properties:
            all_features.update(prop.features)
            all_tags.update(prop.tags)
            all_locations.add(prop.location)
            all_property_types.add(prop.property_type)
        
        # Convert to sorted lists for consistent indexing
        self.feature_list = sorted(list(all_features))
        self.tag_list = sorted(list(all_tags))
        self.location_list = sorted(list(all_locations))
        self.property_type_list = sorted(list(all_property_types))
        
        # Build feature vectors for each property
        self.property_vectors = {}
        for prop in self.properties:
            self.property_vectors[prop.property_id] = self._create_property_vector(prop)
    
    def _create_property_vector(self, prop: Property) -> np.ndarray:
        """Create a feature vector for a single property"""
        vector = []
        
        # Location one-hot encoding
        location_vector = [1.0 if prop.location == loc else 0.0 for loc in self.location_list]
        vector.extend(location_vector)
        
        # Property type one-hot encoding
        type_vector = [1.0 if prop.property_type == prop_type else 0.0 for prop_type in self.property_type_list]
        vector.extend(type_vector)
        
        # Features one-hot encoding
        feature_vector = [1.0 if feature in prop.features else 0.0 for feature in self.feature_list]
        vector.extend(feature_vector)
        
        # Tags one-hot encoding
        tag_vector = [1.0 if tag in prop.tags else 0.0 for tag in self.tag_list]
        vector.extend(tag_vector)
        
        # Price (normalized to 0-1 scale)
        price_vector = [prop.price_per_night / 1000.0]  # Assuming max price around $1000
        vector.extend(price_vector)
        
        return np.array(vector)
    
    def _calculate_budget_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate budget compatibility score (0-1)"""
        price = prop.price_per_night
        
        if price < criteria.min_budget:
            # Below minimum budget - penalize heavily
            return 0.0
        elif price > criteria.max_budget:
            # Above maximum budget - penalize based on how much over
            overage_ratio = (price - criteria.max_budget) / criteria.max_budget
            if overage_ratio > 0.5:  # More than 50% over budget
                return 0.0
            else:
                return max(0.0, 1.0 - overage_ratio)
        else:
            # Within budget - higher score for lower prices
            budget_range = criteria.max_budget - criteria.min_budget
            if budget_range == 0:
                return 1.0
            
            # Prefer properties closer to min_budget (better value)
            position_in_range = (price - criteria.min_budget) / budget_range
            return 1.0 - (position_in_range * 0.3)  # Max 30% penalty for being at max budget
    
    def _calculate_environment_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate environment compatibility score (0-1)"""
        # Environment mapping based on location, features, and tags
        environment_keywords = {
            'mountain': ['mountain_view', 'hiking', 'ski_in_out', 'chalet', 'cabin', 'mountain'],
            'lake': ['lake_view', 'lakeside', 'kayaks', 'lake', 'waterfront'],
            'beach': ['ocean_view', 'beachfront', 'ocean', 'beach', 'coastal'],
            'city': ['apartment', 'condo', 'city_center', 'urban', 'downtown']
        }
        
        # Location-based environment detection
        location_environment_map = {
            # Mountain locations
            'mountain': ['banff', 'aspen', 'park city', 'whistler', 'boulder', 'blue mountains', 
                        'chamonix', 'zermatt', 'st. moritz', 'vail', 'breckenridge', 'telluride',
                        'jackson hole', 'sun valley', 'big sky', 'steamboat', 'keystone'],
            
            # Lake locations
            'lake': ['lake tahoe', 'lake como', 'lake geneva', 'lake louise', 'lake placid',
                    'lake george', 'lake winnipesaukee', 'lake michigan', 'lake superior',
                    'lake huron', 'lake erie', 'lake ontario'],
            
            # Beach locations
            'beach': ['miami', 'san diego', 'bali', 'cancun', 'amalfi', 'cape town', 'maui',
                     'kauai', 'oahu', 'big island', 'tahiti', 'bora bora', 'fiji', 'maldives',
                     'santorini', 'mykonos', 'ibiza', 'malibu', 'santa barbara', 'daytona beach',
                     'virginia beach', 'outer banks', 'key west', 'panama city beach'],
            
            # City locations
            'city': ['new york', 'london', 'tokyo', 'paris', 'berlin', 'barcelona', 'rome',
                    'amsterdam', 'prague', 'budapest', 'vienna', 'stockholm', 'copenhagen',
                    'oslo', 'helsinki', 'dublin', 'edinburgh', 'glasgow', 'manchester',
                    'boston', 'chicago', 'los angeles', 'san francisco', 'seattle', 'denver',
                    'atlanta', 'houston', 'dallas', 'phoenix', 'las vegas', 'orlando']
        }
        
        target_keywords = environment_keywords.get(criteria.preferred_environment.lower(), [])
        if not target_keywords:
            return 0.5  # Neutral score if environment not recognized
        
        # Check location-based environment match first (highest priority)
        location_score = 0.0
        for env, locations in location_environment_map.items():
            if env == criteria.preferred_environment.lower():
                if prop.location.lower() in locations:
                    location_score = 1.0  # Perfect match for location
                    break
        
        # Check if property has any of the target environment features/tags
        property_text = f"{prop.location} {prop.property_type} {' '.join(prop.features)} {' '.join(prop.tags)}".lower()
        
        feature_matches = sum(1 for keyword in target_keywords if keyword in property_text)
        feature_score = 0.0
        if feature_matches > 0:
            feature_score = min(1.0, 0.6 + (feature_matches * 0.1))  # Base 0.6 + bonus for multiple matches
        else:
            feature_score = 0.3  # Penalty for no feature match
        
        # Combine location and feature scores with location having higher weight
        if location_score > 0:
            # If location matches, give it high weight
            environment_score = (location_score * 0.7) + (feature_score * 0.3)
        else:
            # If no location match, rely more on features
            environment_score = (location_score * 0.3) + (feature_score * 0.7)
        
        return environment_score
    
    def _calculate_features_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate features compatibility score based on user preferences (0-1)"""
        if not criteria.user_preferences:
            return 0.5  # Neutral score if no preferences specified
        
        # Extract key words from user preferences
        preference_words = set(criteria.user_preferences.lower().split())
        
        if not preference_words:
            return 0.5
        
        # Check how many preference words match property features/tags
        property_text = f"{prop.property_type} {' '.join(prop.features)} {' '.join(prop.tags)}".lower()
        
        matches = sum(1 for word in preference_words if word in property_text)
        match_ratio = matches / len(preference_words)
        
        return min(1.0, 0.5 + (match_ratio * 0.5))  # Base 0.5 + bonus for matches
    
    def _calculate_location_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate location relevance score using geographic distance when possible"""
        if not criteria.location:
            return 0.7  # Neutral score if no location specified
        
        # First try geographic distance calculation
        distance_score = self._calculate_geographic_distance_score(prop, criteria)
        if distance_score is not None:
            return distance_score
        
        # Fallback to text-based matching if coordinates not available
        text_score = self._calculate_text_based_location_score(prop, criteria)
        return text_score
    
    def _calculate_geographic_distance_score(self, prop: Property, criteria: SearchCriteria) -> Optional[float]:
        """Calculate location score using geographic coordinates"""
        try:
            # Get coordinates for user's desired location
            user_coords = self._get_location_coordinates(criteria.location)
            if not user_coords:
                return None  # No coordinates available, fall back to text matching
            
            # Get coordinates for property location
            prop_coords = self._get_location_coordinates(prop.location)
            if not prop_coords:
                return None  # No coordinates available, fall back to text matching
            
            # Calculate distance
            distance_km = haversine_distance(
                user_coords['lat'], user_coords['lng'],
                prop_coords['lat'], prop_coords['lng']
            )
            
            # Convert distance to score
            return distance_to_score(distance_km)
            
        except Exception as e:
            # If any error occurs, fall back to text matching
            return None
    
    def _get_location_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a given location from the properties data"""
        try:
            # Look for a property with this location to get coordinates (case-insensitive)
            user_location = location.lower().strip()
            for prop in self.properties:
                if prop.location.lower().strip() == user_location:
                    # Check if the property has coordinates
                    if hasattr(prop, 'coordinates') and prop.coordinates:
                        return prop.coordinates
                    # If no coordinates on property, try to get from location mapping
                    break
            
            # If no coordinates found, return None
            return None
            
        except Exception:
            return None
    
    def _calculate_text_based_location_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate location score using text-based matching (fallback method)"""
        # Check if the property location matches the user's desired location
        user_location = criteria.location.lower().strip()
        property_location = prop.location.lower().strip()
        
        # Exact match gets perfect score
        if user_location == property_location:
            return 1.0
        
        # Partial match (e.g., "new york" matches "New York City")
        if user_location in property_location or property_location in user_location:
            return 0.9
        
        # Check for similar locations (e.g., "nyc" matches "New York")
        location_aliases = {
            'nyc': 'new york',
            'la': 'los angeles',
            'sf': 'san francisco',
            'miami beach': 'miami',
            'lake tahoe': 'tahoe',
        }
        
        if user_location in location_aliases and location_aliases[user_location] == property_location:
            return 0.9
        
        # No match - return low score
        return 0.2
    
    def _calculate_group_size_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate group size compatibility score (0-1) based on bedrooms"""
        if prop.bedrooms is None:
            return 0.5  # Neutral score if bedrooms not available
        
        # Calculate how well the property accommodates the group size
        # Assume each bedroom can sleep 2 people
        estimated_capacity = prop.bedrooms * 2
        
        if estimated_capacity >= criteria.group_size:
            # Property can accommodate the group
            if estimated_capacity == criteria.group_size:
                # Perfect match - highest score
                return 1.0
            elif estimated_capacity <= criteria.group_size + 2:
                # Close match (within 2 people) - very good score
                return 0.9
            else:
                # Larger than needed - slightly penalized
                excess_ratio = (estimated_capacity - criteria.group_size) / criteria.group_size
                return max(0.7, 1.0 - (excess_ratio * 0.2))  # Max 20% penalty for being too large
        else:
            # Property is too small for the group
            shortage_ratio = (criteria.group_size - estimated_capacity) / criteria.group_size
            if shortage_ratio <= 0.25:  # Within 25% of needed size
                return 0.4  # Moderate penalty
            elif shortage_ratio <= 0.5:  # Within 50% of needed size
                return 0.2  # Significant penalty
            else:
                return 0.0  # Too small - no match
    
    def _calculate_overall_score(self, prop: Property, criteria: SearchCriteria) -> float:
        """Calculate weighted overall score for a property"""
        budget_score = self._calculate_budget_score(prop, criteria)
        environment_score = self._calculate_environment_score(prop, criteria)
        features_score = self._calculate_features_score(prop, criteria)
        location_score = self._calculate_location_score(prop, criteria)
        group_size_score = self._calculate_group_size_score(prop, criteria)
        
        # Get adaptive weights based on whether location is specified
        weights = criteria.get_adaptive_weights()
        
        # Apply weights
        overall_score = (
            budget_score * weights['budget'] +
            environment_score * weights['environment'] +
            features_score * weights['features'] +
            location_score * weights['location'] +
            group_size_score * weights['group_size']
        )
        
        return overall_score
    
    def get_recommendations(self, criteria: SearchCriteria, top_k: int = 10) -> List[Tuple[Property, float]]:
        """Get top-k property recommendations with scores"""
        scored_properties = []
        
        for prop in self.properties:
            score = self._calculate_overall_score(prop, criteria)
            scored_properties.append((prop, score))
        
        # Sort by score (descending) and return top-k
        scored_properties.sort(key=lambda x: x[1], reverse=True)
        return scored_properties[:top_k]
    
    def get_detailed_recommendations(self, criteria: SearchCriteria, top_k: int = 5) -> List[Dict]:
        """Get detailed recommendations with breakdown of scores"""
        recommendations = []
        
        # Get adaptive weights
        weights = criteria.get_adaptive_weights()
        
        for prop in self.properties:
            budget_score = self._calculate_budget_score(prop, criteria)
            environment_score = self._calculate_environment_score(prop, criteria)
            features_score = self._calculate_features_score(prop, criteria)
            location_score = self._calculate_location_score(prop, criteria)
            group_size_score = self._calculate_group_size_score(prop, criteria)
            
            overall_score = self._calculate_overall_score(prop, criteria)
            
            recommendation = {
                'property': prop,
                'overall_score': overall_score,
                'score_breakdown': {
                    'budget': {
                        'score': budget_score,
                        'weight': weights['budget'],
                        'weighted_score': budget_score * weights['budget']
                    },
                    'environment': {
                        'score': environment_score,
                        'weight': weights['environment'],
                        'weighted_score': environment_score * weights['environment']
                    },
                    'features': {
                        'score': features_score,
                        'weight': weights['features'],
                        'weighted_score': features_score * weights['features']
                    },
                    'location': {
                        'score': location_score,
                        'weight': weights['location'],
                        'weighted_score': location_score * weights['location']
                    },
                    'group_size': {
                        'score': group_size_score,
                        'weight': weights['group_size'],
                        'weighted_score': group_size_score * weights['group_size']
                    }
                }
            }
            recommendations.append(recommendation)
        
        # Sort by overall score and return top-k
        recommendations.sort(key=lambda x: x['overall_score'], reverse=True)
        return recommendations[:top_k]


