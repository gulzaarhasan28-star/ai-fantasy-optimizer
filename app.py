import streamlit as st
import pandas as pd
import numpy as np
import requests
import random
from typing import List, Dict

# ==============================================================================
# 1. PAGE CONFIGURATION & SECRETS
# ==============================================================================
st.set_page_config(layout="wide", page_title="Dream11 Factory Pro")

# --- SECRETS MANAGEMENT ---
# .streamlit/secrets.toml mein rakho:
# [general]
# cricket_api_key = "a5b84aed-6b64-49f5"
def get_api_key():
    try:
        return st.secrets["general"]["cricket_api_key"]
    except:
        return "a5b84aed-6b64-49f5" # Backup hardcode (only for quick testing)

# ==============================================================================
# 2. DATA ACQUISITION & PROCESSING
# ==============================================================================
@st.cache_data(ttl=600)
def fetch_players_from_api(match_id: str) -> pd.DataFrame:
    """Fetch live data from your cricket API provider."""
    api_key = get_api_key()
    url = f"https://apiv2.api-cricket.com/cricket/?method=get_players&APIkey={api_key}&event_key={match_id}"
    
    try:
        response = requests.get(url, timeout=15).json()
        if response.get("status") == "success":
            players_list = response["data"]["players"]
            data = []
            for p in players_list:
                data.append({
                    "name": p.get("name", "Unknown"),
                    "team": p.get("team", "Unknown"),
                    "role": p.get("role", "BAT"),
                    "avg_pts": float(p.get("fantasy_avg", 30.0)),
                    "form": float(p.get("form", 0.7)),
                    "consistency": float(p.get("consistency", 0.7))
                })
            return pd.DataFrame(data)
        else:
            raise Exception("API failure")
    except:
        # Fallback: DEMO DATA (In-production, delete this)
        return pd.DataFrame([
            {"name": "Virat Kohli", "team": "RCB", "role": "BAT", "avg_pts": 45, "form": 0.8, "consistency": 0.9},
            {"name": "Rohit Sharma", "team": "MI", "role": "BAT", "avg_pts": 40, "form": 0.75, "consistency": 0.8},
            {"name": "Rishabh Pant", "team": "DC", "role": "WK", "avg_pts": 42, "form": 0.7, "consistency": 0.82},
            {"name": "Jasprit Bumrah", "team": "MI", "role": "BWL", "avg_pts": 48, "form": 0.9, "consistency": 0.95},
            {"name": "Ravindra Jadeja", "team": "CSK", "role": "AR", "avg_pts": 44, "form": 0.75, "consistency": 0.85},
            {"name": "Hardik Pandya", "team": "GT", "role": "AR", "avg_pts": 42, "form": 0.8, "consistency": 0.8},
            {"name": "Kuldeep Yadav", "team": "DC", "role": "BWL", "avg_pts": 40, "form": 0.7, "consistency": 0.78},
            {"name": "Ishan Kishan", "team": "MI", "role": "WK", "avg_pts": 35, "form": 0.65, "consistency": 0.75},
            {"name": "Shreyas Iyer", "team": "KKR", "role": "BAT", "avg_pts": 40, "form": 0.7, "consistency": 0.8},
            {"name": "T Natarajan", "team": "SRH", "role": "BWL", "avg_pts": 36, "form": 0.7, "consistency": 0.75},
            {"name": "Ruturaj Gaikwad", "team": "CSK", "role": "BAT", "avg_pts": 38, "form": 0.72, "consistency": 0.82},
            {"name": "Suryakumar Yadav", "team": "MI", "role": "BAT", "avg_pts": 42, "form": 0.78, "consistency": 0.88},
            {"name": "Ravi Bishnoi", "team": "LSG", "role": "BWL", "avg_pts": 36, "form": 0.68, "consistency": 0.76},
            {"name": "Mohammed Siraj", "team": "RCB", "role": "BWL", "avg_pts": 38, "form": 0.65, "consistency": 0.8},
        ])

# ==============================================================================
# 3. PERFORMANCE LOGIC (Today's Performer Algorithm)
# ==============================================================================
def calculate_performer_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Algorithm: Base Pts * Form * Consistency * Vibe(Randomised Luck)
    df["vibe"] = np.random.uniform(0.8, 1.0, len(df))
    df["today_score"] = df["avg_pts"] * df["form"] * df["consistency"] * df["vibe"]
    
    # Comeback Boost for high-potential players currently underperforming
    df["today_score"] = df.apply(lambda x: x["today_score"] * 1.5 if x["form"] < 0.6 else x["today_score"], axis=1)
    return df.sort_values("today_score", ascending=False)

# ==============================================================================
# 4. TEAM GENERATION FACTORY
# ==============================================================================
def generate_best_team(df: pd.DataFrame) -> List[Dict]:
    # Dream11 Constraint: 1 WK, 3 BAT, 2 AR, 3 BWL minimum
    team = []
    roles_needed = {"WK": 1, "BAT": 3, "AR": 2, "BWL": 3}
    roles_count = {"WK": 0, "BAT": 0, "AR": 0, "BWL": 0}
    
    # Priority logic
    for _, row in df.iterrows():
        r = row["role"]
        if roles_count.get(r, 0) < roles_needed.get(r, 0):
            team.append(row.to_dict())
            roles_count[r] = roles_count.get(r, 0) + 1
        elif len(team) < 11:
            team.append(row.to_dict())
            roles_count[r] = roles_count.get(r, 0) + 1
        if len(team) == 11: break
    return team

def generate_bulk_teams(df: pd.DataFrame, n: int) -> List[List[Dict]]:
    teams = []
    for _ in range(n):
        # Rotate bench players while keeping core fixed
        core = df.head(8).to_dict("records")
        bench = df.tail(len(df)-8).sample(3).to_dict("records")
        teams.append(core + bench)
    return teams

# ==============================================================================
# 5. USER INTERFACE (STREAMLIT)
# ==============================================================================
st.title("🚀 Dream11 Power Factory | Performance Engine")
st.markdown("---")

# Inputs
col1, col2 = st.columns(2)
match_id = col1.text_input("Enter Match/Event Key:", "MI_VS_DC_2026")
n_teams = col2.number_input("Number of GL Teams to Factory:", 1, 100, 10)

if st.button("GENERATE WINNING TEAMS"):
    # Pipeline
    players = fetch_players_from_api(match_id)
    processed = calculate_performer_score(players)
    
    # 1. Best 11
    best_11 = generate_best_team(processed)
    
    # Captaincy Engine
    c = processed.iloc[0]["name"]
    vc = processed.iloc[1]["name"]
    
    st.subheader("🏆 Best Performance Predictor (Today)")
    st.write(f"**Captain:** {c} | **Vice-Captain:** {vc}")
    st.table(pd.DataFrame(best_11)[["name", "team", "role", "today_score"]])
    
    # 2. Bulk Factory
    st.subheader("🎰 Bulk GL Teams Factory")
    bulk = generate_bulk_teams(processed, n_teams)
    
    # Show one as table
    table_data = []
    for i, t in enumerate(bulk):
        table_data.append({"Team_ID": i+1, "Captain": t[0]["name"], "Total_Confidence": sum(p["today_score"] for p in t)/11})
    st.dataframe(pd.DataFrame(table_data))
    
    st.success("✅ Factory generated successfully!")
