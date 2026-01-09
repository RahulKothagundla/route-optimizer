"""
Data loading and geocoding utilities
Handles CSV loading, data validation, and coordinate processing
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


def load_addresses(csv_path: str = "data/hyderabad_addresses.csv") -> pd.DataFrame:
    """
    Load delivery addresses from CSV file.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        DataFrame with address data
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Address file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Validate required columns
    required_columns = ['id', 'customer_name', 'address', 'lat', 'lng', 'locality', 'package_count']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Validate data types
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
    df['package_count'] = pd.to_numeric(df['package_count'], errors='coerce').fillna(1).astype(int)
    
    # Remove any rows with invalid coordinates
    df = df.dropna(subset=['lat', 'lng'])
    
    if len(df) == 0:
        raise ValueError("No valid addresses found in CSV")
    
    print(f"✅ Loaded {len(df)} delivery addresses")
    return df


def load_warehouse(json_path: str = "data/warehouse.json") -> Dict:
    """
    Load warehouse configuration from JSON file.
    
    Args:
        json_path: Path to warehouse JSON file
    
    Returns:
        Dictionary with warehouse data
    
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        ValueError: If required fields are missing
    """
    json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Warehouse file not found: {json_path}")
    
    with open(json_path, 'r') as f:
        warehouse = json.load(f)
    
    # Validate required fields
    required_fields = ['name', 'address', 'lat', 'lng']
    missing_fields = [field for field in required_fields if field not in warehouse]
    
    if missing_fields:
        raise ValueError(f"Missing required warehouse fields: {missing_fields}")
    
    print(f"✅ Loaded warehouse: {warehouse['name']}")
    return warehouse


def addresses_to_locations(df: pd.DataFrame) -> List[Dict]:
    """
    Convert DataFrame to list of location dictionaries.
    
    Args:
        df: DataFrame with address data
    
    Returns:
        List of location dicts with standardized format
    """
    locations = []
    
    for _, row in df.iterrows():
        location = {
            'id': int(row['id']),
            'name': str(row['customer_name']),
            'address': str(row['address']),
            'lat': float(row['lat']),
            'lng': float(row['lng']),
            'locality': str(row['locality']),
            'package_count': int(row['package_count'])
        }
        locations.append(location)
    
    return locations


