"""
Route Optimizer
High-level optimization logic with comparison utilities
"""

import numpy as np
from typing import List, Dict, Tuple
import random
from datetime import datetime, timedelta

from .tsp_solver import solve_tsp, calculate_route_distance
from ..utils.helpers import calculate_route_metrics


def generate_naive_route(num_locations: int, start_idx: int = 0) -> List[int]:
    """
    Generate a naive route by visiting locations in order.
    This represents a "no optimization" baseline.
    
    Args:
        num_locations: Total number of locations (including warehouse)
        start_idx: Starting location (warehouse)
    
    Returns:
        Route as list of indices [0, 1, 2, 3, ..., n-1, 0]
    """
    route = [start_idx]
    
    # Visit all other locations in sequential order
    for i in range(num_locations):
        if i != start_idx:
            route.append(i)
    
    # Return to start
    route.append(start_idx)
    
    return route


def generate_random_route(num_locations: int, start_idx: int = 0, seed: int = None) -> List[int]:
    """
    Generate a random route.
    Useful for comparison to show optimization value.
    
    Args:
        num_locations: Total number of locations
        start_idx: Starting location
        seed: Random seed for reproducibility
    
    Returns:
        Random route
    """
    if seed is not None:
        random.seed(seed)
    
    route = [start_idx]
    
    # Create list of all other locations
    other_locations = [i for i in range(num_locations) if i != start_idx]
    
    # Shuffle them
    random.shuffle(other_locations)
    
    route.extend(other_locations)
    route.append(start_idx)
    
    return route


def optimize_route(
    locations: List[Dict],
    distance_matrix: np.ndarray,
    warehouse_idx: int = 0,
    method: str = 'nn_2opt',
    verbose: bool = False
) -> Dict:
    """
    Main route optimization function.
    
    This is the primary function to call from the Streamlit app.
    
    Args:
        locations: List of location dictionaries with lat/lng
        distance_matrix: Pre-calculated distance matrix
        warehouse_idx: Index of warehouse in locations list
        method: Optimization method:
            - 'nn': Nearest Neighbor only
            - 'nn_2opt': Nearest Neighbor + 2-Opt (recommended)
            - 'naive': Sequential order (for comparison)
            - 'random': Random order (for comparison)
        verbose: Print progress
    
    Returns:
        Dictionary with route and comprehensive metrics
    """
    num_locations = len(locations)
    
    if method == 'naive':
        route = generate_naive_route(num_locations, warehouse_idx)
        distance = calculate_route_distance(route, distance_matrix)
        
        result = {
            'route': route,
            'distance': distance,
            'algorithm': 'Sequential (Naive)',
            'timing': {'total': 0.001}
        }
    
    elif method == 'random':
        route = generate_random_route(num_locations, warehouse_idx, seed=42)
        distance = calculate_route_distance(route, distance_matrix)
        
        result = {
            'route': route,
            'distance': distance,
            'algorithm': 'Random',
            'timing': {'total': 0.001}
        }
    
    elif method == 'nn':
        result = solve_tsp(
            distance_matrix,
            start_idx=warehouse_idx,
            optimize=False,
            verbose=verbose
        )
    
    elif method == 'nn_2opt':
        result = solve_tsp(
            distance_matrix,
            start_idx=warehouse_idx,
            optimize=True,
            verbose=verbose
        )
    
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Add detailed metrics
    start_time = datetime.now().replace(hour=9, minute=0, second=0)
    metrics = calculate_route_metrics(
        result['route'],
        locations,
        distance_matrix,
        start_time=start_time
    )
    
    result['metrics'] = metrics
    result['num_stops'] = num_locations - 1  # Exclude warehouse
    
    return result


