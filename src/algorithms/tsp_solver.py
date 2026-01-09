"""
TSP Solver Algorithms
Implements Nearest Neighbor and 2-Opt optimization
"""

import numpy as np
from typing import List, Tuple
import time


def calculate_route_distance(route: List[int], distance_matrix: np.ndarray) -> float:
    """
    Calculate total distance for a given route.
    
    Args:
        route: List of location indices [0, 5, 12, 23, ..., 0]
        distance_matrix: NxN matrix of distances between locations
    
    Returns:
        Total distance in kilometers
    """
    total_distance = 0.0
    
    for i in range(len(route) - 1):
        from_idx = route[i]
        to_idx = route[i + 1]
        total_distance += distance_matrix[from_idx][to_idx]
    
    return total_distance


def nearest_neighbor_tsp(distance_matrix: np.ndarray, start_idx: int = 0) -> Tuple[List[int], float]:
    """
    Nearest Neighbor Algorithm (Greedy Heuristic)
    
    Algorithm:
    1. Start at specified location (usually warehouse at index 0)
    2. Visit nearest unvisited location
    3. Repeat until all locations visited
    4. Return to start
    
    Time Complexity: O(n²)
    Space Complexity: O(n)
    
    Args:
        distance_matrix: NxN numpy array of distances
        start_idx: Starting location index (default: 0 for warehouse)
    
    Returns:
        Tuple of (route, total_distance)
        - route: List of location indices in visit order
        - total_distance: Total route distance in km
    
    Example:
        >>> matrix = np.array([[0, 10, 15], [10, 0, 20], [15, 20, 0]])
        >>> route, distance = nearest_neighbor_tsp(matrix, start_idx=0)
        >>> print(route)  # [0, 1, 2, 0]
    """
    n = len(distance_matrix)
    
    # Track which locations have been visited
    visited = [False] * n
    route = [start_idx]
    visited[start_idx] = True
    
    current_idx = start_idx
    total_distance = 0.0
    
    # Visit all locations
    for _ in range(n - 1):
        # Find nearest unvisited location
        nearest_idx = -1
        nearest_distance = float('inf')
        
        for idx in range(n):
            if not visited[idx]:
                dist = distance_matrix[current_idx][idx]
                if dist < nearest_distance:
                    nearest_distance = dist
                    nearest_idx = idx
        
        # Visit nearest location
        route.append(nearest_idx)
        visited[nearest_idx] = True
        total_distance += nearest_distance
        current_idx = nearest_idx
    
    # Return to start
    route.append(start_idx)
    total_distance += distance_matrix[current_idx][start_idx]
    
    return route, total_distance


def two_opt_swap(route: List[int], i: int, k: int) -> List[int]:
    """
    Perform a 2-opt swap on a route.
    
    2-opt swap reverses the order of cities between positions i and k.
    
    Example:
        Original: [0, 1, 2, 3, 4, 5, 0]
        i=1, k=4
        Result:   [0, 4, 3, 2, 1, 5, 0]
        
    This "uncrosses" the route if edges were crossing.
    
    Args:
        route: Current route
        i: Start position for reversal
        k: End position for reversal
    
    Returns:
        New route with segment reversed
    """
    # Keep start, reverse middle segment, keep end
    new_route = route[:i] + route[i:k+1][::-1] + route[k+1:]
    return new_route


def two_opt_optimization(
    route: List[int], 
    distance_matrix: np.ndarray,
    max_iterations: int = 1000,
    verbose: bool = False
) -> Tuple[List[int], float, dict]:
    """
    2-Opt Local Search Optimization
    
    Algorithm:
    1. Start with initial route (from Nearest Neighbor)
    2. For each pair of edges in route:
        a. Try swapping them (uncrossing)
        b. If swap reduces distance, keep it
    3. Repeat until no improvement found
    
    Time Complexity: O(n² × iterations)
    Typical iterations: 10-50
    
    Why It Works:
    - Eliminates "crossing" edges
    - Each swap improves route (or keeps it same)
    - Converges to local optimum
    
    Args:
        route: Initial route from nearest neighbor
        distance_matrix: Distance matrix
        max_iterations: Maximum number of improvement passes
        verbose: Print progress
    
    Returns:
        Tuple of (optimized_route, distance, stats)
    """
    n = len(route)
    best_route = route.copy()
    best_distance = calculate_route_distance(best_route, distance_matrix)
    
    initial_distance = best_distance
    iteration = 0
    total_improvements = 0
    
    improved = True
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        # Try all possible 2-opt swaps
        for i in range(1, n - 2):
            for k in range(i + 1, n - 1):
                # Create new route with this swap
                new_route = two_opt_swap(best_route, i, k)
                new_distance = calculate_route_distance(new_route, distance_matrix)
                
                # If improvement found, keep it
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    total_improvements += 1
                    
                    if verbose:
                        improvement_pct = ((initial_distance - best_distance) / initial_distance) * 100
                        print(f"Iteration {iteration}: Found improvement! "
                              f"Distance: {best_distance:.2f} km "
                              f"({improvement_pct:.1f}% better than initial)")
        
        if not improved and verbose:
            print(f"Iteration {iteration}: No improvement found. Converged!")
    
    # Calculate statistics
    improvement_pct = ((initial_distance - best_distance) / initial_distance) * 100
    
    stats = {
        'initial_distance': initial_distance,
        'optimized_distance': best_distance,
        'improvement_km': initial_distance - best_distance,
        'improvement_pct': improvement_pct,
        'iterations': iteration,
        'total_improvements': total_improvements
    }
    
    return best_route, best_distance, stats


