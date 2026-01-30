import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sqlite3
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Creator Network",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "Creator Network"

# Local DB (works on Mac; on Streamlit Cloud it is ephemeral unless you use an external DB)
DB_PATH = Path("data") / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# =========================================================
# STYLES: light, energetic, trustworthy (female-friendly)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Page background */
.stApp {
  background:
    radial-gradient(900px 600px at 10% 10%, rgba(255, 107, 156, 0.18), transparent 60%),
    radial-gradient(900px 600px at 90% 5%, rgba(76, 201, 240, 0.16), transparent 55%),
    radial-gradient(900px 600px at 70% 90%, rgba(255, 196, 61, 0.10), transparent 60%),
    linear-gradient(180deg, #fbfbfe 0%, #f7f8ff 45%, #fbfbfe 100%);
}

/* Sidebar background a bit cleaner */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(255,255,255,0.86));
  border-right: 1px solid rgba(18, 20, 40, 0.08);
}

/* Headline / text colors */
h1, h2, h3, h4 { color: #111827; }
p, div, span, label { color: #111827; }

/* Containers */
.cn-hero {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(18,20,40,0.08);
  box-shadow: 0 10px 40px rgba(17, 24, 39, 0.06);
  border-radius: 22px;
  padding: 24px 22px;
  margin-bottom: 14px;
}

.cn-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(18,20,40,0.08);
  box-shadow: 0 10px 30px rgba(17, 24, 39, 0.05);
  border-radius: 18px;
  padding: 18px;
}

.cn-muted { color: rgba(17,24,39,0.65); font-size: 14px; }
.cn-micro { color: rgba(17,24,39,0.55); font-size: 12px; }

.cn-pill {
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(18,20,40,0.10);
  background: rgba(255,255,255,0.60);
  font-size: 12px;
  color: rgba(17,24,39,0.75);
  margin-right: 8px;
  margin-top: 8px;
}

.cn-pill-verified {
  border: 1px solid rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.10);
  color: rgba(6, 95, 70, 0.95);
}

/* Buttons - modern */
.stButton > button {
  border-radius: 14px !important;
  font-weight: 650 !important;
  padding: 10px 14px !important;
  border: 1px solid rgba(18,20,40,0.12) !important;
  background: white !important;
}

.stButton > button:hover {
  border-color: rgba(236,72,153,0.35) !important;
  box-shadow: 0 10px 20px rgba(236,72,153,0.10) !important;
}

