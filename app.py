"""
Smart Delivery Route Optimizer
Day 1: Data Loading and Distance Calculation Testing

Author: Rahul Kothagundla
GitHub: https://github.com/RahulKothagundla/route-optimizer
"""

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

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

# Page configuration
st.set_page_config(
    page_title="Route Optimizer - Day 1",
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
    <p style="color: #f0f0f0; margin: 0.5rem 0 0 0;">Day 1: Data Loading & Distance Calculations</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Project Info")
    st.markdown("""
    **Day 1 Goals:**
    - ✅ Load 60 Hyderabad addresses
    - ✅ Load warehouse data
    - ✅ Calculate distances
    - ✅ Display on map
    - ✅ Basic statistics
    
    **Tech Stack:**
    - Python + Streamlit
    - Folium (Maps)
    - Pandas (Data)
    - Numpy (Calculations)
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
    
    st.success(f"✅ Loaded {len(locations)} delivery addresses and warehouse data")
    
    # Display tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📍 Overview", "🗺️ Map View", "📊 Statistics", "🧮 Distance Calculator"])
    
    # TAB 1: Overview
    with tab1:
        st.header("📍 Data Overview")
        
        # Key metrics
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
        
        # Warehouse info
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
        
        # Address table
        st.subheader("📋 Address Details")
        st.dataframe(
            df_addresses[['id', 'customer_name', 'address', 'locality', 'package_count', 'lat', 'lng']],
            height=300,
            use_container_width=True
        )
    
    
    # TAB 2: Map View
    with tab2:
        st.header("🗺️ Interactive Map")

        # Build map ONCE
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

            # Store rendered HTML
            st.session_state.main_map_html = m._repr_html_()

        # Centered square map (HTML render — NO iframe bug)
        left, mid, right = st.columns([1, 2, 1])
        with mid:
            st.components.v1.html(
                st.session_state.main_map_html,
                height=360
            )

        # Legend
        st.markdown("#### Map Legend")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.markdown("🔴 **Warehouse**")
        c2.markdown("🔵 **Madhapur**")
        c3.markdown("🟢 **Gachibowli**")
        c4.markdown("🟣 **Kondapur**")
        c5.markdown("🟠 **Kukatpally**")

    
    # TAB 3: Statistics
    with tab3:
        st.header("📊 Detailed Statistics")
        
        # Distance statistics
        dist_stats = get_distance_statistics(df_addresses, warehouse)
        
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.metric("Nearest Address", f"{dist_stats['min_distance_km']} km")
        
        with col_s2:
            st.metric("Farthest Address", f"{dist_stats['max_distance_km']} km")
        
        with col_s3:
            st.metric("Average Distance", f"{dist_stats['avg_distance_km']} km")
        
        st.divider()
        
        # Locality statistics
        st.subheader("📍 By Locality")
        
        locality_summary = get_locality_summary(df_addresses)
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            # Pie chart - Addresses
            fig_pie = px.pie(
                locality_summary.reset_index(),
                values='num_addresses',
                names='locality',
                title='Address Distribution',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_t2:
            # Bar chart - Packages
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
        
        # Detailed table
        st.subheader("📋 Locality Summary Table")
        
        locality_summary_display = locality_summary.copy()
        locality_summary_display['avg_packages_per_address'] = (
            locality_summary_display['total_packages'] / locality_summary_display['num_addresses']
        ).round(2)
        
        st.dataframe(
            locality_summary_display,
            use_container_width=True
        )
    
    # TAB 4: Distance Calculator
    with tab4:
        st.header("🧮 Distance Calculator")
        st.markdown("Calculate distance and costs between any two locations")

        # ---- SESSION STATE INIT (FIX) ----
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

        # ---- BUTTON STORES RESULT (FIX) ----
        if st.button("Calculate", type="primary"):
            distance = haversine_distance(from_lat, from_lng, to_lat, to_lng)
            fuel_cost = calculate_fuel_cost(distance)

            avg_speed = 35  # km/h
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

        # ---- PERSISTENT RENDER (FIX) ----
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
                st_folium(
                    mini_map,
                    height=550,
                    width = 650
                )


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
    <p>🚚 Smart Route Optimizer | Day 1: Foundation Complete ✅</p>
    <p>Built with ❤️ by Rahul Kothagundla | 
    <a href="https://github.com/RahulKothagundla/route-optimizer">GitHub</a></p>
</div>
""", unsafe_allow_html=True)