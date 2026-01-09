"""
Quick test script for TSP algorithms
Run this before launching the full app to verify everything works
"""

import sys
sys.path.append('.')

from src.utils.geocoding import load_addresses, load_warehouse, addresses_to_locations
from src.utils.helpers import calculate_distance_matrix
from src.algorithms.route_optimizer import compare_routes

print("="*70)
print("TESTING TSP ALGORITHMS")
print("="*70)

# Load data
print("\n1️⃣ Loading data...")
try:
    df_addresses = load_addresses()
    warehouse = load_warehouse()
    locations = addresses_to_locations(df_addresses)
    
    # Add warehouse
    warehouse_loc = {
        'id': 0,
        'name': warehouse['name'],
        'address': warehouse['address'],
        'lat': warehouse['lat'],
        'lng': warehouse['lng'],
        'locality': 'Warehouse',
        'package_count': 0
    }
    all_locations = [warehouse_loc] + locations
    
    print(f"   ✅ Loaded {len(locations)} delivery addresses")
    print(f"   ✅ Total locations (including warehouse): {len(all_locations)}")
except Exception as e:
    print(f"   ❌ Error loading data: {e}")
    sys.exit(1)

# Calculate distance matrix
print("\n2️⃣ Calculating distance matrix...")
try:
    distance_matrix = calculate_distance_matrix(all_locations)
    print(f"   ✅ Distance matrix: {distance_matrix.shape}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Run optimization
print("\n3️⃣ Running route optimization...")
print("   This will take 5-15 seconds...")
print()

try:
    comparison = compare_routes(
        all_locations,
        distance_matrix,
        warehouse_idx=0,
        verbose=True
    )
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    
    print("\n🎉 Your algorithms are working correctly!")
    print("\nNext step: Run the Streamlit app")
    print("   streamlit run app.py")
    
except Exception as e:
    print(f"\n❌ Error during optimization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)