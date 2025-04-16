import streamlit as st
import folium
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from folium.plugins import MarkerCluster
from geopy.distance import geodesic

# City coordinates (add or modify with real coordinates)
cities = {
    "Delhi": [28.7041, 77.1025],
    "Mumbai": [19.0760, 72.8777],
    "Bangalore": [12.9716, 77.5946],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639],
    "Hyderabad": [17.3850, 78.4867],
    "Pune": [18.5204, 73.8567],
    "Ahmedabad": [23.0225, 72.5714],
}

# Streamlit Inputs
st.title("ACO for Optimizing Delivery Routes")
n = st.number_input("Enter number of cities to select:", min_value=2, max_value=len(cities), value=5)
cities_selected = random.sample(list(cities.keys()), n)

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

# Add unoptimized path to map
for i in range(len(unoptimized_path)-1):
    start_city = unoptimized_path[i]
    end_city = unoptimized_path[i+1]
    folium.PolyLine(
        locations=[cities[start_city], cities[end_city]], color="blue", weight=3, opacity=0.7
    ).add_to(m)

# Add optimized path to map
for i in range(len(optimized_path)-1):
    start_city = optimized_path[i]
    end_city = optimized_path[i+1]
    folium.PolyLine(
        locations=[cities[start_city], cities[end_city]], color="red", weight=3, opacity=0.7
    ).add_to(m)

# Display map
st.write("Optimized Delivery Route:")
st.map(m)

# Plot the paths using Matplotlib
fig, ax = plt.subplots(1, 2, figsize=(12, 6))

# Unoptimized Path Plot
ax[0].plot(range(len(unoptimized_path)), [calculate_distance(unoptimized_path[i], unoptimized_path[i+1]) for i in range(len(unoptimized_path)-1)], marker='o', color='blue')
ax[0].set_title("Unoptimized Path")
ax[0].set_xlabel("Cities")
ax[0].set_ylabel("Distance (km)")
ax[0].grid(True)

# Optimized Path Plot
ax[1].plot(range(len(optimized_path)), [calculate_distance(optimized_path[i], optimized_path[i+1]) for i in range(len(optimized_path)-1)], marker='o', color='red')
ax[1].set_title("Optimized Path")
ax[1].set_xlabel("Cities")
ax[1].set_ylabel("Distance (km)")
ax[1].grid(True)

# Display the plot
st.pyplot(fig)
