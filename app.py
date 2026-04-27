import streamlit as st
import pandas as pd
import numpy as np
import random


# ───────────────────────────────────────────────────────────────
# DUMMY IPL PLAYER DATA (SCHEMA ONLY, NO CREDITS)
# Yahan par tum apna API data daaloge – naam, team, role, stats
# ───────────────────────────────────────────────────────────────

@st.cache_data()
def get_dummy_players():
    players = [
        # Example Mumbai (MUM)
        {"name": "Player1_MUM", "team": "MUM", "role": "BAT", "avg_pts": 45, "form": 0.7, "vibe": 0.9},
        {"name": "Player2_MUM", "team": "MUM", "role": "BAT", "avg_pts": 42, "form": 0.6, "vibe": 0.8},
        {"name": "Player3_MUM", "team": "MUM", "role": "AR",  "avg_pts": 44, "form": 0.75,"vibe": 0.85},
        {"name": "Player4_MUM", "team": "MUM", "role": "BWL", "avg_pts": 48, "form": 0.9, "vibe": 0.95},
        {"name": "Player5_MUM", "team": "MUM", "role": "BWL", "avg_pts": 38, "form": 0.65,"vibe": 0.82},

        # Example Delhi (DEL)
        {"name": "Player1_DEL", "team": "DEL", "role": "BAT", "avg_pts": 40, "form": 0.8, "vibe": 0.88},
        {"name": "Player2_DEL", "team": "DEL", "role": "WK",  "avg_pts": 43, "form": 0.7, "vibe": 0.86},
        {"name": "Player3_DEL", "team": "DEL", "role": "AR",  "avg_pts": 42, "form": 0.7, "vibe": 0.83},
        {"name": "Player4_DEL", "team": "DEL", "role": "BWL", "avg_pts": 40, "form": 0.75,"vibe": 0.8},
        {"name": "Player5_DEL", "team": "DEL", "role": "BAT", "avg_pts": 36, "form": 0.66,"vibe": 0.78},

        # Extra players (any team)
        {"name": "Player6_EXT", "team": "CSK", "role": "AR",  "avg_pts": 44, "form": 0.7, "vibe": 0.82},
        {"name": "Player7_EXT", "team": "SRH", "role": "BWL", "avg_pts": 36, "form": 0.7, "vibe": 0.8},
        {"name": "Player8_EXT", "team": "RR",  "role": "BAT", "avg_pts": 34, "form": 0.65,"vibe": 0.75},
        {"name": "Player9_EXT", "team": "PBKS","role": "BWL", "avg_pts": 36, "form": 0.68,"vibe": 0.76},
        {"name": "Player10_EXT","team": "RCB", "role": "WK",  "avg_pts": 43, "form": 0.7, "vibe": 0.88},
    ]
    return pd.DataFrame(players)


# ───────────────────────────────────────────────────────────────
# TODAY'S PERFORMER SCORE (Luck + Form + Base Stats)
# ───────────────────────────────────────────────────────────────

def compute_today_performer(row: pd.Series) -> float:
    # 1. base performance
    base = row["avg_pts"] * row["form"] * row["vibe"]
    # 2. “due for a big score” logic (low‑average last 3)
    last_3_var = 0.2  # real code me yahan last 3 matches avg add karoge
    if last_3_var < 0.6 * row["avg_pts"]:
        base *= 1.5  # 90% “comeback” boost concept
    score = np.clip(base / 70, 0.2, 1.8)
    # 0–1 range: 0.2 → 0, 1.8 → 1
    return (score - 0.2) / 1.6


# ───────────────────────────────────────────────────────────────
# BEST 11 DREAM TEAM (no credits, no 100‑cr cap)
# ───────────────────────────────────────────────────────────────

