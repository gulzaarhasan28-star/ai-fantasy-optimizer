import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="🔥 Live Power System", layout="wide")
st.title("🔥 Live Power System: DC vs RCB")

# Match ID aaj ke liye (Sahi ID yahan daalo)
MATCH_ID = "DC_VS_RCB_2026" 

def get_live_lineup(match_id):
    # API-Cricket ka sahi Endpoint (Lineups ke liye)
    url = f"https://apiv2.api-cricket.com/cricket/?method=get_lineups&APIkey=a5b84aed-6b64-49f5&event_key={match_id}"
    try:
        resp = requests.get(url, timeout=10).json()
        if resp.get("status") == "success":
            # Real Lineups Data
            players = resp["data"]["home"]["lineup"] + resp["data"]["away"]["lineup"]
            return pd.DataFrame(players)
    except:
        return None

if st.button("🔥 PULL LIVE PLAYING 11"):
    df = get_live_lineup(MATCH_ID)
    
    if df is not None and not df.empty:
        st.success("✅ Lineups Locked! Aaj ke real players mil gaye.")
        
        # Performance logic (Average + Form)
        df['dream_score'] = df['fantasy_points'] * df['recent_form']
        dream_team = df.sort_values('dream_score', ascending=False).head(11)
        
        st.subheader("⭐ Dream Team (Real Players)")
        st.table(dream_team[['name', 'role', 'team']])
        
        # C/VC Engine
        c = dream_team.iloc[0]['name']
        vc = dream_team.iloc[1]['name']
        st.info(f"🚀 Captain: {c} | VC: {vc}")
    else:
        st.error("🚫 Lineups Not Yet Announced! Match shuru hone se 30 min pehle aao.")
