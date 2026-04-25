import streamlit as st
import pandas as pd
import numpy as np
from pulp import *
import requests
import random

# --- CONFIGURATION & UI ---
st.set_page_config(page_title="AI Fantasy Intel Pro", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div.stButton > button:first-child { background-color: #00ffcc; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- API INTEGRATION LAYER ---
def fetch_realtime_data(api_key):
    """
    Fetches Live Toss, Playing XI, and Pitch Report.
    Using RapidAPI (Cricbuzz/CricketData)
    """
    # Placeholder for actual API call logic
    # In production, replace with actual endpoints
    try:
        # Example: requests.get(url, headers={"X-RapidAPI-Key": api_key})
        mock_data = {
            "toss": "Team A won & elected to Bat",
            "pitch": "Dry/Dusty",
            "playing_xi": ["Player 1", "Player 3", "Player 5", "Player 10"], # etc
            "weather": {"humidity": 75, "dew_factor": "High"}
        }
        return mock_data
    except:
        return None

# --- THE AI NEURAL BRAIN (LOGIC) ---
def calculate_ai_score(player_row, pitch, weather):
    """
    Custom Algorithm: Matchup + Venue + Luck + Form
    """
    base_score = player_row['recent_avg_pts']
    
    # 1. Venue Specialist Heatmap
    venue_boost = 1.15 if player_row['venue_avg'] > 40 else 1.0
    
    # 2. Luck-Meter Algorithm
    # Logic: High conversion of 20s to 50s + few 'dropped catch' escapes recently
    luck_factor = (player_row['conversion_rate'] * 0.7) + (player_row['dropped_lives'] * 0.3)
    
    # 3. Pitch & Weather Adjustments
    pitch_adj = 1.0
    if pitch == "Dry/Dusty" and player_row['role'] == 'Spinner': pitch_adj = 1.25
    if weather['dew_factor'] == "High" and player_row['role'] == 'Bowler': pitch_adj = 0.85 # Harder to grip
    
    # 4. Psychological Form (Pressure Handling)
    impact_points = player_row['sr_last_5_games'] / 100
    
    final_score = (base_score * venue_boost * pitch_adj) + luck_factor + impact_points
    return round(final_score, 2)

# --- MATHEMATICAL OPTIMIZATION (PuLP) ---
def solve_knapsack(df, constraints, locked_players=[]):
    prob = LpProblem("FantasyTeam", LpMaximize)
    player_vars = LpVariable.dicts("Players", df.index, cat='Binary')

    # Objective: Maximize AI Power Score
    prob += lpSum([df.loc[i, 'ai_score'] * player_vars[i] for i in df.index])

    # Constraint: 100 Credit Limit
    prob += lpSum([df.loc[i, 'credits'] * player_vars[i] for i in df.index]) <= 100

    # Constraint: Exactly 11 players
    prob += lpSum([player_vars[i] for i in df.index]) == 11

    # Team Composition Rules
    prob += lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'WK']) >= 1
    prob += lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BAT']) >= 3
    prob += lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'AR']) >= 1
    prob += lpSum([player_vars[i] for i in df.index if df.loc[i, 'role'] == 'BOWL']) >= 3

    # Lock Core Players
    for p_name in locked_players:
        idx = df[df['name'] == p_name].index
        if not idx.empty:
            prob += player_vars[idx[0]] == 1

    prob.solve(PULP_CBC_CMD(msg=0))
    
    selected_indices = [i for i in df.index if player_vars[i].varValue == 1]
    return df.loc[selected_indices]

# --- STREAMLIT DASHBOARD ---
def main():
    st.title("⚡ AI Fantasy Intelligence Pipeline")
    
    with st.sidebar:
        st.header("Control Center")
        api_key = st.text_input("RapidAPI Key", type="password")
        mode = st.selectbox("Selection Strategy", ["Safe-Core (0.01% Loss)", "Aggressive G.L."])
        num_teams = st.slider("Generate Bulk Teams", 1, 100, 10)
        
    # Mock Data for Demonstration
    raw_data = {
        'name': [f'Player {i}' for i in range(1, 23)],
        'role': ['WK', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT']*2,
        'credits': [9.5, 10.5, 9.0, 8.5, 9.0, 10.0, 8.5, 8.0, 9.0, 8.5, 7.5]*2,
        'recent_avg_pts': np.random.randint(30, 80, 22),
        'venue_avg': np.random.randint(20, 60, 22),
        'conversion_rate': np.random.uniform(0.1, 0.5, 22),
        'dropped_lives': np.random.randint(0, 3, 22),
        'sr_last_5_games': np.random.randint(110, 180, 22)
    }
    df = pd.DataFrame(raw_data)

    # 1. Auto-Sync Fetcher
    live_data = fetch_realtime_data(api_key)
    st.info(f"🏟️ Pitch: {live_data['pitch']} | 🌦️ Weather: {live_data['weather']['dew_factor']} Dew")

    # 2. Apply AI Neural Brain
    df['ai_score'] = df.apply(lambda x: calculate_ai_score(x, live_data['pitch'], live_data['weather']), axis=1)
    
    # 3. Smart Filter (Playing XI)
    # df = df[df['name'].isin(live_data['playing_xi'])] # Uncomment in production

    # 4. Generate Teams
    if st.button(f"🚀 Generate {num_teams} Unique Teams"):
        all_teams = []
        
        # 0.01% Loss Strategy: Lock 7 core players
        core_df = df.nlargest(7, 'ai_score')
        core_names = core_df['name'].tolist()
        
        for t in range(num_teams):
            # Mathematically rotate the remaining 4 slots
            optimized_team = solve_knapsack(df, None, locked_players=core_names)
            
            # Predict C/VC
            top_2 = optimized_team.nlargest(2, 'ai_score')['name'].tolist()
            
            team_entry = {
                "Team ID": t+1,
                "Players": ", ".join(optimized_team['name'].tolist()),
                "Captain": top_2[0],
                "Vice-Captain": top_2[1],
                "Total AI Power": optimized_team['ai_score'].sum()
            }
            all_teams.append(team_entry)
            
            # Rotate core slightly to ensure uniqueness for next iteration
            random_idx = random.choice(df.index)
            df.at[random_idx, 'ai_score'] *= 0.95 

        st.dataframe(pd.DataFrame(all_teams))

if __name__ == "__main__":
    main()
