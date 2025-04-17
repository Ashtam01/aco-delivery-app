import streamlit as st
import folium
from geopy.distance import geodesic
from folium.plugins import MarkerCluster
import random
import pandas as pd

st.set_page_config(layout="wide")
st.title("🚚 Delivery Route Optimization using Ant Colony Optimization (ACO)")

# -----------------------------
# Upload Amazon Locations CSV
# -----------------------------
uploaded_file = st.file_uploader("Upload Amazon Locations CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if not {'Location', 'Latitude', 'Longitude'}.issubset(df.columns):
        st.error("CSV must contain 'Location', 'Latitude', and 'Longitude' columns.")
    else:
        cities = {row['Location']: (row['Latitude'], row['Longitude']) for _, row in df.iterrows()}

        # Step 1: Number of locations
        n = st.number_input("Enter number of locations to include (Min: 3)", min_value=3, max_value=len(cities), value=4)

        # Step 2: Start & End Location
        location_names = list(cities.keys())
        start_city = st.selectbox("Select the Start Location", location_names)
        end_city = st.selectbox("Select the End Location", [c for c in location_names if c != start_city])

        # Step 3: Intermediate Locations
        remaining = [c for c in location_names if c not in [start_city, end_city]]
        num_intermediate = n - 2
        intermediate_cities = st.multiselect(
            f"Select {num_intermediate} Intermediate Locations",
            options=remaining,
            max_selections=num_intermediate
        )

        # Speed input
        speed = st.number_input("Enter average delivery speed (km/h)", min_value=10, max_value=150, value=60)

        if len(intermediate_cities) != num_intermediate:
            st.warning(f"Please select exactly {num_intermediate} intermediate locations.")
        else:
            full_city_list = [start_city] + intermediate_cities + [end_city]

            def calculate_distance(city1, city2):
                return geodesic(cities[city1], cities[city2]).km

            def total_distance(path):
                return sum(calculate_distance(path[i], path[i + 1]) for i in range(len(path) - 1))

            def total_time(distance):
                return distance / speed

            # ACO Algorithm
            def aco_optimize(city_list, iterations=150, ants=30, alpha=1, beta=5, rho=0.5):
                n = len(city_list)
                dist = [[calculate_distance(city_list[i], city_list[j]) for j in range(n)] for i in range(n)]
                pheromone = [[1.0 for _ in range(n)] for _ in range(n)]

                def probability(i, visited):
                    probs = []
                    for j in range(n):
                        if j not in visited:
                            tau = pheromone[i][j] ** alpha
                            eta = (1.0 / dist[i][j]) ** beta if dist[i][j] > 0 else 0
                            probs.append((j, tau * eta))
                    total = sum(p for _, p in probs)
                    return [(j, p / total) for j, p in probs] if total > 0 else []

                best_path = None
                best_length = float('inf')

                for _ in range(iterations):
                    all_paths = []
                    for _ in range(ants):
                        path = [0]
                        while len(path) < n - 1:
                            probs = probability(path[-1], path)
                            if not probs:
                                break
                            next_city = random.choices([x[0] for x in probs], weights=[x[1] for x in probs])[0]
                            path.append(next_city)
                        path.append(n - 1)
                        length = sum(dist[path[i]][path[i + 1]] for i in range(len(path) - 1))
                        all_paths.append((path, length))
                        if length < best_length:
                            best_path = path
                            best_length = length
                    # Pheromone evaporation
                    for i in range(n):
                        for j in range(n):
                            pheromone[i][j] *= (1 - rho)
                    # Pheromone update
                    for path, length in all_paths:
                        for i in range(len(path) - 1):
                            pheromone[path[i]][path[i + 1]] += 1.0 / length

                return [city_list[i] for i in best_path], best_length

            # Unoptimized path
            unoptimized_path = full_city_list
            unoptimized_distance = total_distance(unoptimized_path)
            unoptimized_time = total_time(unoptimized_distance)

            # Optimized path
            optimized_path, optimized_distance = aco_optimize(full_city_list)
            optimized_time = total_time(optimized_distance)

            # Results
            st.subheader("📊 Route Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Unoptimized Path:**")
                st.write(" ➡️ ".join(unoptimized_path))
                st.write(f"Distance: `{unoptimized_distance:.2f}` km")
                st.write(f"Estimated Time: `{unoptimized_time:.2f}` hours")
            with col2:
                st.markdown("**Optimized Path (ACO):**")
                st.write(" ➡️ ".join(optimized_path))
                st.write(f"Distance: `{optimized_distance:.2f}` km")
                st.write(f"Estimated Time: `{optimized_time:.2f}` hours")

            # Map
            m = folium.Map(location=cities[start_city], zoom_start=5)
            marker_cluster = MarkerCluster().add_to(m)

            for city in full_city_list:
                folium.Marker(location=cities[city], popup=city).add_to(marker_cluster)

            for i in range(len(unoptimized_path) - 1):
                folium.PolyLine(
                    [cities[unoptimized_path[i]], cities[unoptimized_path[i + 1]]],
                    color="red", weight=2.5, opacity=0.6
                ).add_to(m)

            for i in range(len(optimized_path) - 1):
                folium.PolyLine(
                    [cities[optimized_path[i]], cities[optimized_path[i + 1]]],
                    color="blue", weight=3, opacity=0.8
                ).add_to(m)

            st.subheader("🗺️ Route Visualization (Red = Unoptimized, Blue = Optimized)")
            st.components.v1.html(m._repr_html_(), height=600, scrolling=True)
