import streamlit as st
import numpy as np
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
import math
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# ---------------------------- CONFIG ----------------------------
st.set_page_config(page_title="ACO Delivery Optimizer", layout="centered")
st.title("🚚 Ant Colony Optimization for Delivery Routes")

# ---------------------------- CITY SETUP ----------------------------
n = st.number_input("Enter number of cities:", min_value=2, max_value=20, value=5, step=1)
city_names = []
city_coords = []

st.markdown("### 📍 Enter city names (suggest real Indian cities):")
for i in range(n):
    city = st.text_input(f"City {i+1}", key=f"city_{i}")
    if city:
        city_names.append(city)
        # Fake coordinates for demo; in practice, use geocoder or fixed dict
        city_coords.append((random.uniform(8, 35), random.uniform(68, 90)))

if len(city_coords) < n:
    st.warning("Please enter all city names.")
    st.stop()

# ---------------------------- DISTANCE MATRIX ----------------------------
def haversine(coord1, coord2):
    R = 6371
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

distance_matrix = np.array(
    [[haversine(c1, c2) for c2 in city_coords] for c1 in city_coords]
)

# ---------------------------- ACO SETUP ----------------------------
num_ants = 20
num_iterations = 100
alpha = 1  # pheromone influence
beta = 5   # distance influence
rho = 0.5  # evaporation rate
Q = 100

pheromone = np.ones_like(distance_matrix)


def tour_length(tour):
    return sum(distance_matrix[tour[i], tour[(i + 1) % len(tour)]] for i in range(len(tour)))

def run_aco():
    global pheromone
    best_tour = None
    best_length = float('inf')

    for _ in range(num_iterations):
        all_tours = []
        all_lengths = []

        for _ in range(num_ants):
            unvisited = list(range(len(city_coords)))
            tour = [unvisited.pop(random.randint(0, len(unvisited) - 1))]

            while unvisited:
                current = tour[-1]
                probs = []
                for j in unvisited:
                    tau = pheromone[current][j] ** alpha
                    eta = (1 / distance_matrix[current][j]) ** beta
                    probs.append(tau * eta)
                probs = np.array(probs)
                probs /= probs.sum()
                next_city = np.random.choice(unvisited, p=probs)
                tour.append(next_city)
                unvisited.remove(next_city)

            length = tour_length(tour)
            all_tours.append(tour)
            all_lengths.append(length)

            if length < best_length:
                best_tour, best_length = tour, length

        pheromone *= (1 - rho)
        for tour, length in zip(all_tours, all_lengths):
            for i in range(len(tour)):
                pheromone[tour[i]][tour[(i + 1) % len(tour)]] += Q / length

    return best_tour, best_length

# ---------------------------- MAPPING ----------------------------
def save_map_to_html(tour):
    fmap = folium.Map(location=city_coords[tour[0]], zoom_start=5)
    for idx in tour:
        folium.Marker(city_coords[idx], tooltip=city_names[idx]).add_to(fmap)

    path = [city_coords[i] for i in tour] + [city_coords[tour[0]]]
    folium.PolyLine(path, color="blue", weight=3).add_to(fmap)

    map_file = "map.html"
    fmap.save(map_file)
    return map_file

# ---------------------------- RUN ACO ----------------------------
if st.button("🚀 Optimize Route"):
    # Initial random tour
    random_tour = list(range(n))
    random.shuffle(random_tour)
    random_len = tour_length(random_tour)

    # ACO-optimized tour
    best_tour, best_len = run_aco()

    st.markdown(f"📍 **Initial (Random) Route Distance**: `{random_len:.2f} km`")
    st.markdown(f"✅ **Optimized Route Distance**: `{best_len:.2f} km`")

    st.write("**Initial (Random) Route Order:**")
    st.markdown(" → ".join([city_names[i] for i in random_tour]))

    st.write("**Optimized Route Order:**")
    st.markdown(" → ".join([city_names[i] for i in best_tour]))

    map_file_path = save_map_to_html(best_tour)
    with open(map_file_path, "r") as f:
        map_html = f.read()
        st.components.v1.html(map_html, height=600, width=700)

    # Bar Chart Comparison
    st.write("📊 **Distance Comparison: Initial vs Optimized Route**")
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ['Initial', 'Optimized']
    values = [random_len, best_len]
    colors = ['#ff9999', '#90ee90']
    ax.bar(labels, values, color=colors)
    ax.set_ylabel('Total Distance (km)')
    ax.set_title('Route Distance Comparison')
    for i, v in enumerate(values):
        ax.text(i, v + 1, f"{v:.2f} km", ha='center', fontweight='bold')
    st.pyplot(fig)
