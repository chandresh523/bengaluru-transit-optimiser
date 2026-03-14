import os
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
from openai import OpenAI

# Load the secure key (if using .env)
load_dotenv()

# Initialize the AI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN")
)

# --- COORDINATES DICTIONARY ---
LOCATIONS = {
    "Koramangala": [12.9279, 77.6271],
    "Indiranagar": [12.9784, 77.6408],
    "HSR Layout": [12.9121, 77.6446],
    "Whitefield": [12.9698, 77.7499],
    "Christ University Central Campus": [12.9345, 77.6056],
    "Manyata Tech Park": [13.0450, 77.6200],
    "MG Road": [12.9719, 77.6010],
    "Electronic City": [12.8399, 77.6770]
}

# --- OSRM ROUTING FUNCTION ---
def get_route_geometry(start_coords, end_coords):
    # OSRM expects Longitude, Latitude
    start_lon, start_lat = start_coords[1], start_coords[0]
    end_lon, end_lat = end_coords[1], end_coords[0]
    
    # Ping the public OSRM API
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            coordinates = data['routes'][0]['geometry']['coordinates']
            # Flip [lon, lat] back to [lat, lon] for Folium
            return [[lat, lon] for lon, lat in coordinates]
    except Exception as e:
        st.error(f"Routing API failed: {e}")
    return None

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Bengaluru Transit AI", page_icon="🚦", layout="centered")

st.title("🚦 Bengaluru Transit Optimizer")
st.markdown("Powered by live traffic logic, GitHub Models, and OSRM Road Mapping.")

st.sidebar.header("Route Settings")
origin = st.sidebar.selectbox("Start Location", ["Koramangala", "Indiranagar", "HSR Layout", "Whitefield"])
destination = st.sidebar.selectbox("Destination", ["Christ University Central Campus", "Manyata Tech Park", "MG Road", "Electronic City"])
time_of_day = st.sidebar.radio("Time of Day", ["Morning Peak (8 AM - 11 AM)", "Afternoon", "Evening Peak (5 PM - 8 PM)"])

# --- MAP GENERATION ---
st.markdown("### 🗺️ Route Map")
start_coords = LOCATIONS[origin]
end_coords = LOCATIONS[destination]

mid_lat = (start_coords[0] + end_coords[0]) / 2
mid_lon = (start_coords[1] + end_coords[1]) / 2

# Create the base map
m = folium.Map(location=[mid_lat, mid_lon], zoom_start=12)

# Add markers
folium.Marker(start_coords, tooltip=f"Start: {origin}", icon=folium.Icon(color="green", icon="play")).add_to(m)
folium.Marker(end_coords, tooltip=f"End: {destination}", icon=folium.Icon(color="red", icon="stop")).add_to(m)

# Get the real road geometry from OSRM
road_path = get_route_geometry(start_coords, end_coords)

if road_path:
    # Draw the actual roads
    folium.PolyLine(road_path, color="blue", weight=4, opacity=0.8).add_to(m)
else:
    # Fallback to straight line if OSRM is down
    folium.PolyLine([start_coords, end_coords], color="gray", weight=2.5, opacity=0.8, dash_array='5, 5').add_to(m)

# Display the map
st_folium(m, width=700, height=400)

# --- AI LOGIC ---
if st.button("Optimize My Route"):
    with st.spinner("Analyzing traffic patterns and generating optimal route..."):
        try:
            prompt = f"I need to travel from {origin} to {destination} during {time_of_day}. Considering typical Bengaluru traffic, what is the best realistic alternate route to avoid major bottlenecks? Keep your response concise and structured."
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a local Bengaluru transit routing expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            st.success("Route Optimized!")
            st.markdown("### 🧭 Recommended Route")
            st.write(response.choices[0].message.content)
            
        except Exception as e:
            st.error("Engine failure. Check your API key or connection.")
            st.write(e)