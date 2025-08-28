from app.models.property import Property
import json
import os

##### 2. Load Properties from JSON File #####
def load_properties_from_json(json_file_path="properties.json"):
    """Load properties from the properties.json file"""
    try:
        # Get the directory where this script is located (app/utils/)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to app/, then into data/
        data_dir = os.path.join(script_dir, "..", "data")
        json_path = os.path.join(data_dir, json_file_path)
        
        with open(json_path, 'r', encoding='utf-8') as file:
            properties_data = json.load(file)
        
        # Convert JSON data to Property objects
        properties = []
        for prop_data in properties_data:
            try:
                property_obj = Property(
                    property_id=prop_data["property_id"],
                    location=prop_data["location"],
                    property_type=prop_data["property_type"],
                    price_per_night=prop_data["price_per_night"],
                    features=prop_data["features"],
                    tags=prop_data["tags"],
                    coordinates=prop_data.get("coordinates"),
                    bedrooms=prop_data.get("bedrooms")
                )
                properties.append(property_obj)
            except KeyError as e:
                print(f"Warning: Skipping property with missing field {e}: {prop_data}")
                continue
            except Exception as e:
                print(f"Warning: Skipping property due to error {e}: {prop_data}")
                continue
        
        print(f"✅ Successfully loaded {len(properties)} properties from {json_file_path}")
        return properties
        
    except FileNotFoundError:
        print(f"❌ Error: {json_file_path} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {json_file_path}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error loading properties: {e}")
        return []

# Load properties from JSON file
properties = load_properties_from_json()