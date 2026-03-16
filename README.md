# 🚦 Bengaluru Transit Optimiser

**A live, AI-powered transit dashboard designed to navigate the unique traffic challenges of Bengaluru.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg.svg)](https://bengaluru-transit-optimiser-g4vbgmvva7q4crvnfeotja.streamlit.app/)

## 🌟 Overview
The Bengaluru Transit Optimiser is a full-stack web application that combines real-time geospatial data with Large Language Models (LLMs) to provide more than just "the fastest route." It offers **contextual driving advice** based on Bengaluru's historical traffic patterns, famous bottlenecks, and live road conditions.

## 🚀 Live Demo
Check out the live app here: [Bengaluru Transit Optimiser](https://bengaluru-transit-optimiser-g4vbgmvva7q4crvnfeotja.streamlit.app/)

## ✨ Features
* **Live Traffic Routing:** Powered by the **TomTom Routing API**, providing real-time traffic-aware paths.
* **AI Local Commentary:** Uses **GPT-4o-mini (via GitHub Models)** to give witty, localized advice (e.g., avoiding the Silk Board junction or flagging specific potholes).
* **Fuzzy Search Geocoding:** Users can type landmarks (e.g., "Christ University") instead of raw coordinates, limited to a 50km Bengaluru radius.
* **Interactive Mapping:** Built with **Folium**, featuring custom markers and dynamic route rendering.
* **Bubbly UI:** A custom-styled, cartoonish interface with a fully functional **Dark/Light Mode** toggle.
* **Step-by-Step Directions:** Detailed turn-by-turn guidance for every optimized route.

## 🛠️ Tech Stack
* **Language:** Python 3.11
* **Frontend:** Streamlit (Custom CSS injection)
* **AI Engine:** OpenAI SDK / GitHub Models (GPT-4o-mini)
* **Maps & Routing:** TomTom Search & Routing APIs, Folium
* **Environment Management:** Python-Dotenv
* **Deployment:** Streamlit Community Cloud

## 🔧 Installation & Local Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/chandresh523/bengaluru-transit-optimiser.git](https://github.com/chandresh523/bengaluru-transit-optimiser.git)
    cd bengaluru-transit-optimiser
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your keys:
    ```text
    GITHUB_TOKEN="your_github_model_token"
    TOMTOM_API_KEY="your_tomtom_api_key"
    ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 🛡️ Security
This project uses `.env` files and Streamlit Secrets to ensure that API keys are never exposed in the public repository history. 

## 👨‍💻 Author
**Chandresh**
* Student at Christ University, Bengaluru
* Passionate about AI, Mobile Development, and Statistical Inference.

---
*Built with ❤️ in Bengaluru.*
