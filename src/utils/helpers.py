"""
Utility functions for route optimization
Includes distance calculations, time estimation, and helpers
"""

import numpy as np
from typing import Tuple, List, Dict
from datetime import datetime, timedelta
import math


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula.
    
    Args:
        lat1, lng1: Coordinates of first point (degrees)
        lat2, lng2: Coordinates of second point (degrees)
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> distance = haversine_distance(17.4485, 78.3908, 17.4400, 78.3811)
        >>> print(f"{distance:.2f} km")  # ~1.12 km
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lng1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lng2_rad = math.radians(lng2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def calculate_distance_matrix(locations: List[Dict]) -> np.ndarray:
    """
    Calculate distance matrix for all locations.
    
    Args:
        locations: List of dicts with 'lat' and 'lng' keys
    
    Returns:
        NxN numpy array where element [i][j] is distance from location i to j
    
    Example:
        >>> locations = [
        ...     {'lat': 17.4485, 'lng': 78.3908},
        ...     {'lat': 17.4400, 'lng': 78.3811}
        ... ]
        >>> matrix = calculate_distance_matrix(locations)
        >>> matrix.shape  # (2, 2)
    """
    n = len(locations)
    distance_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                distance_matrix[i][j] = haversine_distance(
                    locations[i]['lat'], locations[i]['lng'],
                    locations[j]['lat'], locations[j]['lng']
                )
    
    return distance_matrix


def calculate_total_distance(route: List[int], distance_matrix: np.ndarray) -> float:
    """
    Calculate total distance for a given route.
    
    Args:
        route: List of location indices representing the order
        distance_matrix: NxN distance matrix
    
    Returns:
        Total distance in kilometers
    
    Example:
        >>> route = [0, 2, 1, 3, 0]  # Start at 0, visit 2, 1, 3, return to 0
        >>> total = calculate_total_distance(route, distance_matrix)
    """
    total = 0.0
    for i in range(len(route) - 1):
        total += distance_matrix[route[i]][route[i + 1]]
    return total


def estimate_travel_time(distance_km: float, time_of_day: str = "normal") -> float:
    """
    Estimate travel time based on distance and traffic conditions.
    
    Args:
        distance_km: Distance in kilometers
        time_of_day: Traffic condition ('morning_rush', 'evening_rush', 'normal', 'night')
    
    Returns:
        Estimated time in hours
    
    Traffic multipliers simulate real Hyderabad conditions:
    - Morning rush (6-9 AM): 1.4x slower
    - Evening rush (5-8 PM): 1.5x slower
    - Normal: 1.0x
    - Night: 0.9x faster
    """
    # Base speed assumptions for Hyderabad
    base_speed_kmph = 35  # Average city speed
    
    traffic_multipliers = {
        'morning_rush': 1.4,   # 6-9 AM
        'evening_rush': 1.5,   # 5-8 PM
        'normal': 1.0,         # 9 AM - 5 PM
        'night': 0.9           # 8 PM - 6 AM
    }
    
    multiplier = traffic_multipliers.get(time_of_day, 1.0)
    effective_speed = base_speed_kmph / multiplier
    
    time_hours = distance_km / effective_speed
    return time_hours


def get_traffic_condition(current_time: datetime) -> str:
    """
    Determine traffic condition based on time of day.
    
    Args:
        current_time: datetime object
    
    Returns:
        Traffic condition string
    """
    hour = current_time.hour
    
    if 6 <= hour < 9:
        return 'morning_rush'
    elif 17 <= hour < 20:
        return 'evening_rush'
    elif 20 <= hour or hour < 6:
        return 'night'
    else:
        return 'normal'


def format_time(hours: float) -> str:
    """
    Format time in hours to readable string.
    
    Args:
        hours: Time in hours (can be decimal)
    
    Returns:
        Formatted string like "2h 30m"
    
    Example:
        >>> format_time(2.5)
        '2h 30m'
        >>> format_time(0.75)
        '45m'
    """
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    
    if h > 0:
        return f"{h}h {m}m"
    else:
        return f"{m}m"


def calculate_fuel_cost(distance_km: float, fuel_efficiency_kmpl: float = 12, 
                        fuel_price_per_liter: float = 95) -> float:
    """
    Calculate fuel cost for a journey.
    
    Args:
        distance_km: Total distance in kilometers
        fuel_efficiency_kmpl: Vehicle fuel efficiency (km per liter)
        fuel_price_per_liter: Fuel price in rupees
    
    Returns:
        Fuel cost in rupees
    
    Example:
        >>> cost = calculate_fuel_cost(82.5, 12, 95)
        >>> print(f"₹{cost:.2f}")  # ₹653.13
    """
    liters_needed = distance_km / fuel_efficiency_kmpl
    cost = liters_needed * fuel_price_per_liter
    return cost


def calculate_route_metrics(route: List[int], locations: List[Dict], 
                            distance_matrix: np.ndarray,
                            start_time: datetime = None) -> Dict:
    """
    Calculate comprehensive metrics for a route.
    
    Args:
        route: List of location indices
        locations: List of location dicts
        distance_matrix: Distance matrix
        start_time: Starting time (default: now)
    
    Returns:
        Dictionary with all metrics
    """
    if start_time is None:
        start_time = datetime.now().replace(hour=9, minute=0)  # Default 9 AM
    
    total_distance = calculate_total_distance(route, distance_matrix)
    
    # Calculate time considering traffic
    current_time = start_time
    total_time = 0.0
    stop_times = [start_time]
    
    for i in range(len(route) - 1):
        segment_distance = distance_matrix[route[i]][route[i + 1]]
        traffic_condition = get_traffic_condition(current_time)
        segment_time = estimate_travel_time(segment_distance, traffic_condition)
        
        total_time += segment_time
        current_time += timedelta(hours=segment_time)
        stop_times.append(current_time)
    
    fuel_cost = calculate_fuel_cost(total_distance)
    
    return {
        'total_distance_km': round(total_distance, 2),
        'total_time_hours': round(total_time, 2),
        'total_time_formatted': format_time(total_time),
        'fuel_cost_inr': round(fuel_cost, 2),
        'start_time': start_time,
        'end_time': stop_times[-1],
        'stop_times': stop_times,
        'num_stops': len(route) - 1,  # Excluding return to warehouse
        'avg_distance_per_stop': round(total_distance / (len(route) - 1), 2)
    }


def calculate_co2_emissions(distance_km: float, emission_factor: float = 2.31) -> float:
    """
    Calculate CO2 emissions for a journey.
    
    Args:
        distance_km: Total distance
        emission_factor: kg CO2 per liter of fuel (default: 2.31 for diesel)
    
    Returns:
        CO2 emissions in kg
    """
    liters_needed = distance_km / 12  # Assuming 12 kmpl
    co2_kg = liters_needed * emission_factor
    return co2_kg


# Test function
if __name__ == "__main__":
    # Test distance calculation
    print("Testing Haversine Distance Calculation")
    print("=" * 50)
    
    # Test 1: Distance between two known points
    warehouse = {'lat': 17.4485, 'lng': 78.3908}
    madhapur = {'lat': 17.4400, 'lng': 78.3811}
    
    dist = haversine_distance(
        warehouse['lat'], warehouse['lng'],
        madhapur['lat'], madhapur['lng']
    )
    print(f"\nWarehouse to Madhapur: {dist:.2f} km")
    
    # Test 2: Distance matrix
    locations = [warehouse, madhapur, {'lat': 17.4239, 'lng': 78.3460}]
    matrix = calculate_distance_matrix(locations)
    print(f"\nDistance Matrix Shape: {matrix.shape}")
    print("Distance Matrix:")
    print(matrix)
    
    # Test 3: Time estimation
    print("\n" + "=" * 50)
    print("Testing Travel Time Estimation")
    print("=" * 50)
    
    test_distance = 10.5  # km
    
    for condition in ['morning_rush', 'normal', 'evening_rush', 'night']:
        time = estimate_travel_time(test_distance, condition)
        print(f"{condition:15s}: {format_time(time):8s} for {test_distance} km")
    
    # Test 4: Fuel cost
    print("\n" + "=" * 50)
    print("Testing Cost Calculation")
    print("=" * 50)
    
    test_distances = [50, 82.5, 120]
    for dist in test_distances:
        cost = calculate_fuel_cost(dist)
        co2 = calculate_co2_emissions(dist)
        print(f"{dist:6.1f} km → ₹{cost:7.2f} fuel, {co2:5.2f} kg CO2")
    
    print("\n✅ All tests completed successfully!")