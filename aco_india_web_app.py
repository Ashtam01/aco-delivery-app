import streamlit as st
import numpy as np
import folium
import random
from streamlit_folium import st_folium
from math import radians, sin, cos, sqrt, atan2

st.title(" ACO Delivery Route Optimizer for Indian Cities 🚚")

# Full city dictionary with lat/lon
india_cities = {
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

# User input: Slider to choose how many cities to optimize
n = st.slider("How many cities to optimize (min 3):", 3, len(india_cities), 6)

# Generate random cities
selected = dict(random.sample(list(india_cities.items()), n))
coords = list(selected.values())
city_names = list(selected.keys())
num_cities = len(coords)

# Haversine distance function to calculate distance between two cities
def haversine(coord1, coord2):
    R = 6371  # Radius of Earth in kilometers
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# Distance matrix for the cities
dist_matrix = np.zeros((num_cities, num_cities))
for i in range(num_cities):
    for j in range(num_cities):
        dist_matrix[i][j] = haversine(coords[i], coords[j]) if i != j else np.inf

# ACO algorithm parameters
alpha, beta, evaporation_rate, Q = 1, 5, 0.5, 100
num_ants, num_iterations = 20, 100

def tour_length(tour):
    return sum(dist_matrix[tour[i], tour[(i + 1) % num_cities]] for i in range(num_cities))

# Ant Colony Optimization
def run_aco():
    pheromone = np.ones((num_cities, num_cities))
    heuristic = 1 / (dist_matrix + 1e-10)
    best_tour, best_length = None, float('inf')

    for _ in range(num_iterations):
        for _ in range(num_ants):
            tour = [random.randint(0, num_cities - 1)]
            while len(tour) < num_cities:
                current = tour[-1]
                probs = [(j, (pheromone[current][j] ** alpha) * (heuristic[current][j] ** beta))
                         for j in range(num_cities) if j not in tour]
                total = sum(p[1] for p in probs)
                r = random.uniform(0, total)
                acc = 0
                for city, prob in probs:
                    acc += prob
                    if acc >= r:
                        tour.append(city)
                        break
            length = tour_length(tour)
            if length < best_length:
                best_tour, best_length = tour, length
            for i in range(num_cities):
                a, b = tour[i], tour[(i + 1) % num_cities]
                pheromone[a][b] += Q / length
        pheromone *= (1 - evaporation_rate)

    return best_tour, best_length

# Run optimization when button is clicked
if st.button(" Optimize Route  🚀"):
    best_tour, best_len = run_aco()
    st.success(f"Optimized Distance: {best_len:.2f} km")
    st.write("**Optimized Route:**")
    st.markdown(" → ".join([city_names[i] for i in best_tour]))

    # Create the map
    map_center = np.mean(coords, axis=0)
    m = folium.Map(location=map_center.tolist(), zoom_start=5)

    # Add route to map
    path = [coords[i] for i in best_tour] + [coords[best_tour[0]]]
    folium.PolyLine(locations=path, color='green', weight=4).add_to(m)

    # Add markers for cities
    for i, city in enumerate(city_names):
        folium.Marker(location=coords[i], popup=city).add_to(m)

    # Show map in Streamlit
    st_folium(m, width=700, height=500)