/* Primary action button (we’ll use a CSS class via markdown wrappers) */
.cn-primary button {
  background: linear-gradient(90deg, #ec4899 0%, #8b5cf6 100%) !important;
  color: white !important;
  border: 0 !important;
}
.cn-primary button:hover {
  filter: brightness(1.05);
  box-shadow: 0 14px 28px rgba(139,92,246,0.18) !important;
}

/* Inputs slightly softer */
.stTextInput input, .stTextArea textarea, .stSelectbox div, .stNumberInput input {
  border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================
def db():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
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
    CREATE TABLE IF NOT EXISTS connections (
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

def insert_connection(a, b):
    conn = db()
    conn.execute("""
    INSERT INTO connections (a, b, created)
    VALUES (?, ?, ?)
    """, (a, b, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def read_connections(user):
    conn = db()
    df = pd.read_sql_query("""
        SELECT * FROM connections
        WHERE a = ? OR b = ?
        ORDER BY created DESC
    """, conn, params=(user, user))
    conn.close()
    return df

init_db()

# =========================================================
# SESSION STATE
# =========================================================
if "user" not in st.session_state:
    st.session_state.user = ""
if "_compose_to" not in st.session_state:
    st.session_state["_compose_to"] = ""
if "_pending_notice" not in st.session_state:
    st.session_state["_pending_notice"] = ""

# =========================================================
# SIDEBAR (NO WAITLIST)
# =========================================================
with st.sidebar:
    st.markdown(f"## {APP_NAME}")
    st.caption("Verified partnerships for creators and agencies.")
    st.markdown("---")

    st.session_state.user = st.text_input(
        "Your name (for messaging)",
        value=st.session_state.user,
        placeholder="e.g., Orel"
    )

    st.markdown("---")
    page = st.radio("Navigate", ["Overview", "Create Profile", "Marketplace", "Messages"], index=0)

    st.markdown("---")
    st.markdown("**Quick actions**")
    st.caption("Use Marketplace to search profiles, then connect + message.")

# =========================================================
# TOP HERO
# =========================================================
st.markdown(f"""
<div class="cn-hero">
  <div style="display:flex; justify-content:space-between; gap:16px; align-items:flex-start; flex-wrap:wrap;">
    <div style="max-width:780px;">
      <h1 style="margin:0; font-size:40px; line-height:1.05;">Verified partnerships for creators and agencies.</h1>
      <div class="cn-muted" style="margin-top:10px;">
        Stop the random DMs. Discover verified profiles, compare clear terms, and start partnerships with confidence.
      </div>
      <div style="margin-top:10px;">
        <span class="cn-pill">Trust-first</span>
        <span class="cn-pill">Transparent terms</span>
        <span class="cn-pill cn-pill-verified">Verification layer</span>
      </div>
    </div>
    <div style="text-align:right; min-width:220px;">
      <div class="cn-micro">Signed in as</div>
      <div style="font-weight:800; font-size:18px; margin-top:2px;">
        {st.session_state.user.strip() if st.session_state.user.strip() else "Guest"}
      </div>
      <div class="cn-micro" style="margin-top:10px;">
        Tip: Set your name to message and connect.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

profiles = read_profiles()

# =========================================================
# OVERVIEW / DASHBOARD
# =========================================================
if page == "Overview":
    # Metrics
    agencies = int((profiles["account_type"] == "Agency").sum()) if not profiles.empty else 0
    creators = int((profiles["account_type"] == "Creator").sum()) if not profiles.empty else 0
    verified = int((profiles["verified"] == 1).sum()) if not profiles.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    for col, title, value in [
        (c1, "Total Profiles", len(profiles)),
        (c2, "Agencies", agencies),
        (c3, "Creators", creators),
        (c4, "Verified Profiles", verified),
    ]:
        with col:
            st.markdown('<div class="cn-card">', unsafe_allow_html=True)
            st.metric(title, value)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### How it works")
    steps = st.columns(3)
    step_cards = [
        ("1) Create a profile", "Creators and agencies describe what they do, what they want, and their niche."),
        ("2) Discover verified partners", "Search and filter profiles. Verification highlights higher-trust accounts."),
        ("3) Connect + message", "Shortlist profiles and message with a clear intro and proposal."),
    ]
    for col, (h, p) in zip(steps, step_cards):
        with col:
            st.markdown('<div class="cn-card">', unsafe_allow_html=True)
            st.markdown(f"**{h}**")
            st.write(p)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Insights")
    if profiles.empty:
        st.info("No profiles yet. Start in **Create Profile**.")
    else:
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
            title="Revenue bucket (approx) by niche",
        )
        st.plotly_chart(fig, use_container_width=True)

# =========================================================
# CREATE PROFILE
# =========================================================
elif page == "Create Profile":
    st.markdown("### Create your profile")

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="cn-card">', unsafe_allow_html=True)
        account_type = st.selectbox("Account Type", ["Creator", "Agency"])
        name = st.text_input("Display Name", placeholder="Your brand / name")
        niche = st.text_input("Niche", placeholder="beauty, fitness, lifestyle, education...")
        location = st.text_input("Location", placeholder="City, Country")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cn-card">', unsafe_allow_html=True)

        if account_type == "Agency":
            revenue = st.selectbox("Monthly Revenue Managed", ["$0-10k", "$10-50k", "$50k+"])
            size = st.slider("Creators Managed", 0, 200, 5)
            bio = st.text_area(
                "Agency Bio",
                height=140,
                placeholder="What services do you provide? What results can you prove? Who is your ideal creator?"
            )
        else:
            revenue = st.selectbox("Monthly Revenue", ["$0-5k", "$5-20k", "$20k+"])
            size = st.slider("Audience Size (approx)", 0, 500000, 10000, step=5000)
            bio = st.text_area(
                "Creator Bio",
                height=140,
                placeholder="What do you create? What are your goals? What kind of partner are you looking for?"
            )

        # For now: keep verification as an internal flag (future: real verification workflow)
        verified = st.checkbox("Verified (admin only for now)", value=False)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
    publish = st.button("Publish Profile", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if publish:
        if not name.strip():
            st.error("Display Name is required.")
        else:
            insert_profile({
                "name": name.strip(),
                "account_type": account_type,
                "niche": niche.strip(),
                "revenue": revenue,
                "size": int(size),
                "location": location.strip(),
                "bio": bio.strip(),
                "verified": bool(verified),
                "created": datetime.now().isoformat()
            })
            st.success("Profile published.")
            st.rerun()

# =========================================================
# MARKETPLACE
# =========================================================
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

        st.caption(f"Showing **{len(df)}** profile(s).")

        for _, p in df.iterrows():
            st.markdown('<div class="cn-card">', unsafe_allow_html=True)
            top = st.columns([3, 1, 1])

            with top[0]:
                badges = ""
                if int(p["verified"]) == 1:
                    badges += '<span class="cn-pill cn-pill-verified">Verified</span>'
                badges += f'<span class="cn-pill">{p["account_type"]}</span>'
                st.markdown(badges, unsafe_allow_html=True)

                st.markdown(f"**{p['name']}**")
                st.caption(f"{p.get('niche','')} • {p.get('location','')} • {p.get('revenue','')}")
                bio_text = p.get("bio", "") or ""
                st.write(bio_text[:260] + ("..." if len(bio_text) > 260 else ""))

            with top[1]:
                if st.button("Message", key=f"msg_{p['id']}", use_container_width=True):
                    if not st.session_state.user.strip():
                        st.session_state["_pending_notice"] = "Set your name in the sidebar to message."
                    else:
                        st.session_state["_compose_to"] = p["name"]
                        st.session_state["_pending_notice"] = f"Compose a message to **{p['name']}** in Messages."
                        # soft navigation hint (user clicks Messages)
            with top[2]:
                if st.button("Connect", key=f"connect_{p['id']}", use_container_width=True):
                    if not st.session_state.user.strip():
                        st.session_state["_pending_notice"] = "Set your name in the sidebar to connect."
                    else:
                        insert_connection(st.session_state.user.strip(), p["name"])
                        st.session_state["_pending_notice"] = f"Connected with **{p['name']}** ✅"

            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state["_pending_notice"]:
            st.info(st.session_state["_pending_notice"])
            st.session_state["_pending_notice"] = ""

# =========================================================
# MESSAGES
# =========================================================
elif page == "Messages":
    st.markdown("### Messages")

    if not st.session_state.user.strip():
        st.warning("Set your name in the sidebar first.")
    else:
        user = st.session_state.user.strip()
        msgs = read_messages(user)
        connections = read_connections(user)

        left, right = st.columns([1, 1])

        with left:
            st.markdown('<div class="cn-card">', unsafe_allow_html=True)
            st.subheader("Compose")

            to_default = st.session_state.get("_compose_to", "")
            to = st.text_input("To (profile name)", value=to_default, placeholder="Type a profile name")
            body = st.text_area(
                "Message",
                height=140,
                placeholder="Quick intro + what you want + your next step.\nExample: “Hi, I’m … I saw your profile… Are you open to a 10-min call this week?”"
            )

            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            send = st.button("Send", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if send:
                if not to.strip() or not body.strip():
                    st.error("To + Message are required.")
                else:
                    insert_message(user, to.strip(), body.strip())
                    st.session_state["_compose_to"] = ""
                    st.success("Sent ✅")
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="cn-card">', unsafe_allow_html=True)
            st.subheader("Your connections")

            if connections.empty:
                st.caption("No connections yet. Use Marketplace to connect.")
            else:
                people = []
                for _, m in connections.iterrows():
                    other = m["b"] if m["a"] == user else m["a"]
                    people.append(other)
                for other in sorted(set(people)):
                    st.write(f"• {other}")

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