def build_best_11(players: pd.DataFrame, role_min: Dict[str, int] = None) -> List[Dict]:
    if role_min is None:
        role_min = {"WK": 1, "BAT": 3, "AR": 2, "BWL": 3, "ATH": 2}  # ATH = any extra

    players_sorted = players.sort_values("today_score", ascending=False).to_dict("records")
    team = []
    counts = {"WK": 0, "BAT": 0, "AR": 0, "B WL": 0}

    for p in players_sorted:
        role = p["role"]
        # Ensure at least 1 WK, 3 BAT, 2 AR, 3 BOWL
        if counts.get(role, 0) >= role_min.get(role, 0):
            if len(team) < 11:
                team.append(p)
        else:
            team.append(p)
            counts[role] = counts.get(role, 0) + 1
        if len(team) == 11:
            break

    # Still not 11? fill with top‑performers
    if len(team) < 11:
        taken = {p["name"] for p in team}
        for p in players_sorted:
            if p["name"] not in taken:
                team.append(p)
            if len(team) == 11:
                break

    return team


# ───────────────────────────────────────────────────────────────
# UNLIMITED DREAM‑TEAM FACTORY (Mega‑GL rotation)
# ───────────────────────────────────────────────────────────────

def generate_mega_gl_teams(popular_set: List[Dict], others: List[Dict], n_teams: int) -> List[List[Dict]]:
    # popular_set = 10–20 best players
    # others = backup bench
    teams = []
    seen = set()
    for _ in range(n_teams * 3):
        # 7 strong core + 4 rotated from bench
        core = random.sample(popular_set, 7)
        extras = random.sample(others, 4)
        team = core + extras
        key = frozenset(p["name"] for p in team)
        if key not in seen and len(team) == 11:
            seen.add(key)
            teams.append(team)
        if len(teams) >= n_teams:
            break
    return teams


# ───────────────────────────────────────────────────────────────
# WINNING CONFIDENCE PER TEAM (Performance‑Intensity)
# ───────────────────────────────────────────────────────────────
def compute_team_confidence(team: List[Dict]) -> float:
    scores = [p["today_score"] for p in team]
    mean_score = np.mean(scores)
    # 0.2–1.5 → 0–1 confidence
    s = np.clip(mean_score * 3.0, 0.2, 1.5)
    return (s - 0.2) / 1.3


# ───────────────────────────────────────────────────────────────
# CAPTAIN / VICE‑CAPTAIN: “Ceiling” Engine (100+‑point potential)
# ───────────────────────────────────────────────────────────────

def compute_ceiling_score(row: pd.Series, is_cap: bool = False) -> float:
    base = row["avg_pts"] * row["form"] * row["vibe"]
    cap_boost = 2.0 if is_cap else 1.5
    return base * cap_boost

def pick_c_vc(players: pd.DataFrame) -> tuple:
    cap_series = players.assign(
        cap_score=players.apply(lambda r: compute_ceiling_score(r, True), axis=1)
    )
    vc_series = players.assign(
        vc_score=players.apply(lambda r: compute_ceiling_score(r, False), axis=1)
    )
    cap = cap_series.loc[cap_series["cap_score"].idxmax(), "name"]
    vc = vc_series[vc_series["name"] != cap].loc[vc_series["vc_score"].idxmax(), "name"]
    return cap, vc


# ───────────────────────────────────────────────────────────────
# STREAMLIT UI: Dream Team Finder (No Credits, Pure Performance)
# ───────────────────────────────────────────────────────────────

st.set_page_config(
    layout="wide",
    page_title="Dream11 Dream‑Team Finder (No Credits, Power‑System)"
)

st.title("🧠 Dream11 Super‑Power Performance System")

st.markdown(
    """
    Advanced AI‑style system jo **kyun player aaj perform karega** predict karta hai,  
    phir uske basis par **11‑player Dream Team** banaata hai – **bina 100‑credits ka tension**.  
    Tum jitni bhi **grand‑league teams** chaaho, system unlimited teams bana dega.
    """
)

