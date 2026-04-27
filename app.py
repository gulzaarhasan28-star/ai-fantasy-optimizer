import streamlit as st
import pandas as pd
import requests

st.title("🏏 Live Match Dream Factory (FIXED)")

# API KEY INJECTION
API_KEY = "a5b84aed-6b64-49f5"

def get_real_players(match_id):
    # API URL ke saath Key ko params mein bhejna zaroori hai
    url = "https://apiv2.api-cricket.com/cricket/"
    params = {
        "method": "get_players",
        "APIkey": API_KEY,      # API Key yahan injekt ho rahi hai
        "event_key": match_id
    }
    
    try:
        # Request with parameters
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        # Checking if data exists
        if resp.status_code == 200 and data.get("status") == "success":
            players = pd.DataFrame(data['data']['players'])
            return players
        else:
            st.error(f"API Error: {data.get('message', 'Check Match ID')}")
            return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None

match_id = st.text_input("Enter Match ID (e.g., DC_VS_RCB_2026):")

if st.button("GET REAL DATA"):
    df = get_real_players(match_id)
    if df is not None:
        st.write("Real Data Received:", df.head())
    else:
        st.write("No data found. API Key might be invalid or Match ID is wrong.")
