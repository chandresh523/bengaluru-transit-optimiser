import os
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from dotenv import load_dotenv
from openai import OpenAI

# --- SECRETS & SETUP ---
load_dotenv()

# Grab keys (Hardcoded for testing!)
# Grab keys from the .env file
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
TOMTOM_API_KEY = os.environ.get("TOMTOM_API_KEY")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=GITHUB_TOKEN
)

# --- SESSION STATE FOR DARK MODE ---
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# --- CUSTOM CARTOON UI CSS ---
# This injects custom styles to make it look fun, bright, and bubbly
if st.session_state.dark_mode:
    bg_color, text_color, card_bg = "#1a1a2e", "#ffffff", "#16213e"
else:
    bg_color, text_color, card_bg = "#f0f8ff", "#333333", "#ffffff"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif;
    }}
    .stTextInput>div>div>input {{
        border-radius: 15px;
        border: 3px solid #ff6b6b;
        padding: 10px;
        font-size: 16px;
    }}
    /* The big bubbly button */
    div.stButton > button:first-child {{
        background-color: #ff9f43;
        color: white;
        border-radius: 25px;
        border: 3px solid #ee5253;
        box-shadow: 4px 4px 0px #ee5253;
        font-size: 18px;
        font-weight: bold;
        transition: 0.2s;
    }}
    div.stButton > button:first-child:active {{
        box-shadow: 0px 0px 0px #ee5253;
        transform: translateY(4px);
    }}
    .css-1d391kg {{
        background-color: {card_bg};
        border-radius: 15px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- TOMTOM API FUNCTIONS ---
def get_coordinates(location_name):
    """Turns a text location into GPS coordinates using a strict Bengaluru bounding box."""
    # Center of Bengaluru coordinates
    BLR_LAT, BLR_LON = 12.9716, 77.5946
    
    url = f"https://api.tomtom.com/search/2/search/{location_name}.json"
    
    # We use params to properly format the URL and FORCE it to stay near Bengaluru
    params = {
        "key": TOMTOM_API_KEY,
        "limit": 1,
        "lat": BLR_LAT,
        "lon": BLR_LON,
        "radius": 50000,  # Only search within 50km of Bengaluru center!
        "countrySet": "IN"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json().get('results', [])
        if results:
            lat = results[0]['position']['lat']
            lon = results[0]['position']['lon']
            return [lat, lon]
    return None

def get_tomtom_route(start_coords, end_coords):
    """Gets the live route AND the turn-by-turn text instructions."""
    start_lat, start_lon = start_coords[0], start_coords[1]
    end_lat, end_lon = end_coords[0], end_coords[1]
    
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_lat},{start_lon}:{end_lat},{end_lon}/json"
    
    params = {
        "key": TOMTOM_API_KEY,
        "traffic": "true",
        "instructionsType": "text" # MAGIC FIX: Ask for written directions!
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        
        # 1. Get the map coordinates
        points = data['routes'][0]['legs'][0]['points']
        route_path = [[p['latitude'], p['longitude']] for p in points]
        
        # 2. Extract the step-by-step instructions
        instructions = []
        if 'guidance' in data['routes'][0] and 'instructions' in data['routes'][0]['guidance']:
            for step in data['routes'][0]['guidance']['instructions']:
                instructions.append(step['message'])
                
        return route_path, instructions
        
    return None, None

# --- UI LAYOUT ---
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🚦 Bubbly Bengaluru Transit")
with col2:
    # The Dark Mode Toggle Button
    st.button("🌓 Theme", on_click=toggle_theme)

st.markdown(f"**Current Mode:** {'Dark 🌙' if st.session_state.dark_mode else 'Light ☀️'}")

# Text inputs instead of dropdowns! Type literally anything.
origin = st.text_input("📍 Where are you starting?", placeholder="e.g. Truffles Koramangala")
destination = st.text_input("🏁 Where are you going?", placeholder="e.g. Christ University Central Campus")
time_of_day = st.radio("⏰ When are you leaving?", ["Right Now (Live Traffic)", "Morning Peak", "Evening Peak"], horizontal=True)

if st.button("🚀 Optimize My Route!"):
    if not origin or not destination:
        st.warning("Whoops! You need to type a start and end point!")
    else:
        with st.spinner("Snooping on Bengaluru traffic cameras... 🕵️‍♂️"):
            
            start_coords = get_coordinates(origin)
            end_coords = get_coordinates(destination)
            
            if not start_coords or not end_coords:
                st.error("Uh oh! I couldn't find those locations. Try being a bit more specific!")
            else:
                # Catch BOTH the route and the text instructions now
                route_path, instructions = get_tomtom_route(start_coords, end_coords)
                
                if route_path:
                    st.markdown("### 🗺️ Your Magic Route")
                    
                    mid_lat = (start_coords[0] + end_coords[0]) / 2
                    mid_lon = (start_coords[1] + end_coords[1]) / 2
                    
                    m = folium.Map(location=[mid_lat, mid_lon], zoom_start=13, tiles="CartoDB positron")
                    
                    folium.Marker(start_coords, tooltip="Start", icon=folium.Icon(color="green", icon="rocket", prefix='fa')).add_to(m)
                    folium.Marker(end_coords, tooltip="Finish", icon=folium.Icon(color="red", icon="flag", prefix='fa')).add_to(m)
                    
                    folium.PolyLine(route_path, color="#ff4757", weight=6, opacity=0.9).add_to(m)
                    
                    st_folium(m, width=700, height=400, returned_objects=[])
                    
                    # --- NEW: DISPLAY TURN-BY-TURN DIRECTIONS ---
                    if instructions:
                        with st.expander("📝 Step-by-Step Directions"):
                            for i, step in enumerate(instructions, 1):
                                st.write(f"**{i}.** {step}")
                    
                    # AI Commentary (unchanged)
                    prompt = f"I am driving from {origin} to {destination} in Bengaluru. The time is {time_of_day}. I am using a live traffic route. In 3 short, punchy, fun sentences, give me local advice on what to watch out for on this specific drive (like bad potholes, speed breakers, or famous traffic traps)."
                    
                    try:
                        ai_response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "You are a witty, fun Bengaluru local who knows the roads perfectly."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.8
                        )
                        st.success("Route Locked In! 🎯")
                        st.info(ai_response.choices[0].message.content)
                    except Exception as e:
                        st.error("AI engine took a coffee break.")
                        st.write(e)
                else:
                    st.error("TomTom couldn't calculate a route for this!")