# Load data
players = get_dummy_players()

# Simulate “last 3 matches” avg for “comeback” logic (in real app, replace with API)
players["last_3_avg"] = players["avg_pts"] * (0.8 + 0.4 * np.random.rand())  # dummy
players["today_score"] = players.apply(compute_today_performer, axis=1)
player_list = players.to_dict("records")

# Side Panel: Match Setup
st.sidebar.header("Match Setup")
all_teams = sorted(players["team"].unique())
team1 = st.sidebar.selectbox("Team 1", all_teams, index=0)
team2 = st.sidebar.selectbox("Team 2", [t for t in all_teams if t != team1], index=0)

teams_filter = [team1, team2]
filtered = players[players["team"].isin(teams_filter)].copy()
filter_list = filtered.to_dict("records")

st.sidebar.divider()
st.sidebar.header("Factory Settings")
n_teams = st.sidebar.number_input(
    "How many Mega‑GL teams?", 1, 100, 20
)
risk_level = st.sidebar.selectbox(
    "Risk Type", ["Safe", "Balanced", "High‑Risky (GL‑Focused)"]
)


if st.sidebar.button("👾 Find Today's Best Performers & Dream Team"):

    # 1. Top 10–20 performers (core bench)
    top_performers = filtered.sort_values("today_score", ascending=False).head(20)
    popular_names = top_performers["name"].tolist()
    popular_list = top_performers.to_dict("records")
    others_list = [p for p in filter_list if p["name"] not in popular_names]

    # 2. Best 11 Dream Team
    st.markdown("<h2>⭐ Best 11 Dream Team (Today’s Top Performers)</h2>", unsafe_allow_html=True)
    best_11 = build_best_11(top_performers)
    conf = compute_team_confidence(best_11)
    cap, vc = pick_c_vc(top_performers)

    st.markdown(
        f"**Confidence: {int(conf * 100)}%** | **Captain: {cap}** | **VC: {vc}**"
    )
    for p in best_11:
        st.markdown(
            f"- **{p['name']}** ({p['team']} | {p['role']}) – "
            f"Today’s Score: {p['today_score']:.2f}"
        )

    # 3. Show Mega‑GL teams table
    st.markdown(
        "<h2>🎲 Mega‑GL Grand‑League Team Factory</h2>",
        unsafe_allow_html=True
    )
    mega_teams = generate_mega_gl_teams(popular_list, others_list, n_teams)

    table_data = []
    for i, team in enumerate(mega_teams):
        conf = compute_team_confidence(team)
        cap, vc = pick_c_vc(pd.DataFrame(team))
        table_data.append({
            "Team": f"GL Team {i+1}",
            "Confidence": f"{int(conf * 100)}%",
            "Captain": cap,
            "VC": vc,
            "Best Players": "<br>".join(
                f"{p['name']} ({p['team']} | {p['role']} | {p['today_score']:.2f})"
                for p in team[:6]  # top 6 as key players
            ),
        })

    if len(table_data) == 0:
        st.warning("Not enough players; try more teams or data.")
    else:
        df = pd.DataFrame(table_data)
        st.data_editor(
            df,
            column_config={"Best Players": st.column_config.TextColumn("Key Players", width="large")},
            use_container_width=True,
            hide_index=True
        )

        st.markdown("<h3>🔍 Example GL Team Breakdown</h3>", unsafe_allow_html=True)
        ex = mega_teams[0]
        ex_conf = compute_team_confidence(ex)
        ex_cap, ex_vc = pick_c_vc(pd.DataFrame(ex))
        st.markdown(
            f"**Team 1 GL:** Confidence **{int(ex_conf * 100)}%** | C: **{ex_cap}** | VC: **{ex_vc}**"
        )
        for p in ex:
            st.markdown(
                f"- **{p['name']}** ({p['team']} | {p['role']}) – Today Score: {p['today_score']:.2f}"
         )
