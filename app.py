import streamlit as st
import requests

st.title("🛠️ API Diagnostic Tool")
API_KEY = "a5b84aed-6b64-49f5"

match_id = st.text_input("Enter Match ID:", "DC_VS_RCB_2026")

if st.button("DEBUG API"):
    url = "https://apiv2.api-cricket.com/cricket/"
    params = {"method": "get_players", "APIkey": API_KEY, "event_key": match_id}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        st.write("Status Code:", response.status_code)
        st.write("Raw Response:", response.json()) # Yahan dikhega ki API kya bol rahi hai
    except Exception as e:
        st.write("Error:", e)