def get_locality_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get summary statistics by locality.
    
    Args:
        df: DataFrame with address data
    
    Returns:
        Summary DataFrame with counts and package totals by locality
    """
    summary = df.groupby('locality').agg({
        'id': 'count',
        'package_count': 'sum'
    }).rename(columns={
        'id': 'num_addresses',
        'package_count': 'total_packages'
    })
    
    summary = summary.sort_values('num_addresses', ascending=False)
    return summary


def validate_coordinates(lat: float, lng: float, 
                        hyderabad_bounds: Dict = None) -> bool:
    """
    Validate if coordinates are within Hyderabad bounds.
    
    Args:
        lat: Latitude
        lng: Longitude
        hyderabad_bounds: Optional custom bounds
    
    Returns:
        True if coordinates are valid and within bounds
    """
    # Default Hyderabad bounds (approximate)
    if hyderabad_bounds is None:
        hyderabad_bounds = {
            'lat_min': 17.2,
            'lat_max': 17.6,
            'lng_min': 78.2,
            'lng_max': 78.6
        }
    
    # Check if coordinates are valid numbers
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        return False
    
    # Check if within bounds
    if not (hyderabad_bounds['lat_min'] <= lat <= hyderabad_bounds['lat_max']):
        return False
    
    if not (hyderabad_bounds['lng_min'] <= lng <= hyderabad_bounds['lng_max']):
        return False
    
    return True


def get_bounding_box(locations: List[Dict]) -> Dict:
    """
    Calculate bounding box for a list of locations.
    Useful for map centering and zoom level.
    
    Args:
        locations: List of location dicts with 'lat' and 'lng'
    
    Returns:
        Dict with min/max lat/lng and center point
    """
    lats = [loc['lat'] for loc in locations]
    lngs = [loc['lng'] for loc in locations]
    
    return {
        'lat_min': min(lats),
        'lat_max': max(lats),
        'lng_min': min(lngs),
        'lng_max': max(lngs),
        'center_lat': sum(lats) / len(lats),
        'center_lng': sum(lngs) / len(lngs)
    }


def filter_by_locality(df: pd.DataFrame, localities: List[str]) -> pd.DataFrame:
    """
    Filter addresses by specific localities.
    
    Args:
        df: DataFrame with address data
        localities: List of locality names to keep
    
    Returns:
        Filtered DataFrame
    """
    return df[df['locality'].isin(localities)]


def get_distance_statistics(df: pd.DataFrame, warehouse: Dict) -> Dict:
    """
    Calculate distance statistics from warehouse to all addresses.
    
    Args:
        df: DataFrame with addresses
        warehouse: Warehouse dict with lat/lng
    
    Returns:
        Dictionary with distance statistics
    """
    from .helpers import haversine_distance
    
    distances = []
    for _, row in df.iterrows():
        dist = haversine_distance(
            warehouse['lat'], warehouse['lng'],
            row['lat'], row['lng']
        )
        distances.append(dist)
    
    return {
        'min_distance_km': round(min(distances), 2),
        'max_distance_km': round(max(distances), 2),
        'avg_distance_km': round(sum(distances) / len(distances), 2),
        'total_addresses': len(distances)
    }


# Test function
if __name__ == "__main__":
    print("Testing Data Loading Utilities")
    print("=" * 60)
    
    try:
        # Test 1: Load addresses
        print("\n1. Loading Addresses...")
        df = load_addresses("data/hyderabad_addresses.csv")
        print(f"   Loaded {len(df)} addresses")
        print(f"   Columns: {list(df.columns)}")
        
        # Test 2: Load warehouse
        print("\n2. Loading Warehouse...")
        warehouse = load_warehouse("data/warehouse.json")
        print(f"   Warehouse: {warehouse['name']}")
        print(f"   Location: ({warehouse['lat']}, {warehouse['lng']})")
        
        # Test 3: Locality summary
        print("\n3. Locality Summary:")
        summary = get_locality_summary(df)
        print(summary)
        
        # Test 4: Convert to locations
        print("\n4. Converting to Locations...")
        locations = addresses_to_locations(df)
        print(f"   Created {len(locations)} location objects")
        print(f"   Sample location: {locations[0]['name']} at {locations[0]['locality']}")
        
        # Test 5: Bounding box
        print("\n5. Calculating Bounding Box...")
        bbox = get_bounding_box(locations)
        print(f"   Center: ({bbox['center_lat']:.4f}, {bbox['center_lng']:.4f})")
        print(f"   Latitude range: {bbox['lat_min']:.4f} to {bbox['lat_max']:.4f}")
        print(f"   Longitude range: {bbox['lng_min']:.4f} to {bbox['lng_max']:.4f}")
        
        # Test 6: Distance statistics
        print("\n6. Distance Statistics...")
        dist_stats = get_distance_statistics(df, warehouse)
        print(f"   Min distance: {dist_stats['min_distance_km']} km")
        print(f"   Max distance: {dist_stats['max_distance_km']} km")
        print(f"   Avg distance: {dist_stats['avg_distance_km']} km")
        
        # Test 7: Coordinate validation
        print("\n7. Testing Coordinate Validation...")
        test_coords = [
            (17.4485, 78.3908, "Valid Hyderabad"),
            (28.6139, 77.2090, "Invalid - Delhi"),
            (200, 300, "Invalid - Out of range")
        ]
        
        for lat, lng, desc in test_coords:
            is_valid = validate_coordinates(lat, lng)
            status = "✅" if is_valid else "❌"
            print(f"   {status} {desc}: ({lat}, {lng})")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()