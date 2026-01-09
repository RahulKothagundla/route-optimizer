"""
Smart Delivery Route Optimizer
Day 2: TSP Algorithms & Route Optimization

Author: Rahul Kothagundla
GitHub: https://github.com/RahulKothagundla/route-optimizer
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Import our utilities
from src.utils.geocoding import (
    load_addresses, 
    load_warehouse, 
    addresses_to_locations,
    get_locality_summary,
    get_bounding_box,
    get_distance_statistics
)
from src.utils.helpers import (
    haversine_distance,
    calculate_distance_matrix,
    format_time,
    calculate_fuel_cost
)

# Import algorithms (NEW!)
from src.algorithms.route_optimizer import (
    optimize_route,
    compare_routes,
    get_route_coordinates
)

# Page configuration
st.set_page_config(
    page_title="Route Optimizer - Day 2",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
    border-radius: 10px; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0;">🚚 Smart Route Optimizer</h1>
    <p style="color: #f0f0f0; margin: 0.5rem 0 0 0;">Day 2: TSP Algorithms & Optimization</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Project Info")
    st.markdown("""
    **Day 2 Goals:**
    - ✅ Nearest Neighbor TSP
    - ✅ 2-Opt Optimization
    - ✅ Route Comparison
    - ✅ Visual Before/After
    - ✅ Metrics Dashboard
    
    **Algorithms:**
    - Nearest Neighbor (Greedy)
    - 2-Opt (Local Search)
    
    **Expected:**
    - 30-35% distance reduction
    """)
    
    st.divider()
    
    st.markdown("""
    **GitHub:**  
    [RahulKothagundla/route-optimizer](https://github.com/RahulKothagundla/route-optimizer)
    """)

# Main content
try:
    # Load data
    with st.spinner("Loading data..."):
        df_addresses = load_addresses()
        warehouse = load_warehouse()
        locations = addresses_to_locations(df_addresses)
        
        # Add warehouse as first location
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
        
        # Calculate distance matrix (cache it)
        if 'distance_matrix' not in st.session_state:
            st.session_state.distance_matrix = calculate_distance_matrix(all_locations)
        
        distance_matrix = st.session_state.distance_matrix
    
    st.success(f"✅ Loaded {len(locations)} delivery addresses and calculated distance matrix")
    
    # Display tabs (NEW: Route Optimizer tab added)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Overview", 
        "🗺️ Map View", 
        "📊 Statistics", 
        "🧮 Distance Calculator",
        "🚀 Route Optimizer"  # NEW!
    ])
    
    # TAB 1: Overview (same as before)
    with tab1:
        st.header("📍 Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Addresses", len(locations))
        
        with col2:
            total_packages = df_addresses['package_count'].sum()
            st.metric("Total Packages", total_packages)
        
        with col3:
            localities = df_addresses['locality'].nunique()
            st.metric("Localities", localities)
        
        with col4:
            bbox = get_bounding_box(locations)
            area_coverage = (bbox['lat_max'] - bbox['lat_min']) * (bbox['lng_max'] - bbox['lng_min'])
            st.metric("Coverage Area", f"{area_coverage*100:.1f} km²")
        
        st.divider()
        
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.subheader("🏭 Warehouse")
            st.write(f"**Name:** {warehouse['name']}")
            st.write(f"**Address:** {warehouse['address']}")
            st.write(f"**Coordinates:** ({warehouse['lat']:.4f}, {warehouse['lng']:.4f})")
        
        with col_b:
            st.subheader("📦 Locality Distribution")
            locality_summary = get_locality_summary(df_addresses)
            
            fig = px.bar(
                locality_summary.reset_index(),
                x='locality',
                y='num_addresses',
                title='Delivery Addresses by Locality',
                labels={'num_addresses': 'Number of Addresses', 'locality': 'Locality'},
                color='num_addresses',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        st.subheader("📋 Address Details")
        st.dataframe(
            df_addresses[['id', 'customer_name', 'address', 'locality', 'package_count', 'lat', 'lng']],
            height=300,
            use_container_width=True
        )
    
    # TAB 2: Map View (same as before)
    with tab2:
        st.header("🗺️ Interactive Map")

        if "main_map_html" not in st.session_state:
            bbox = get_bounding_box(locations)

            m = folium.Map(
                location=[bbox["center_lat"], bbox["center_lng"]],
                zoom_start=12,
                tiles="OpenStreetMap",
                control_scale=True
            )

            folium.Marker(
                location=[warehouse["lat"], warehouse["lng"]],
                popup=f"<b>{warehouse['name']}</b><br>{warehouse['address']}",
                tooltip="Warehouse",
                icon=folium.Icon(color="red", icon="home")
            ).add_to(m)

            locality_colors = {
                "Madhapur": "blue",
                "Gachibowli": "green",
                "Kondapur": "purple",
                "Kukatpally": "orange"
            }

            for loc in locations:
                folium.CircleMarker(
                    location=[loc["lat"], loc["lng"]],
                    radius=6,
                    color=locality_colors.get(loc["locality"], "gray"),
                    fill=True,
                    fill_color=locality_colors.get(loc["locality"], "gray"),
                    fill_opacity=0.7,
                    tooltip=f"{loc['locality']} - {loc['package_count']} pkg",
                    popup=f"<b>{loc['name']}</b><br>{loc['address']}"
                ).add_to(m)

            st.session_state.main_map_html = m._repr_html_()

        left, mid, right = st.columns([1, 3, 1])
        with mid:
            st.components.v1.html(
                st.session_state.main_map_html,
                height=440
            )

        st.markdown("#### Map Legend")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown("🔴 **Warehouse**")
        c2.markdown("🔵 **Madhapur**")
        c3.markdown("🟢 **Gachibowli**")
        c4.markdown("🟣 **Kondapur**")
        c5.markdown("🟠 **Kukatpally**")
    
    # TAB 3: Statistics (same as before)
    with tab3:
        st.header("📊 Detailed Statistics")
        
        dist_stats = get_distance_statistics(df_addresses, warehouse)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.metric("Nearest Address", f"{dist_stats['min_distance_km']} km")
        
        with col_s2:
            st.metric("Farthest Address", f"{dist_stats['max_distance_km']} km")
        
        with col_s3:
            st.metric("Average Distance", f"{dist_stats['avg_distance_km']} km")
        
        st.divider()
        
        st.subheader("📍 By Locality")
        
        locality_summary = get_locality_summary(df_addresses)
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            fig_pie = px.pie(
                locality_summary.reset_index(),
                values='num_addresses',
                names='locality',
                title='Address Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_t2:
            fig_bar = px.bar(
                locality_summary.reset_index(),
                x='locality',
                y='total_packages',
                title='Package Distribution',
                labels={'total_packages': 'Total Packages'},
                color='total_packages',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.subheader("📋 Locality Summary Table")
        
        locality_summary_display = locality_summary.copy()
        locality_summary_display['avg_packages_per_address'] = (
            locality_summary_display['total_packages'] / locality_summary_display['num_addresses']
        ).round(2)
        
        st.dataframe(
            locality_summary_display,
            use_container_width=True
        )
    
    # TAB 4: Distance Calculator (same as before)
    with tab4:
        st.header("🧮 Distance Calculator")
        st.markdown("Calculate distance and costs between any two locations")

        if "distance_calc" not in st.session_state:
            st.session_state.distance_calc = None

        col_calc1, col_calc2 = st.columns(2)

        with col_calc1:
            st.subheader("From:")
            from_type = st.radio("Select start point:", ["Warehouse", "Delivery Address"])

            if from_type == "Warehouse":
                from_lat = warehouse['lat']
                from_lng = warehouse['lng']
                from_name = warehouse['name']
            else:
                from_options = [f"{loc['id']}: {loc['name']} ({loc['locality']})" for loc in locations]
                from_selected = st.selectbox("Select address:", from_options)
                from_id = int(from_selected.split(":")[0])
                from_loc = next(loc for loc in locations if loc['id'] == from_id)
                from_lat = from_loc['lat']
                from_lng = from_loc['lng']
                from_name = from_loc['name']

        with col_calc2:
            st.subheader("To:")
            to_type = st.radio("Select end point:", ["Delivery Address", "Warehouse"], key="to")

            if to_type == "Warehouse":
                to_lat = warehouse['lat']
                to_lng = warehouse['lng']
                to_name = warehouse['name']
            else:
                to_options = [f"{loc['id']}: {loc['name']} ({loc['locality']})" for loc in locations]
                to_selected = st.selectbox("Select address:", to_options, key="to_select")
                to_id = int(to_selected.split(":")[0])
                to_loc = next(loc for loc in locations if loc['id'] == to_id)
                to_lat = to_loc['lat']
                to_lng = to_loc['lng']
                to_name = to_loc['name']

        if st.button("Calculate", type="primary"):
            distance = haversine_distance(from_lat, from_lng, to_lat, to_lng)
            fuel_cost = calculate_fuel_cost(distance)

            avg_speed = 35
            time_hours = distance / avg_speed
            co2 = (distance / 12) * 2.31

            st.session_state.distance_calc = {
                "distance": distance,
                "fuel_cost": fuel_cost,
                "time_hours": time_hours,
                "co2": co2,
                "from": (from_lat, from_lng, from_name),
                "to": (to_lat, to_lng, to_name)
            }

        if st.session_state.distance_calc:
            result = st.session_state.distance_calc

            st.divider()
            st.success("✅ Calculation Complete")

            col_r1, col_r2, col_r3, col_r4 = st.columns(4)

            with col_r1:
                st.metric("Distance", f"{result['distance']:.2f} km")

            with col_r2:
                st.metric("Estimated Time", format_time(result['time_hours']))

            with col_r3:
                st.metric("Fuel Cost", f"₹{result['fuel_cost']:.2f}")

            with col_r4:
                st.metric("CO₂ Emissions", f"{result['co2']:.2f} kg")

            st.subheader("Route Preview")

            mini_map = folium.Map(
                location=[
                    (result['from'][0] + result['to'][0]) / 2,
                    (result['from'][1] + result['to'][1]) / 2
                ],
                zoom_start=13
            )

            folium.Marker(
                [result['from'][0], result['from'][1]],
                popup=result['from'][2],
                tooltip="Start",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(mini_map)

            folium.Marker(
                [result['to'][0], result['to'][1]],
                popup=result['to'][2],
                tooltip="End",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(mini_map)

            folium.PolyLine(
                locations=[
                    [result['from'][0], result['from'][1]],
                    [result['to'][0], result['to'][1]]
                ],
                color='blue',
                weight=3,
                opacity=0.7
            ).add_to(mini_map)

            left, mid, right = st.columns([1, 2, 1])
            with mid:
                st_folium(mini_map, height=400, width=650)
    
    # TAB 5: ROUTE OPTIMIZER (NEW!)
    with tab5:
        st.header("🚀 Route Optimizer")
        st.markdown("Compare naive vs optimized delivery routes using TSP algorithms")
        
        # Optimization controls
        col_opt1, col_opt2, col_opt3 = st.columns([2, 1, 1])
        
        with col_opt1:
            st.markdown("### 🎯 Optimization Settings")
        
        with col_opt2:
            if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
                with st.spinner("Running optimization algorithms..."):
                    comparison = compare_routes(
                        all_locations,
                        distance_matrix,
                        warehouse_idx=0,
                        verbose=False
                    )
                    st.session_state.route_comparison = comparison
                    st.success("✅ Optimization complete!")
        
        with col_opt3:
            if st.button("🗑️ Clear Results"):
                if 'route_comparison' in st.session_state:
                    del st.session_state.route_comparison
                st.rerun()
        
        # Display results if available
        if 'route_comparison' in st.session_state:
            comp = st.session_state.route_comparison
            
            st.divider()
            
            # KEY METRICS
            st.subheader("📊 Key Metrics")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            naive_dist = comp['distances']['naive']
            opt_dist = comp['distances']['optimized']
            saved_km = comp['improvements']['opt_vs_naive']['km_saved']
            saved_pct = comp['improvements']['opt_vs_naive']['percent']
            
            with col_m1:
                st.metric("Naive Route", f"{naive_dist:.2f} km")
            
            with col_m2:
                st.metric("Optimized Route", f"{opt_dist:.2f} km")
            
            with col_m3:
                st.metric("Distance Saved", f"{saved_km:.2f} km", 
                         delta=f"-{saved_pct:.1f}%",
                         delta_color="inverse")
            
            with col_m4:
                fuel_saved = calculate_fuel_cost(saved_km)
                st.metric("Fuel Cost Saved", f"₹{fuel_saved:.2f}")
            
            st.divider()
            
            # COMPARISON TABLE
            st.subheader("📋 Route Comparison")
            
            comparison_data = {
                'Metric': ['Distance (km)', 'Estimated Time', 'Fuel Cost (₹)', 'CO₂ Emissions (kg)'],
                'Naive Route': [
                    f"{naive_dist:.2f}",
                    format_time(naive_dist / 35),
                    f"₹{calculate_fuel_cost(naive_dist):.2f}",
                    f"{(naive_dist / 12) * 2.31:.2f}"
                ],
                'Optimized Route': [
                    f"{opt_dist:.2f}",
                    format_time(opt_dist / 35),
                    f"₹{calculate_fuel_cost(opt_dist):.2f}",
                    f"{(opt_dist / 12) * 2.31:.2f}"
                ],
                'Improvement': [
                    f"{saved_km:.2f} km ({saved_pct:.1f}%)",
                    format_time((naive_dist - opt_dist) / 35),
                    f"₹{fuel_saved:.2f}",
                    f"{((naive_dist - opt_dist) / 12) * 2.31:.2f} kg"
                ]
            }
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # VISUAL COMPARISON
            st.subheader("📈 Visual Comparison")
            
            # Bar chart
            fig_comparison = go.Figure(data=[
                go.Bar(name='Naive Route', x=['Distance', 'Time', 'Cost'], 
                      y=[naive_dist, naive_dist/35*60, calculate_fuel_cost(naive_dist)],
                      marker_color='#ff6b6b'),
                go.Bar(name='Optimized Route', x=['Distance', 'Time', 'Cost'],
                      y=[opt_dist, opt_dist/35*60, calculate_fuel_cost(opt_dist)],
                      marker_color='#51cf66')
            ])
            
            fig_comparison.update_layout(
                title='Naive vs Optimized Comparison',
                yaxis_title='Value',
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            st.divider()
            
            # ROUTE VISUALIZATION
            st.subheader("🗺️ Route Visualization")
            
            col_v1, col_v2 = st.columns(2)
            
            # Naive route map
            with col_v1:
                st.markdown("**Naive Route (Sequential)**")
                
                naive_route = comp['routes']['naive']['route']
                naive_coords = get_route_coordinates(naive_route, all_locations)
                
                bbox = get_bounding_box(all_locations)
                map_naive = folium.Map(
                    location=[bbox["center_lat"], bbox["center_lng"]],
                    zoom_start=11
                )
                
                # Draw route
                folium.PolyLine(
                    naive_coords,
                    color='red',
                    weight=3,
                    opacity=0.7,
                    popup=f"Naive Route: {naive_dist:.2f} km"
                ).add_to(map_naive)
                
                # Add markers
                for i, coord in enumerate(naive_coords):
                    if i == 0:
                        icon = folium.Icon(color='red', icon='home')
                        folium.Marker(coord, icon=icon, tooltip="Warehouse").add_to(map_naive)
                    elif i == len(naive_coords) - 1:
                        pass  # Skip the return to warehouse
                    else:
                        folium.CircleMarker(coord, radius=4, color='red', fill=True).add_to(map_naive)
                
                st_folium(map_naive, height=400, width=None)
            
            # Optimized route map
            with col_v2:
                st.markdown("**Optimized Route (TSP)**")
                
                opt_route = comp['routes']['optimized']['route']
                opt_coords = get_route_coordinates(opt_route, all_locations)
                
                map_opt = folium.Map(
                    location=[bbox["center_lat"], bbox["center_lng"]],
                    zoom_start=11
                )
                
                # Draw route
                folium.PolyLine(
                    opt_coords,
                    color='green',
                    weight=3,
                    opacity=0.7,
                    popup=f"Optimized Route: {opt_dist:.2f} km"
                ).add_to(map_opt)
                
                # Add markers
                for i, coord in enumerate(opt_coords):
                    if i == 0:
                        icon = folium.Icon(color='red', icon='home')
                        folium.Marker(coord, icon=icon, tooltip="Warehouse").add_to(map_opt)
                    elif i == len(opt_coords) - 1:
                        pass
                    else:
                        folium.CircleMarker(coord, radius=4, color='green', fill=True).add_to(map_opt)
                
                st_folium(map_opt, height=400, width=None)
            
            st.divider()
            
            # ALGORITHM DETAILS
            with st.expander("🔬 Algorithm Details"):
                st.markdown("### Algorithms Used")
                
                st.markdown("**1. Nearest Neighbor (Greedy Heuristic)**")
                st.code("""
Algorithm:
1. Start at warehouse
2. Visit nearest unvisited location
3. Repeat until all visited
4. Return to warehouse

Time: O(n²)
Result: ~20-30% better than random
                """)
                
                st.markdown("**2. 2-Opt Optimization (Local Search)**")
                st.code("""
Algorithm:
1. Start with Nearest Neighbor solution
2. Try swapping edge pairs
3. Keep swaps that reduce distance
4. Repeat until no improvement

Time: O(n² × iterations)
Result: 20-40% improvement over NN
                """)
                
                if 'optimization_stats' in comp['routes']['optimized']:
                    stats = comp['routes']['optimized']['optimization_stats']
                    st.markdown("### Optimization Statistics")
                    st.write(f"- **Iterations:** {stats['iterations']}")
                    st.write(f"- **Improvements found:** {stats['total_improvements']}")
                    st.write(f"- **Improvement:** {stats['improvement_pct']:.1f}%")
        
        else:
            st.info("👆 Click 'Run Optimization' to compare routes!")
            
            st.markdown("""
            ### What will happen:
            
            1. **Naive Route Generation**
               - Visits addresses in sequential order (1, 2, 3, ...)
               - Baseline for comparison
            
            2. **Nearest Neighbor Algorithm**
               - Greedy approach: always go to nearest unvisited location
               - Fast and gives good initial solution
            
            3. **2-Opt Optimization**
               - Improves Nearest Neighbor solution
               - Uncrosses routes to reduce distance
               - Converges to local optimum
            
            4. **Results**
               - Expected: **30-35% distance reduction**
               - Metrics: Distance, Time, Fuel Cost, CO₂
               - Visual comparison of routes
            """)

except FileNotFoundError as e:
    st.error(f"❌ Error loading data: {e}")
    st.info("Make sure `data/hyderabad_addresses.csv` and `data/warehouse.json` exist!")

except Exception as e:
    st.error(f"❌ An error occurred: {e}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🚚 Smart Route Optimizer | Day 2: TSP Algorithms Complete ✅</p>
    <p>Built with ❤️ by Rahul Kothagundla | 
    <a href="https://github.com/RahulKothagundla/route-optimizer">GitHub</a></p>
</div>
""", unsafe_allow_html=True)