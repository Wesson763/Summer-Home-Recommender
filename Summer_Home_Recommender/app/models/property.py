# Define Property Class
class Property:
    def __init__(self, property_id, location, property_type, price_per_night, features, tags, coordinates=None, bedrooms=None):
        self.property_id = property_id
        self.location = location
        self.property_type = property_type
        self.price_per_night = price_per_night
        self.features = features
        self.tags = tags
        self.coordinates = coordinates  # {"lat": float, "lng": float}
        self.bedrooms = bedrooms  # Number of bedrooms for group size matching
    
    def __repr__(self):
        coord_info = f", Coordinates: {self.coordinates}" if self.coordinates else ""
        bedrooms_info = f", Bedrooms: {self.bedrooms}" if self.bedrooms is not None else ""
        return (f"Property(ID: {self.property_id}, Location: {self.location}, "
                f"Type: {self.property_type}, Price: ${self.price_per_night}/night, "
                f"Features: {self.features}, Tags: {self.tags}{coord_info}{bedrooms_info})")

    def to_dict(self):
        """Convert a Property object into a dictionary for JSON storage."""
        result = {
            "property_id": self.property_id,
            "location": self.location,
            "property_type": self.property_type,  # Keep field name consistent
            "price_per_night": self.price_per_night,
            "features": self.features,
            "tags": self.tags,
        }
        if self.coordinates:
            result["coordinates"] = self.coordinates
        if self.bedrooms is not None:
            result["bedrooms"] = self.bedrooms
        return result

    @classmethod
    def from_dict(cls, d):
        """Recreate a Property object from a dictionary."""
        coordinates = d.get("coordinates")  # Optional field
        bedrooms = d.get("bedrooms")  # Optional field
        return cls(
            property_id=d["property_id"],
            location=d["location"],
            property_type=d["property_type"],  # Match the dictionary key
            price_per_night=d["price_per_night"],
            features=d["features"],
            tags=d["tags"],
            coordinates=coordinates,
            bedrooms=bedrooms
        )