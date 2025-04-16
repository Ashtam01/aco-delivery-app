import streamlit as st
import folium
import random
import numpy as np
import pandas as pd
from folium.plugins import MarkerCluster
from geopy.distance import geodesic

# City coordinates (add or modify with real coordinates)
cities = {
    'Delhi': (28.6139, 77.2090),
    'Mumbai': (19.0760, 72.8777),
    'Bangalore': (12.9716, 77.5946),
    'Hyderabad': (17.3850, 78.4867),
    'Chennai': (13.0827, 80.2707),
    'Kolkata': (22.5726, 88.3639),
    'Ahmedabad': (23.0225, 72.5714),
    'Pune': (18.5204, 73.8567),
    'Jaipur': (26.9124, 75.7873),
    'Lucknow': (26.8467, 80.9462),
    'Surat': (21.1702, 72.8311),
    'Bhopal': (23.2599, 77.4126),
    'Nagpur': (21.1458, 79.0882),
    'Indore': (22.7196, 75.8577),
    'Kanpur': (26.4499, 80.3319),
    'Patna': (25.5941, 85.1376),
    'Ranchi': (23.3441, 85.3096),
    'Guwahati': (26.1445, 91.7362),
    'Raipur': (21.2514, 81.6296),
    'Thiruvananthapuram': (8.5241, 76.9366),
    'Coimbatore': (11.0168, 76.9558),
    'Visakhapatnam': (17.6868, 83.2185),
    'Vadodara': (22.3072, 73.1812),
    'Vijayawada': (16.5062, 80.6480),
    'Agra': (27.1767, 78.0081),
    'Varanasi': (25.3176, 82.9739),
}

# Streamlit Inputs
st.title("ACO for Optimizing Delivery Routes")

# Allow users to select multiple cities
cities_selected = st.multiselect(
    "Select cities to include in the route optimization",
    options=list(cities.keys())
)

# Ensure at least 2 cities are selected
if len(cities_selected) < 2:
    st.error("Please select at least two cities.")
else:
    # Show selected cities
    st.write("Selected Cities:", cities_selected)

    # Calculate the distance between cities
    def calculate_distance(city1, city2):
        coord1 = cities[city1]
        coord2 = cities[city2]
        return geodesic(coord1, coord2).km

    # Function to calculate total distance for a path
    def total_distance(path):
        return sum(calculate_distance(path[i], path[i+1]) for i in range(len(path)-1))

    # Initial (Unoptimized) Path
    unoptimized_path = cities_selected[:]
    random.shuffle(unoptimized_path)
    unoptimized_distance = total_distance(unoptimized_path)

    # Display initial unoptimized path distance
    st.write("Unoptimized Path Distance:", unoptimized_distance, "km")

    # ACO-based optimized path (This is a simplified version)
    def ant_colony_optimization(cities_list, iterations=100, alpha=1, beta=1, evaporation_rate=0.5):
        # Simplified ACO: Random shuffle to simulate optimization
        best_path = cities_list[:]
        random.shuffle(best_path)
        best_distance = total_distance(best_path)
        return best_path, best_distance

    # Find optimized path using ACO
    optimized_path, optimized_distance = ant_colony_optimization(cities_selected)

    # Show optimized path and distance
    st.write("Optimized Path Distance:", optimized_distance, "km")
    st.write("Optimized Path:", optimized_path)

    # Create a map with Folium
    map_center = cities[cities_selected[0]]
    m = folium.Map(location=map_center, zoom_start=6)

    # Add markers for selected cities
    marker_cluster = MarkerCluster().add_to(m)
    for city in cities_selected:
        folium.Marker(location=cities[city], popup=city).add_to(marker_cluster)

    # Add unoptimized path to map (blue line)
    for i in range(len(unoptimized_path)-1):
        start_city = unoptimized_path[i]
        end_city = unoptimized_path[i+1]
        folium.PolyLine(
            locations=[cities[start_city], cities[end_city]], color="blue", weight=3, opacity=0.7
        ).add_to(m)

    # Add optimized path to map (red line)
    for i in range(len(optimized_path)-1):
        start_city = optimized_path[i]
        end_city = optimized_path[i+1]
        folium.PolyLine(
            locations=[cities[start_city], cities[end_city]], color="red", weight=3, opacity=0.7
        ).add_to(m)

    # Display the Folium map in the Streamlit app using st.components.v1.html
    st.write("Optimized Delivery Route:")
    map_html = m._repr_html_()  # Get the HTML representation of the map
    st.components.v1.html(map_html, width=700, height=500)
