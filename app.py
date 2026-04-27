import streamlit as st
import pandas as pd
import requests

st.title("🏏 Live Match Dream Factory")

# API KEY
API_KEY = "a5b84aed-6b64-49f5"

def get_real_players(match_id):
    # Yeh API URL tumhare provider ka format hai
    url = f"https://apiv2.api-cricket.com/cricket/?method=get_players&APIkey={API_KEY}&event_key={match_id}"
    
    try:
        resp = requests.get(url, timeout=10).json()
        if resp.get("status") == "success":
            # API se aaye huye real khiladi
            players = resp["data"]["players"] 
            return pd.DataFrame(players)
        else:
            return None # Data nahi mila
    except:
        return None # Connection error

match_id = st.text_input("Enter Match Event Key (e.g., DC_VS_RCB_2026):")

if st.button("GET REAL TEAMS"):
    df = get_real_players(match_id)
    
    if df is not None:
        st.success("Real Data Mil Gaya!")
        # Logic: Score calculation (Real data fields ke hisaab se)
        df['score'] = df['fantasy_avg'] * df['form'] 
        top_11 = df.sort_values('score', ascending=False).head(11)
        
        st.subheader("⭐ Aaj Ke 11 Khiladi")
        st.table(top_11[['name', 'team', 'role']])
        
        st.subheader("🎰 Team 1")
        st.write(", ".join(top_11['name'].tolist()))
    else:
        st.error("🚫 Real Data Nahi Mila! API Key check karo ya Match ID sahi daalo.")