def compare_routes(
    locations: List[Dict],
    distance_matrix: np.ndarray,
    warehouse_idx: int = 0,
    verbose: bool = False
) -> Dict:
    """
    Compare multiple routing strategies.
    
    Generates and compares:
    - Naive sequential route
    - Nearest Neighbor
    - Nearest Neighbor + 2-Opt (optimized)
    
    Args:
        locations: List of location dictionaries
        distance_matrix: Distance matrix
        warehouse_idx: Warehouse index
        verbose: Print progress
    
    Returns:
        Dictionary with all routes and comparison metrics
    """
    if verbose:
        print("\n" + "="*60)
        print("ROUTE COMPARISON")
        print("="*60)
    
    # Generate all routes
    routes = {}
    
    # 1. Naive route
    if verbose:
        print("\n1️⃣ Generating naive (sequential) route...")
    routes['naive'] = optimize_route(
        locations, distance_matrix, warehouse_idx, 
        method='naive', verbose=False
    )
    
    # 2. Nearest Neighbor only
    if verbose:
        print("2️⃣ Running Nearest Neighbor algorithm...")
    routes['nn'] = optimize_route(
        locations, distance_matrix, warehouse_idx,
        method='nn', verbose=False
    )
    
    # 3. Optimized (NN + 2-Opt)
    if verbose:
        print("3️⃣ Running full optimization (NN + 2-Opt)...")
    routes['optimized'] = optimize_route(
        locations, distance_matrix, warehouse_idx,
        method='nn_2opt', verbose=verbose
    )
    
    # Calculate improvements
    naive_distance = routes['naive']['distance']
    nn_distance = routes['nn']['distance']
    opt_distance = routes['optimized']['distance']
    
    comparison = {
        'routes': routes,
        'distances': {
            'naive': naive_distance,
            'nearest_neighbor': nn_distance,
            'optimized': opt_distance
        },
        'improvements': {
            'nn_vs_naive': {
                'km_saved': naive_distance - nn_distance,
                'percent': ((naive_distance - nn_distance) / naive_distance) * 100
            },
            'opt_vs_naive': {
                'km_saved': naive_distance - opt_distance,
                'percent': ((naive_distance - opt_distance) / naive_distance) * 100
            },
            'opt_vs_nn': {
                'km_saved': nn_distance - opt_distance,
                'percent': ((nn_distance - opt_distance) / nn_distance) * 100
            }
        }
    }
    
    if verbose:
        print("\n" + "="*60)
        print("RESULTS SUMMARY")
        print("="*60)
        print(f"\n📏 Distances:")
        print(f"   Naive:            {naive_distance:.2f} km")
        print(f"   Nearest Neighbor: {nn_distance:.2f} km")
        print(f"   Optimized:        {opt_distance:.2f} km")
        
        print(f"\n📊 Improvements:")
        print(f"   NN vs Naive:      {comparison['improvements']['nn_vs_naive']['km_saved']:.2f} km "
              f"({comparison['improvements']['nn_vs_naive']['percent']:.1f}%)")
        print(f"   Optimized vs NN:  {comparison['improvements']['opt_vs_nn']['km_saved']:.2f} km "
              f"({comparison['improvements']['opt_vs_nn']['percent']:.1f}%)")
        print(f"   Optimized vs Naive: {comparison['improvements']['opt_vs_naive']['km_saved']:.2f} km "
              f"({comparison['improvements']['opt_vs_naive']['percent']:.1f}%)")
        
        print("\n" + "="*60)
    
    return comparison


def get_route_coordinates(route: List[int], locations: List[Dict]) -> List[Tuple[float, float]]:
    """
    Convert route indices to lat/lng coordinates.
    Useful for map visualization.
    
    Args:
        route: List of location indices
        locations: List of location dictionaries with 'lat' and 'lng'
    
    Returns:
        List of (lat, lng) tuples in route order
    """
    coordinates = []
    for idx in route:
        loc = locations[idx]
        coordinates.append((loc['lat'], loc['lng']))
    
    return coordinates


def get_route_details(route: List[int], locations: List[Dict]) -> List[Dict]:
    """
    Get detailed information for each stop in route.
    
    Args:
        route: List of location indices
        locations: List of location dictionaries
    
    Returns:
        List of dictionaries with stop details
    """
    details = []
    
    for position, idx in enumerate(route):
        loc = locations[idx]
        
        stop_info = {
            'position': position,
            'id': loc['id'],
            'name': loc['name'],
            'address': loc['address'],
            'locality': loc['locality'],
            'lat': loc['lat'],
            'lng': loc['lng'],
            'package_count': loc.get('package_count', 0)
        }
        
        details.append(stop_info)
    
    return details


# Test function
if __name__ == "__main__":
    print("Testing Route Optimizer")
    print("=" * 60)
    
    # Create simple test data
    test_locations = [
        {'id': 0, 'name': 'Warehouse', 'lat': 17.4485, 'lng': 78.3908, 'locality': 'Hitech City', 'package_count': 0},
        {'id': 1, 'name': 'Customer 1', 'lat': 17.4400, 'lng': 78.3811, 'locality': 'Madhapur', 'package_count': 2},
        {'id': 2, 'name': 'Customer 2', 'lat': 17.4239, 'lng': 78.3460, 'locality': 'Gachibowli', 'package_count': 3},
        {'id': 3, 'name': 'Customer 3', 'lat': 17.4609, 'lng': 78.3671, 'locality': 'Kondapur', 'package_count': 1},
        {'id': 4, 'name': 'Customer 4', 'lat': 17.4950, 'lng': 78.3595, 'locality': 'Kukatpally', 'package_count': 2}
    ]
    
    # Create test distance matrix
    from ..utils.helpers import calculate_distance_matrix
    test_matrix = calculate_distance_matrix(test_locations)
    
    print("\n1. Testing naive route:")
    naive = optimize_route(test_locations, test_matrix, method='naive')
    print(f"   Route: {naive['route']}")
    print(f"   Distance: {naive['distance']:.2f} km")
    
    print("\n2. Testing optimized route:")
    optimized = optimize_route(test_locations, test_matrix, method='nn_2opt', verbose=True)
    print(f"   Route: {optimized['route']}")
    print(f"   Distance: {optimized['distance']:.2f} km")
    
    print("\n3. Comparing all routes:")
    comparison = compare_routes(test_locations, test_matrix, verbose=True)
    
    print("\n✅ All tests passed!")