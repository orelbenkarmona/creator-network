import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3

# ----------------------------
# CONFIG
# ----------------------------
st.set_page_config(
    page_title="Creator Network",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "Creator Network"
DB_PATH = "data/app.db"


# ----------------------------
# STYLES (cleaner + less "prototype")
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]  {
  font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Background */
.stApp {
  background: radial-gradient(1200px 800px at 10% 0%, rgba(255,107,107,0.18), transparent 50%),
              radial-gradient(900px 700px at 90% 10%, rgba(78,205,196,0.14), transparent 55%),
              linear-gradient(135deg, #0b0f17 0%, #0f1220 60%, #0b0f17 100%);
}

/* Cards */
.card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  backdrop-filter: blur(16px);
  border-radius: 18px;
  padding: 18px;
}
.hero {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 22px;
  padding: 26px 22px;
  margin-bottom: 16px;
}
.small-muted { color: rgba(255,255,255,0.65); font-size: 14px; }
.badge {
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  font-size: 12px;
  color: rgba(255,255,255,0.85);
  margin-right: 8px;
}
.badge-verified {
  border: 1px solid rgba(78,205,196,0.45);
  background: rgba(78,205,196,0.14);
  color: rgba(200,255,250,0.95);
}

/* Buttons */
.stButton>button {
  border-radius: 14px !important;
  font-weight: 600 !important;
  padding: 10px 14px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATABASE
# ----------------------------
def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = db()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        account_type TEXT NOT NULL,
        niche TEXT,
        revenue TEXT,
        size INTEGER,
        location TEXT,
        bio TEXT,
        verified INTEGER DEFAULT 0,
        created TEXT NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        body TEXT NOT NULL,
        created TEXT NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        a TEXT NOT NULL,
        b TEXT NOT NULL,
        created TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def read_profiles():
    conn = db()
    df = pd.read_sql_query("SELECT * FROM profiles ORDER BY created DESC", conn)
    conn.close()
    return df

def insert_profile(row: dict):
    conn = db()
    conn.execute("""
    INSERT INTO profiles (name, account_type, niche, revenue, size, location, bio, verified, created)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["name"], row["account_type"], row["niche"], row["revenue"], row["size"],
        row["location"], row["bio"], int(row["verified"]), row["created"]
    ))
    conn.commit()
    conn.close()

def insert_message(sender, receiver, body):
    conn = db()
    conn.execute("""
    INSERT INTO messages (sender, receiver, body, created)
    VALUES (?, ?, ?, ?)
    """, (sender, receiver, body, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def read_messages(user):
    conn = db()
    df = pd.read_sql_query("""
        SELECT * FROM messages
        WHERE sender = ? OR receiver = ?
        ORDER BY created DESC
    """, conn, params=(user, user))
    conn.close()
    return df

def insert_match(a, b):
    conn = db()
    conn.execute("""
    INSERT INTO matches (a, b, created)
    VALUES (?, ?, ?)
    """, (a, b, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def read_matches(user):
    conn = db()
    df = pd.read_sql_query("""
        SELECT * FROM matches
        WHERE a = ? OR b = ?
        ORDER BY created DESC
    """, conn, params=(user, user))
    conn.close()
    return df

init_db()

# ----------------------------
# SIMPLE "LOGIN"
# ----------------------------
if "user" not in st.session_state:
    st.session_state.user = ""

with st.sidebar:
    st.markdown(f"### 🔥 {APP_NAME}")
    st.caption("Demo build (garage MVP).")
    st.markdown("---")
    st.session_state.user = st.text_input("Your name (for messaging)", value=st.session_state.user, placeholder="e.g., Orel")
    st.markdown("---")
    page = st.radio("Navigate", ["Dashboard", "Create Profile", "Marketplace", "Messages"], index=0)

# ----------------------------
# HEADER
# ----------------------------
st.markdown(f"""
<div class="hero">
  <div style="display:flex; justify-content:space-between; gap:12px; align-items:flex-start; flex-wrap:wrap;">
    <div>
      <h1 style="margin:0; color:white;">🔥 {APP_NAME}</h1>
      <div class="small-muted">A verified marketplace connecting creators and managers with transparent terms.</div>
      <div style="margin-top:10px;">
        <span class="badge">Trust-first</span>
        <span class="badge">Transparent deals</span>
        <span class="badge">Verified profiles</span>
      </div>
    </div>
    <div style="text-align:right;">
      <div class="small-muted">Logged in as</div>
      <div style="color:white; font-weight:700; font-size:18px;">{st.session_state.user if st.session_state.user else "Guest"}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

profiles = read_profiles()

# ----------------------------
# DASHBOARD
# ----------------------------
if page == "Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    agencies = int((profiles["account_type"] == "Agency").sum()) if not profiles.empty else 0
    creators = int((profiles["account_type"] == "Creator").sum()) if not profiles.empty else 0
    verified = int((profiles["verified"] == 1).sum()) if not profiles.empty else 0

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Total Profiles", len(profiles))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Agencies", agencies)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Creators", creators)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("Verified Profiles", verified)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Insights")
    if not profiles.empty:
        revenue_map = {
            "$0-5k": 2500, "$5-20k": 12500, "$20k+": 50000,
            "$0-10k": 5000, "$10-50k": 30000, "$50k+": 75000
        }
        df_plot = profiles.copy()
        df_plot["revenue_numeric"] = df_plot["revenue"].map(revenue_map).fillna(0)

        fig = px.bar(
            df_plot,
            x="niche",
            y="revenue_numeric",
            color="account_type",
            title="Revenue (rough buckets) by Niche",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet. Create your first profile in **Create Profile**.")

# ----------------------------
# CREATE PROFILE
# ----------------------------
elif page == "Create Profile":
    st.markdown("### Create your profile")

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        account_type = st.selectbox("Account Type", ["Creator", "Agency"])
        name = st.text_input("Display Name", placeholder="Your brand / name")
        niche = st.text_input("Niche", placeholder="fitness, education, lifestyle, etc.")
        location = st.text_input("Location", placeholder="City, Country")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if account_type == "Agency":
            revenue = st.selectbox("Monthly Revenue Managed", ["$0-10k", "$10-50k", "$50k+"])
            size = st.slider("Creators Managed", 0, 200, 5)
            bio = st.text_area("Agency Bio", height=120, placeholder="What do you do? What results can you prove?")
        else:
            revenue = st.selectbox("Monthly Revenue", ["$0-5k", "$5-20k", "$20k+"])
            size = st.slider("Audience Size (approx)", 0, 500000, 10000, step=5000)
            bio = st.text_area("Creator Bio", height=120, placeholder="What are your goals and what help do you want?")
        verified = False

        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Publish Profile", use_container_width=True):
        if not name.strip():
            st.error("Name is required.")
        else:
            insert_profile({
                "name": name.strip(),
                "account_type": account_type,
                "niche": niche.strip(),
                "revenue": revenue,
                "size": int(size),
                "location": location.strip(),
                "bio": bio.strip(),
                "verified": verified,
                "created": datetime.now().isoformat()
            })
            st.success("Profile published.")
            st.rerun()

# ----------------------------
# MARKETPLACE
# ----------------------------
elif page == "Marketplace":
    st.markdown("### Marketplace")

    a, b, c = st.columns([2, 1, 1])
    with a:
        q = st.text_input("Search", placeholder="niche, name, location...")
    with b:
        show = st.selectbox("Show", ["All", "Creators", "Agencies"])
    with c:
        only_verified = st.checkbox("Verified only", value=False)

    df = profiles.copy()
    if df.empty:
        st.info("No profiles yet. Create one in **Create Profile**.")
    else:
        if q.strip():
            q2 = q.strip().lower()
            df = df[
                df["name"].str.lower().str.contains(q2, na=False) |
                df["niche"].str.lower().str.contains(q2, na=False) |
                df["location"].str.lower().str.contains(q2, na=False)
            ]
        if show != "All":
            df = df[df["account_type"] == ("Creator" if show == "Creators" else "Agency")]
        if only_verified:
            df = df[df["verified"] == 1]

        for _, p in df.iterrows():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            top = st.columns([3, 1, 1])

            with top[0]:
                badges = ""
                if int(p["verified"]) == 1:
                    badges += '<span class="badge badge-verified">Verified</span>'
                badges += f'<span class="badge">{p["account_type"]}</span>'
                st.markdown(f"{badges}", unsafe_allow_html=True)

                st.markdown(f"**{p['name']}**")
                st.caption(f"{p.get('niche','')} • {p.get('location','')} • {p.get('revenue','')}")
                st.write(p.get("bio","")[:220] + ("..." if len(p.get("bio","")) > 220 else ""))

            with top[1]:
                if st.button("Message", key=f"msg_{p['id']}", use_container_width=True):
                    if not st.session_state.user.strip():
                        st.error("Set your name in the sidebar first.")
                    else:
                        st.session_state["_compose_to"] = p["name"]
                        st.session_state["_nav_to_messages"] = True

            with top[2]:
                if st.button("Match", key=f"match_{p['id']}", use_container_width=True):
                    if not st.session_state.user.strip():
                        st.error("Set your name in the sidebar first.")
                    else:
                        insert_match(st.session_state.user.strip(), p["name"])
                        st.success(f"Matched with {p['name']} ✅")

            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("_nav_to_messages"):
            st.session_state["_nav_to_messages"] = False
            st.info("Go to **Messages** to write your message (pre-filled).")

# ----------------------------
# MESSAGES
# ----------------------------
elif page == "Messages":
    st.markdown("### Messages")

    if not st.session_state.user.strip():
        st.warning("Set your name in the sidebar first.")
    else:
        user = st.session_state.user.strip()
        msgs = read_messages(user)
        matches = read_matches(user)

        left, right = st.columns([1, 1])

        with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Compose")
            to_default = st.session_state.get("_compose_to", "")
            to = st.text_input("To", value=to_default, placeholder="Type a profile name")
            body = st.text_area("Message", height=120, placeholder="Write a short intro + what you want.")
            if st.button("Send"):
                if not to.strip() or not body.strip():
                    st.error("To + Message required.")
                else:
                    insert_message(user, to.strip(), body.strip())
                    st.session_state["_compose_to"] = ""
                    st.success("Sent ✅")
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Your Matches")
            if matches.empty:
                st.caption("No matches yet.")
            else:
                people = []
                for _, m in matches.iterrows():
                    other = m["b"] if m["a"] == user else m["a"]
                    people.append(other)
                for other in sorted(set(people)):
                    st.write(f"✅ {other}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### Recent messages")
        if msgs.empty:
            st.caption("No messages yet.")
        else:
            for _, m in msgs.head(12).iterrows():
                direction = "→" if m["sender"] == user else "←"
                other = m["receiver"] if m["sender"] == user else m["sender"]
                st.markdown(f"**{direction} {other}**  \n{m['body']}")
                st.caption(m["created"])
                st.markdown("---")