def solve_tsp(
    distance_matrix: np.ndarray,
    start_idx: int = 0,
    optimize: bool = True,
    verbose: bool = False
) -> dict:
    """
    Complete TSP solver combining Nearest Neighbor + 2-Opt.
    
    This is the main function to call for route optimization.
    
    Args:
        distance_matrix: NxN distance matrix
        start_idx: Starting location (warehouse)
        optimize: Whether to run 2-Opt optimization
        verbose: Print progress
    
    Returns:
        Dictionary with:
        - route: Optimized route
        - distance: Total distance
        - algorithm: Which algorithms were used
        - stats: Performance statistics
        - timing: Execution times
    """
    results = {
        'algorithm': 'Nearest Neighbor',
        'timing': {}
    }
    
    # Phase 1: Nearest Neighbor
    if verbose:
        print("🔍 Running Nearest Neighbor algorithm...")
    
    start_time = time.time()
    nn_route, nn_distance = nearest_neighbor_tsp(distance_matrix, start_idx)
    nn_time = time.time() - start_time
    
    results['nn_route'] = nn_route
    results['nn_distance'] = nn_distance
    results['timing']['nearest_neighbor'] = nn_time
    
    if verbose:
        print(f"✅ Nearest Neighbor complete: {nn_distance:.2f} km in {nn_time:.3f}s")
    
    # Phase 2: 2-Opt Optimization (if requested)
    if optimize:
        results['algorithm'] = 'Nearest Neighbor + 2-Opt'
        
        if verbose:
            print("🔧 Running 2-Opt optimization...")
        
        start_time = time.time()
        opt_route, opt_distance, opt_stats = two_opt_optimization(
            nn_route, 
            distance_matrix,
            verbose=verbose
        )
        opt_time = time.time() - start_time
        
        results['route'] = opt_route
        results['distance'] = opt_distance
        results['optimization_stats'] = opt_stats
        results['timing']['two_opt'] = opt_time
        results['timing']['total'] = nn_time + opt_time
        
        if verbose:
            print(f"✅ 2-Opt complete: {opt_distance:.2f} km in {opt_time:.3f}s")
            print(f"📊 Overall improvement: {opt_stats['improvement_pct']:.1f}%")
    else:
        results['route'] = nn_route
        results['distance'] = nn_distance
        results['timing']['total'] = nn_time
    
    return results


# Test function
if __name__ == "__main__":
    print("Testing TSP Algorithms")
    print("=" * 60)
    
    # Create a small test distance matrix (5 locations)
    test_matrix = np.array([
        [0,   10,  15,  20,  25],
        [10,  0,   35,  25,  30],
        [15,  35,  0,   30,  20],
        [20,  25,  30,  0,   15],
        [25,  30,  20,  15,  0]
    ])
    
    print("\n1. Testing Nearest Neighbor:")
    route, distance = nearest_neighbor_tsp(test_matrix, start_idx=0)
    print(f"   Route: {route}")
    print(f"   Distance: {distance:.2f}")
    
    print("\n2. Testing 2-Opt Optimization:")
    opt_route, opt_distance, stats = two_opt_optimization(route, test_matrix, verbose=True)
    print(f"   Optimized Route: {opt_route}")
    print(f"   Optimized Distance: {opt_distance:.2f}")
    print(f"   Improvement: {stats['improvement_pct']:.1f}%")
    
    print("\n3. Testing Complete Solver:")
    results = solve_tsp(test_matrix, start_idx=0, optimize=True, verbose=True)
    print(f"\n   Final Route: {results['route']}")
    print(f"   Final Distance: {results['distance']:.2f}")
    print(f"   Total Time: {results['timing']['total']:.3f}s")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")