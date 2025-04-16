import streamlit as st
import numpy as np
import folium
from streamlit_folium import folium_static
from math import radians, sin, cos, sqrt, atan2
import random

# City data (name: (latitude, longitude))
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
    'Lucknow': (26.8467, 80.9462)
}

st.title("🚚 Ant Colony Optimization for Delivery Routes (India)")

selected_cities = st.multiselect("Select Cities to Optimize", list(cities.keys()), default=list(cities.keys())[:6])

if len(selected_cities) < 3:
    st.warning("Please select at least 3 cities to optimize.")
    st.stop()

coords = np.array([cities[city] for city in selected_cities])
num_cities = len(coords)

# Haversine formula
def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# Build distance matrix
dist_matrix = np.zeros((num_cities, num_cities))
for i in range(num_cities):
    for j in range(num_cities):
        if i != j:
            dist_matrix[i][j] = haversine(coords[i], coords[j])
        else:
            dist_matrix[i][j] = np.inf

# ACO Parameters
alpha = 1.0
beta = 5.0
evaporation_rate = 0.5
Q = 100
num_ants = 20
num_iterations = 100

def tour_length(tour):
    return sum(dist_matrix[tour[i], tour[(i + 1) % num_cities]] for i in range(num_cities))

# ACO Algorithm
def run_aco():
    pheromone = np.ones((num_cities, num_cities))
    heuristic = 1 / (dist_matrix + 1e-10)
    best_tour = None
    best_length = float('inf')

    for _ in range(num_iterations):
        all_tours = []
        all_lengths = []

        for _ in range(num_ants):
            tour = []
            current = random.randint(0, num_cities - 1)
            tour.append(current)
            visited = set(tour)

            while len(tour) < num_cities:
                probs = []
                for j in range(num_cities):
                    if j not in visited:
                        prob = (pheromone[current][j] ** alpha) * (heuristic[current][j] ** beta)
                        probs.append((j, prob))
                total = sum(p[1] for p in probs)
                if total == 0:
                    next_city = random.choice([p[0] for p in probs])
                else:
                    r = random.uniform(0, total)
                    upto = 0
                    for city, prob in probs:
                        if upto + prob >= r:
                            next_city = city
                            break
                        upto += prob
                tour.append(next_city)
                visited.add(next_city)
                current = next_city

            length = tour_length(tour)
            if length < best_length:
                best_length = length
                best_tour = tour
            all_tours.append(tour)
            all_lengths.append(length)

        pheromone *= (1 - evaporation_rate)
        for tour, length in zip(all_tours, all_lengths):
            deposit = Q / length
            for i in range(num_cities):
                a, b = tour[i], tour[(i + 1) % num_cities]
                pheromone[a][b] += deposit
                pheromone[b][a] += deposit

    return best_tour, best_length

if st.button("🚀 Optimize Routes"):
    best_tour, best_length = run_aco()

    # Initial route
    initial_tour = list(range(num_cities))
    initial_length = tour_length(initial_tour)

    st.markdown(f"**Initial Total Distance**: {initial_length:.2f} km")
    st.markdown(f"**Optimized Total Distance**: {best_length:.2f} km")
    st.markdown(f"**Distance Saved**: {initial_length - best_length:.2f} km")

    # Map
    m = folium.Map(location=np.mean(coords, axis=0).tolist(), zoom_start=5)

    def plot_route(tour, color, label):
        path = [coords[i] for i in tour] + [coords[tour[0]]]
        folium.PolyLine(locations=path, color=color, weight=4, tooltip=label).add_to(m)
        for i in tour:
            folium.Marker(location=coords[i], popup=selected_cities[i]).add_to(m)

    plot_route(initial_tour, 'red', 'Before Optimization')
    plot_route(best_tour, 'green', 'After ACO')

    folium_static(m)
