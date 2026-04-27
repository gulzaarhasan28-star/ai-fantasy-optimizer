import streamlit as st
import pandas as pd
import numpy as np
import requests
import random

st.set_page_config(layout="wide", page_title="Ultimate Dream11 Factory")

# 1. API CONNECTION (Your Key Set)
API_KEY = "a5b84aed-6b64-49f5"

@st.cache_data(ttl=300)
def fetch_live_match_data(match_id):
    # API Structure for Match Players
    url = f"https://apiv2.api-cricket.com/cricket/?method=get_players&APIkey={API_KEY}&event_key={match_id}"
    try:
        response = requests.get(url, timeout=10).json()
        players = []
        for p in response['data']['players']:
            players.append({
                "name": p['name'], "team": p['team'], "role": p['role'],
                "avg": float(p.get('fantasy_avg', 30)), "form": float(p.get('form', 0.7))
            })
        return pd.DataFrame(players)
    except:
        # Fallback to Mock if API doesn't respond for DC/RCB yet
        return pd.DataFrame([
            {"name": "Virat Kohli", "team": "RCB", "role": "BAT", "avg": 45, "form": 0.9},
            {"name": "Rishabh Pant", "team": "DC", "role": "WK", "avg": 42, "form": 0.85},
            {"name": "Kuldeep Yadav", "team": "DC", "role": "BWL", "avg": 40, "form": 0.9},
            {"name": "Axar Patel", "team": "DC", "role": "AR", "avg": 38, "form": 0.8},
            {"name": "Mohammed Siraj", "team": "RCB", "role": "BWL", "avg": 35, "form": 0.75},
            {"name": "Faf du Plessis", "team": "RCB", "role": "BAT", "avg": 40, "form": 0.8},
            {"name": "David Warner", "team": "DC", "role": "BAT", "avg": 39, "form": 0.7},
            {"name": "Glenn Maxwell", "team": "RCB", "role": "AR", "avg": 36, "form": 0.65},
            {"name": "Anrich Nortje", "team": "DC", "role": "BWL", "avg": 35, "form": 0.7},
            {"name": "Dinesh Karthik", "team": "RCB", "role": "WK", "avg": 32, "form": 0.75},
            {"name": "Prithvi Shaw", "team": "DC", "role": "BAT", "avg": 30, "form": 0.6},
            {"name": "Cameron Green", "team": "RCB", "role": "AR", "avg": 34, "form": 0.7}
        ])

# 2. LOGIC: WHO WILL PERFORM?
def get_dream_team(df):
    df['score'] = df['avg'] * df['form'] * np.random.uniform(0.9, 1.1, len(df))
    return df.sort_values('score', ascending=False).head(11)

# 3. UI
st.title("🏏 Ultimate Dream Team Factory (Live)")
match_id = st.text_input("Match ID", "DC_VS_RCB_2026")
n_teams = st.number_input("Number of Teams", 1, 50, 5)

if st.button("GENERATE DREAM TEAMS"):
    df = fetch_live_match_data(match_id)
    dream_team = get_dream_team(df)
    
    st.subheader("⭐ Today's Dream Team (Top 11)")
    st.dataframe(dream_team[['name', 'team', 'role']])
    
    st.subheader(f"🎰 {n_teams} Mega GL Teams Factory")
    for i in range(n_teams):
        # Rotation Logic
        team = dream_team.sample(11)
        c = team.iloc[0]['name']
        vc = team.iloc[1]['name']
        st.write(f"**Team {i+1}** | Captain: {c} | VC: {vc}")
        st.write(", ".join(team['name'].tolist()))
        st.markdown("---")
