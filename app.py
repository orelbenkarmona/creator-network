import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
from pathlib import Path

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Creator Network",
    page_icon="CN",
    layout="wide",
    initial_sidebar_state="collapsed"
)

APP_NAME = "Creator Network"
DB_PATH = Path("data") / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# =========================
# STYLES (light, energetic, trust)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  { font-family: 'Manrope', sans-serif; }

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Background */
.stApp {
  background:
    radial-gradient(900px 600px at 12% 8%, rgba(255,61,135,.18), transparent 60%),
    radial-gradient(900px 600px at 88% 10%, rgba(20,184,166,.14), transparent 55%),
    radial-gradient(900px 600px at 60% 92%, rgba(255,176,32,.12), transparent 60%),
    linear-gradient(180deg, #fff7fb 0%, #f4fbff 55%, #ffffff 100%);
}

/* Cards */
.cn-card {
  background: rgba(255,255,255,.76);
  border: 1px solid rgba(15,23,42,.10);
  box-shadow: 0 18px 60px rgba(15, 23, 42, .08);
  backdrop-filter: blur(14px);
  border-radius: 22px;
  padding: 18px 18px;
}

.cn-hero {
  background: rgba(255,255,255,.78);
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 28px;
  padding: 22px 22px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, .08);
}

.cn-muted { color: rgba(15, 23, 42, .65); }
.cn-title { font-weight: 800; color: #0f172a; }
.cn-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.70);
  font-size: 12px;
  color: rgba(15,23,42,.75);
  margin-right: 8px;
}
.cn-badge-verify{
  border: 1px solid rgba(20,184,166,.25);
  background: rgba(20,184,166,.10);
  color: rgba(6,95,70,1);
}

/* Buttons */
.stButton>button {
  border-radius: 16px !important;
  font-weight: 800 !important;
  padding: 10px 14px !important;
  border: 1px solid rgba(15,23,42,.10) !important;
}

