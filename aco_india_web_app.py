import streamlit as st
import folium
from geopy.distance import geodesic
from folium.plugins import MarkerCluster
import random

# -----------------------------
# City coordinates dictionary
# -----------------------------
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
    'Nashik': (19.9975, 73.7900),
    'Faridabad': (28.4089, 77.3178),
    'Meerut': (28.9845, 77.7060),
    'Kochi': (9.9312, 76.2673),
    'Jabalpur': (23.1815, 79.9500),
    'Mysore': (12.2958, 76.6394),
    'Agartala': (23.8315, 91.2868),
    'Udaipur': (24.5854, 73.7125),
    'Navi Mumbai': (19.0330, 73.0297),
    'Jammu': (32.7338, 74.8656),
    'Srinagar': (34.0836, 74.7973),
    'Chandigarh': (30.7333, 76.7794),
    'Noida': (28.5355, 77.3910),
    'Ghaziabad': (28.6610, 77.4419),
    'Rajkot': (22.3039, 70.8022),
    'Chandrapur': (19.9493, 79.2972),
    'Dhanbad': (23.8007, 86.4347),
    'Kolhapur': (16.7057, 74.2433),
    'Haldia': (22.0700, 88.0970),
    'Mangalore': (12.9141, 74.8560),
    'Tiruchirappalli': (10.7900, 78.7045),
    'Madhurai': (9.9196, 78.1198),
    'Jammu': (32.7338, 74.8656),
    'Bhubaneswar': (20.2961, 85.8189),
    'Gwalior': (26.2183, 78.1828),
    'Shimla': (31.1048, 77.1700),
    'Dehradun': (30.3165, 78.0322),
    'Raigarh': (21.8775, 83.0963),
    'Bikaner': (28.0228, 73.3114),
    'Patiala': (30.3408, 76.3857),
    'Kurnool': (15.8281, 78.0473),
    'Aligarh': (27.8974, 78.0842),
    'Bilaspur': (22.0777, 82.1470),
    'Bhubaneshwar': (20.2961, 85.8189),
    'Muzaffarpur': (26.1206, 85.3583),
    'Bokaro': (23.6263, 86.1517),
    'Ajmer': (26.4499, 74.6389),
    'Kota': (25.1820, 75.8648)
}

st.set_page_config(layout="wide")
st.title("🚚 Delivery Route Optimization using Ant Colony Optimization (ACO)")



# Step 1: Number of cities
n = st.number_input("Enter number of cities to include (Min: 3)", min_value=3, max_value=len(cities), value=4)

# Step 2: Start & End City
city_names = list(cities.keys())
start_city = st.selectbox("Select the Start City", city_names)
end_city = st.selectbox("Select the End City", [c for c in city_names if c != start_city])

# Step 3: Intermediate Cities
remaining_cities = [c for c in city_names if c not in [start_city, end_city]]
num_intermediate = n - 2
intermediate_cities = st.multiselect(
    f"Select {num_intermediate} Intermediate Cities",
    options=remaining_cities,
    max_selections=num_intermediate
)

# Speed input
speed = st.number_input("Enter average delivery speed (km/h)", min_value=10, max_value=150, value=60)

if len(intermediate_cities) != num_intermediate:
    st.warning(f"Please select exactly {num_intermediate} intermediate cities.")
else:
    full_city_list = [start_city] + intermediate_cities + [end_city]

    def calculate_distance(city1, city2):
        return geodesic(cities[city1], cities[city2]).km

    def total_distance(path):
        return sum(calculate_distance(path[i], path[i + 1]) for i in range(len(path) - 1))

    def total_time(distance):
        return distance / speed  # in hours

    # --------------------------
    # ACO Algorithm
    # --------------------------
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

    # Unoptimized route
    unoptimized_path = full_city_list
    unoptimized_distance = total_distance(unoptimized_path)
    unoptimized_time = total_time(unoptimized_distance)

    # Optimized route
    optimized_path, optimized_distance = aco_optimize(full_city_list)
    optimized_time = total_time(optimized_distance)

    # --------------------------
    # Display Results
    # --------------------------
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

    # --------------------------
    # Map Visualization
    # --------------------------
    m = folium.Map(location=cities[start_city], zoom_start=5)
    marker_cluster = MarkerCluster().add_to(m)

    for city in full_city_list:
        folium.Marker(location=cities[city], popup=city).add_to(marker_cluster)

    # Unoptimized path in RED
    for i in range(len(unoptimized_path) - 1):
        folium.PolyLine(
            [cities[unoptimized_path[i]], cities[unoptimized_path[i + 1]]],
            color="red", weight=2.5, opacity=0.6
        ).add_to(m)

    # Optimized path in BLUE
    for i in range(len(optimized_path) - 1):
        folium.PolyLine(
            [cities[optimized_path[i]], cities[optimized_path[i + 1]]],
            color="blue", weight=3, opacity=0.8
        ).add_to(m)

    st.subheader("🗺️ Route Visualization (Red = Unoptimized, Blue = Optimized)")
    st.components.v1.html(m._repr_html_(), height=600, scrolling=True)