.cn-primary button {
  background: linear-gradient(90deg, #ff3d87 0%, #7c3aed 100%) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 18px 30px rgba(255,61,135,.18);
}
.cn-primary button:hover {
  filter: brightness(1.03);
  transform: translateY(-1px);
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  border-radius: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DATABASE
# =========================
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
        account_type TEXT NOT NULL,   -- "Creator" or "Agency"
        niche TEXT,
        location TEXT,
        revenue TEXT,
        size INTEGER,
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

    conn.commit()
    conn.close()

def read_profiles():
    conn = db()
    df = pd.read_sql_query("SELECT * FROM profiles ORDER BY created DESC", conn)
    conn.close()
    return df

def upsert_profile(row: dict):
    conn = db()
    c = conn.cursor()

    # If user exists by name+type, update; else insert
    existing = c.execute(
        "SELECT id FROM profiles WHERE name = ? AND account_type = ?",
        (row["name"], row["account_type"])
    ).fetchone()

    if existing:
        c.execute("""
        UPDATE profiles
        SET niche=?, location=?, revenue=?, size=?, bio=?, verified=?
        WHERE id=?
        """, (
            row["niche"], row["location"], row["revenue"], row["size"], row["bio"], int(row["verified"]), existing[0]
        ))
    else:
        c.execute("""
        INSERT INTO profiles (name, account_type, niche, location, revenue, size, bio, verified, created)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["name"], row["account_type"], row["niche"], row["location"],
            row["revenue"], row["size"], row["bio"], int(row["verified"]), row["created"]
        ))

    conn.commit()
    conn.close()

def insert_message(sender, receiver, body):
    conn = db()
    conn.execute("""
    INSERT INTO messages (sender, receiver, body, created)
    VALUES (?, ?, ?, ?)
    """, (sender, receiver, body, datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()

def read_inbox(user):
    conn = db()
    df = pd.read_sql_query("""
        SELECT * FROM messages
        WHERE sender = ? OR receiver = ?
        ORDER BY created DESC
    """, conn, params=(user, user))
    conn.close()
    return df

init_db()

# =========================
# SESSION STATE (guided navigation)
# =========================
if "auth_step" not in st.session_state:
    st.session_state.auth_step = "role"   # role -> name -> profile -> app

if "role" not in st.session_state:
    st.session_state.role = ""

if "user" not in st.session_state:
    st.session_state.user = ""

if "compose_to" not in st.session_state:
    st.session_state.compose_to = ""

if "screen" not in st.session_state:
    st.session_state.screen = "home"      # home / browse / messages / profile

profiles = read_profiles()

# =========================
# HELPERS
# =========================
def hero(title, subtitle, badges):
    b = "".join([f'<span class="cn-badge">{x}</span>' for x in badges])
    st.markdown(f"""
    <div class="cn-hero">
      <div class="cn-title" style="font-size:34px; line-height:1.1;">{title}</div>
      <div class="cn-muted" style="margin-top:8px; font-size:15px;">{subtitle}</div>
      <div style="margin-top:14px;">{b}</div>
    </div>
    """, unsafe_allow_html=True)

def card_start():
    st.markdown('<div class="cn-card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

def goto(screen):
    st.session_state.screen = screen
    st.rerun()

# =========================
# ONBOARDING FLOW (no navbar)
# =========================
if st.session_state.auth_step != "app":
    # STEP 1: ROLE
    if st.session_state.auth_step == "role":
        hero(
            "Creator Network",
            "A professional matching engine for creators and agencies. Clear profiles. Faster partnerships.",
            ["Trust-first", "Business matching", "Safe messaging"]
        )

        st.write("")
        card_start()
        st.markdown("### Choose your account type")
        st.markdown('<div class="cn-muted">This sets what you see inside the app.</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            if st.button("I’m a Creator", use_container_width=True):
                st.session_state.role = "Creator"
                st.session_state.auth_step = "name"
                st.rerun()

        with col2:
            if st.button("I’m an Agency", use_container_width=True):
                st.session_state.role = "Agency"
                st.session_state.auth_step = "name"
                st.rerun()

        card_end()
        st.stop()

    # STEP 2: NAME (login)
    if st.session_state.auth_step == "name":
        hero(
            f"Sign in as {st.session_state.role}",
            "Use your professional name/brand. You can edit later.",
            ["Fast onboarding", "No clutter"]
        )
        st.write("")
        card_start()
        st.markdown("### Your display name")
        name = st.text_input("Name / Brand", placeholder="e.g., LunaFit or Aurora Media")

        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("Back", use_container_width=True):
                st.session_state.auth_step = "role"
                st.rerun()
        with colB:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            go = st.button("Continue", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if go:
            if not name.strip():
                st.error("Name is required.")
            else:
                st.session_state.user = name.strip()
                st.session_state.auth_step = "profile"
                st.rerun()

        card_end()
        st.stop()

    # STEP 3: PROFILE (minimal)
    if st.session_state.auth_step == "profile":
        role = st.session_state.role
        user = st.session_state.user

        hero(
            "Finish your profile",
            "Short, clean, and professional. You can update anytime.",
            ["High-signal profiles", "Less noise"]
        )

        st.write("")
        card_start()
        st.markdown(f"### {role} profile")

        left, right = st.columns([1, 1])

        with left:
            niche = st.text_input("Primary niche", placeholder="fitness, lifestyle, education, beauty…")
            location = st.text_input("Location", placeholder="City, Country")

        with right:
            if role == "Agency":
                revenue = st.selectbox("Monthly revenue managed", ["Prefer not to say", "$0-10k", "$10-50k", "$50k+"])
                size = st.slider("Creators managed", 0, 200, 5)
                bio = st.text_area("Agency bio (short)", height=120, placeholder="Results, process, what you offer. Keep it short.")
            else:
                revenue = st.selectbox("Monthly revenue", ["Prefer not to say", "$0-5k", "$5-20k", "$20k+"])
                size = st.slider("Audience size (approx)", 0, 500000, 10000, step=5000)
                bio = st.text_area("Creator bio (short)", height=120, placeholder="Your goals + what help you want. Keep it short.")

        st.write("")
        colA, colB = st.columns([1, 1])
        with colA:
            if st.button("Back", use_container_width=True):
                st.session_state.auth_step = "name"
                st.rerun()

        with colB:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            save = st.button("Enter the app", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if save:
            upsert_profile({
                "name": user,
                "account_type": role,
                "niche": niche.strip(),
                "location": location.strip(),
                "revenue": revenue,
                "size": int(size),
                "bio": bio.strip(),
                "verified": 0,
                "created": datetime.now().isoformat(timespec="seconds")
            })
            st.session_state.auth_step = "app"
            st.session_state.screen = "home"
            st.rerun()

        card_end()
        st.stop()

# =========================
# MAIN APP (role-based, self navigating)
# =========================
role = st.session_state.role
user = st.session_state.user

# Top hero
hero(
    f"Welcome, {user}",
    f"You are signed in as a {role}.",
    ["Marketplace", "Messaging", "Trust-first"]
)

# Minimal “top actions” (instead of nav bar)
st.write("")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Browse", use_container_width=True):
        goto("browse")
with col2:
    if st.button("Messages", use_container_width=True):
        goto("messages")
with col3:
    if st.button("My Profile", use_container_width=True):
        goto("profile")

# Screen renderer
profiles = read_profiles()

# HOME
if st.session_state.screen == "home":
    st.write("")
    card_start()
    st.markdown("### What you can do now")
    if role == "Creator":
        st.write("- Browse agencies that match your niche/location")
        st.write("- Message an agency directly inside the platform")
        st.write("- Update your profile anytime")
    else:
        st.write("- Browse creators by niche/location")
        st.write("- Message creators directly inside the platform")
        st.write("- Update your profile anytime")
    card_end()

# BROWSE
elif st.session_state.screen == "browse":
    st.write("")
    card_start()
    target_type = "Agency" if role == "Creator" else "Creator"
    st.markdown(f"### Browse {target_type}s")

    q = st.text_input("Search (name, niche, location)", placeholder="e.g., beauty, London, fitness…")
    adv = st.expander("Advanced filters")
    with adv:
        only_verified = st.checkbox("Verified only", value=False)

    df = profiles.copy()
    df = df[df["account_type"] == target_type] if not df.empty else df

    if q.strip() and not df.empty:
        q2 = q.strip().lower()
        df = df[
            df["name"].str.lower().str.contains(q2, na=False) |
            df["niche"].str.lower().str.contains(q2, na=False) |
            df["location"].str.lower().str.contains(q2, na=False)
        ]

    if only_verified and not df.empty:
        df = df[df["verified"] == 1]

    if df.empty:
        st.info(f"No {target_type.lower()} profiles yet.")
    else:
        for _, p in df.iterrows():
            st.markdown("<div class='cn-card hover-depth'>", unsafe_allow_html=True)
            top = st.columns([3, 1])

            with top[0]:
                badges = []
                if int(p["verified"]) == 1:
                    badges.append('<span class="cn-badge cn-badge-verify">Verified</span>')
                badges.append(f'<span class="cn-badge">{p["account_type"]}</span>')
                st.markdown("".join(badges), unsafe_allow_html=True)

                st.markdown(f"**{p['name']}**")
                st.caption(f"{p.get('niche','')} • {p.get('location','')} • {p.get('revenue','')}")
                bio = p.get("bio","") or ""
                st.write(bio[:220] + ("..." if len(bio) > 220 else ""))

            with top[1]:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                msg = st.button("Message", key=f"m_{p['id']}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if msg:
                    st.session_state.compose_to = p["name"]
                    goto("messages")

            st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    if st.button("Back to home", use_container_width=True):
        goto("home")

    card_end()

# MESSAGES
elif st.session_state.screen == "messages":
    st.write("")
    inbox = read_inbox(user)

    left, right = st.columns([1, 1])

    with left:
        card_start()
        st.markdown("### Compose")
        to_default = st.session_state.compose_to or ""
        to = st.text_input("To", value=to_default, placeholder="Type a name from marketplace")
        body = st.text_area("Message", height=140, placeholder="Short intro + what you want.")

        st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
        send = st.button("Send", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if send:
            if not to.strip() or not body.strip():
                st.error("To + message are required.")
            else:
                insert_message(user, to.strip(), body.strip())
                st.session_state.compose_to = ""
                st.success("Sent.")
                st.rerun()

        if st.button("Back to home", use_container_width=True):
            goto("home")

        card_end()

    with right:
        card_start()
        st.markdown("### Inbox (latest)")
        if inbox.empty:
            st.caption("No messages yet.")
        else:
            for _, m in inbox.head(10).iterrows():
                direction = "To" if m["sender"] == user else "From"
                other = m["receiver"] if m["sender"] == user else m["sender"]
                st.markdown(f"**{direction}: {other}**")
                st.write(m["body"])
                st.caption(m["created"])
                st.markdown("---")
        card_end()

# PROFILE
elif st.session_state.screen == "profile":
    st.write("")
    card_start()
    st.markdown("### My profile")

    # Find current profile
    my = profiles[(profiles["name"] == user) & (profiles["account_type"] == role)]
    if my.empty:
        st.info("Profile not found. Please re-create it.")
        if st.button("Re-create profile", use_container_width=True):
            st.session_state.auth_step = "profile"
            st.rerun()
    else:
        p = my.iloc[0]
        st.write(f"**Name:** {p['name']}")
        st.write(f"**Type:** {p['account_type']}")
        st.write(f"**Niche:** {p.get('niche','')}")
        st.write(f"**Location:** {p.get('location','')}")
        st.write(f"**Revenue:** {p.get('revenue','')}")
        st.write(f"**Size:** {p.get('size','')}")
        st.write("")
        st.write("**Bio:**")
        st.write(p.get("bio",""))

        st.write("")
        colA, colB = st.columns(2)
        with colA:
            if st.button("Edit profile", use_container_width=True):
                st.session_state.auth_step = "profile"
                st.rerun()
        with colB:
            if st.button("Sign out", use_container_width=True):
                st.session_state.auth_step = "role"
                st.session_state.role = ""
                st.session_state.user = ""
                st.session_state.screen = "home"
                st.session_state.compose_to = ""
                st.rerun()

    card_end()
