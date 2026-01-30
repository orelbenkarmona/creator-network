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
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

APP_NAME = "Creator Network"
DB_PATH = Path("data") / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# =========================
# STYLES (premium / light / energetic)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"]  { font-family: 'Manrope', sans-serif; }

/* Hide Streamlit chrome (stable selectors) */
[data-testid="stHeader"] { display: none; }
[data-testid="stToolbar"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

/* App background */
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(900px 600px at 12% 8%, rgba(255,61,135,.18), transparent 60%),
    radial-gradient(900px 600px at 88% 10%, rgba(20,184,166,.14), transparent 55%),
    radial-gradient(900px 600px at 60% 92%, rgba(255,176,32,.12), transparent 60%),
    linear-gradient(180deg, #fff7fb 0%, #f4fbff 55%, #ffffff 100%);
}

/* Container width (fixes "empty page" vibe) */
.block-container { padding-top: 2.2rem !important; }
.cn-wrap{ max-width: 1120px; margin: 0 auto; }

/* Typography helpers */
.cn-muted { color: rgba(15, 23, 42, .66); }
.cn-title { font-weight: 900; color: #0f172a; letter-spacing: -0.02em; }

/* Cards */
.cn-card{
  background: rgba(255,255,255,.82);
  border: 1px solid rgba(15,23,42,.10);
  box-shadow: 0 18px 60px rgba(15, 23, 42, .08);
  backdrop-filter: blur(14px);
  border-radius: 24px;
  padding: 18px 18px;
}
.cn-hero{
  background: rgba(255,255,255,.86);
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 28px;
  padding: 22px 22px;
  box-shadow: 0 26px 90px rgba(15, 23, 42, .08);
}

/* Pills / badges */
.cn-pill{
  display:inline-flex;
  align-items:center;
  gap:.5rem;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.92);
  box-shadow: 0 10px 26px rgba(15,23,42,.06);
  border-radius: 999px;
  padding: .5rem .8rem;
  font-weight: 800;
  font-size: .82rem;
  color: rgba(15,23,42,.78);
  margin-right: .5rem;
}
.cn-dot{
  width: 10px; height: 10px; border-radius: 999px;
  background: rgba(20,184,166,.45);
  box-shadow: 0 0 0 6px rgba(20,184,166,.12);
}

/* Buttons (global) */
.stButton>button{
  border-radius: 16px !important;
  font-weight: 900 !important;
  padding: 12px 14px !important;
  border: 1px solid rgba(15,23,42,.10) !important;
}

/* Primary gradient wrapper (IMPORTANT: wrap st.button inside this div) */
.cn-primary button{
  background: linear-gradient(90deg, #ff3d87 0%, #7c3aed 100%) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 18px 34px rgba(255,61,135,.18);
}
.cn-primary button:hover{
  filter: brightness(1.03);
  transform: translateY(-1px);
}

/* Soft secondary */
.cn-ghost button{
  background: rgba(255,255,255,.9) !important;
}
.cn-ghost button:hover{
  box-shadow: 0 18px 40px rgba(15,23,42,.08);
  transform: translateY(-1px);
}

/* "3D" blob + float animation */
.cn-blob{
  position: relative;
  width: 100%;
  height: 360px;
  border-radius: 28px;
  border: 1px solid rgba(15,23,42,.08);
  background:
    radial-gradient(220px 220px at 30% 30%, rgba(255,61,135,.35), transparent 60%),
    radial-gradient(260px 260px at 75% 25%, rgba(20,184,166,.28), transparent 60%),
    radial-gradient(260px 260px at 60% 85%, rgba(255,176,32,.26), transparent 60%),
    linear-gradient(180deg, rgba(255,255,255,.85), rgba(255,255,255,.75));
  box-shadow: 0 30px 90px rgba(15,23,42,.08);
  overflow: hidden;
}

.cn-orb{
  position:absolute;
  width: 170px; height: 170px;
  border-radius: 999px;
  filter: blur(.2px);
  opacity: .95;
  animation: floaty 7.5s ease-in-out infinite;
}
.cn-orb.o1{
  left: 8%;
  top: 18%;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.65), rgba(255,61,135,.65));
}
.cn-orb.o2{
  right: 10%;
  top: 10%;
  width: 210px; height: 210px;
  animation-delay: -2.4s;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.65), rgba(20,184,166,.62));
}
.cn-orb.o3{
  right: 18%;
  bottom: -10%;
  width: 240px; height: 240px;
  animation-delay: -4.2s;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.65), rgba(124,58,237,.58));
}

@keyframes floaty{
  0%{ transform: translateY(0px) translateX(0px); }
  50%{ transform: translateY(-12px) translateX(6px); }
  100%{ transform: translateY(0px) translateX(0px); }
}

.cn-mini{
  position:absolute;
  left: 18px;
  bottom: 18px;
  right: 18px;
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
}
.cn-mini > div{
  flex: 1 1 160px;
  background: rgba(255,255,255,.86);
  border: 1px solid rgba(15,23,42,.08);
  border-radius: 18px;
  padding: 12px 12px;
  box-shadow: 0 18px 40px rgba(15,23,42,.06);
}

.cn-hr{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(15,23,42,.10), transparent);
  margin: 22px 0;
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
        account_type TEXT NOT NULL,
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
            row["niche"], row["location"], row["revenue"], row["size"],
            row["bio"], int(row["verified"]), existing[0]
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
# SESSION STATE (guided nav, no sidebar)
# =========================
if "auth_step" not in st.session_state:
    st.session_state.auth_step = "role"  # role -> name -> profile -> app
if "role" not in st.session_state:
    st.session_state.role = ""
if "user" not in st.session_state:
    st.session_state.user = ""
if "compose_to" not in st.session_state:
    st.session_state.compose_to = ""
if "screen" not in st.session_state:
    st.session_state.screen = "home"  # home / browse / messages / profile

def goto(screen: str):
    st.session_state.screen = screen
    st.rerun()

def hero_block(title: str, subtitle: str, pills: list[str]):
    pill_html = "".join([f'<span class="cn-pill"><span class="cn-dot"></span>{p}</span>' for p in pills])
    st.markdown(f"""
    <div class="cn-hero">
      <div class="cn-title" style="font-size:36px; line-height:1.05;">{title}</div>
      <div class="cn-muted" style="margin-top:10px; font-size:15px;">{subtitle}</div>
      <div style="margin-top:14px;">{pill_html}</div>
    </div>
    """, unsafe_allow_html=True)

def card_open():
    st.markdown('<div class="cn-card">', unsafe_allow_html=True)

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# WRAP (centered premium width)
# =========================
st.markdown('<div class="cn-wrap">', unsafe_allow_html=True)

profiles = read_profiles()

# =========================
# ONBOARDING (NO NAVBAR)
# =========================
if st.session_state.auth_step != "app":

    # ROLE
    if st.session_state.auth_step == "role":
        hero_block(
            "Choose your role",
            "This sets what you see inside the marketplace.",
            ["Trust-first", "Structured discovery", "Safe messaging"]
        )

        st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)

        left, right = st.columns([1.1, 1], gap="large")

        with left:
            card_open()
            st.markdown("### Start in 10 seconds")
            st.markdown('<div class="cn-muted">Pick what you are. You can switch later by signing out.</div>', unsafe_allow_html=True)
            st.write("")

            c1, c2 = st.columns(2, gap="medium")
            with c1:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                if st.button("I’m a Creator", use_container_width=True):
                    st.session_state.role = "Creator"
                    st.session_state.auth_step = "name"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                if st.button("I’m an Agency", use_container_width=True):
                    st.session_state.role = "Agency"
                    st.session_state.auth_step = "name"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            st.write("")
            st.markdown("#### What you get")
            st.markdown(
                """
                - Verified-style profiles (clean + high signal)
                - Private messaging inside the platform
                - Browse & compare partners without chaos
                """.strip()
            )
            card_close()

        with right:
            st.markdown("""
              <div class="cn-blob">
                <div class="cn-orb o1"></div>
                <div class="cn-orb o2"></div>
                <div class="cn-orb o3"></div>

                <div class="cn-mini">
                  <div>
                    <div style="font-weight:900;">Verified profiles</div>
                    <div class="cn-muted" style="margin-top:4px;">Clear info, less noise.</div>
                  </div>
                  <div>
                    <div style="font-weight:900;">Match faster</div>
                    <div class="cn-muted" style="margin-top:4px;">Niche + location filters.</div>
                  </div>
                  <div>
                    <div style="font-weight:900;">Safe messaging</div>
                    <div class="cn-muted" style="margin-top:4px;">No personal contact needed.</div>
                  </div>
                </div>
              </div>
            """, unsafe_allow_html=True)

        st.stop()

    # NAME
    if st.session_state.auth_step == "name":
        hero_block(
            f"Sign in as {st.session_state.role}",
            "Use your professional name/brand. You can edit later.",
            ["Fast onboarding", "No clutter", "Clean UI"]
        )

        st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)

        card_open()
        st.markdown("### Your display name")
        name = st.text_input("Name / Brand", placeholder="e.g., LunaFit or Aurora Media")
        st.write("")

        colA, colB = st.columns([1, 1])
        with colA:
            st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
            if st.button("Back", use_container_width=True):
                st.session_state.auth_step = "role"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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

        card_close()
        st.stop()

    # PROFILE
    if st.session_state.auth_step == "profile":
        role = st.session_state.role
        user = st.session_state.user

        hero_block(
            "Finish your profile",
            "Short, clean, and professional. You can update anytime.",
            ["High-signal profiles", "Better matches", "Trusted network"]
        )

        st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)

        card_open()
        st.markdown(f"### {role} profile")

        left, right = st.columns(2, gap="large")
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
            st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
            if st.button("Back", use_container_width=True):
                st.session_state.auth_step = "name"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

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

        card_close()
        st.stop()

# =========================
# MAIN APP (self navigating)
# =========================
role = st.session_state.role
user = st.session_state.user
profiles = read_profiles()

hero_block(
    f"Welcome, {user}",
    f"You are signed in as a {role}.",
    ["Marketplace", "Messaging", "Trust-first"]
)

st.write("")
a, b, c = st.columns(3, gap="medium")
with a:
    st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
    if st.button("Browse", use_container_width=True):
        goto("browse")
    st.markdown('</div>', unsafe_allow_html=True)
with b:
    st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
    if st.button("Messages", use_container_width=True):
        goto("messages")
    st.markdown('</div>', unsafe_allow_html=True)
with c:
    st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
    if st.button("My Profile", use_container_width=True):
        goto("profile")
    st.markdown('</div>', unsafe_allow_html=True)

# HOME
if st.session_state.screen == "home":
    st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)
    card_open()
    st.markdown("### What you can do now")
    if role == "Creator":
        st.markdown("- Browse agencies that match your niche/location")
        st.markdown("- Message an agency directly inside the platform")
        st.markdown("- Update your profile anytime")
    else:
        st.markdown("- Browse creators by niche/location")
        st.markdown("- Message creators directly inside the platform")
        st.markdown("- Update your profile anytime")
    card_close()

# BROWSE
elif st.session_state.screen == "browse":
    st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)
    card_open()

    target_type = "Agency" if role == "Creator" else "Creator"
    st.markdown(f"### Browse {target_type}s")

    q = st.text_input("Search (name, niche, location)", placeholder="e.g., beauty, London, fitness…")
    with st.expander("Advanced filters"):
        only_verified = st.checkbox("Verified only", value=False)

    df = profiles.copy()
    if not df.empty:
        df = df[df["account_type"] == target_type]

    if q.strip() and not df.empty:
        q2 = q.strip().lower()
        df = df[
            df["name"].str.lower().str.contains(q2, na=False) |
            df["niche"].str.lower().str.contains(q2, na=False) |
            df["location"].str.lower().str.contains(q2, na=False)
        ]

    if only_verified and not df.empty:
        df = df[df["verified"] == 1]

    st.write("")
    if df.empty:
        st.info(f"No {target_type.lower()} profiles yet.")
    else:
        for _, p in df.iterrows():
            st.markdown('<div class="cn-card" style="margin-bottom:14px;">', unsafe_allow_html=True)
            top = st.columns([3, 1], gap="medium")

            with top[0]:
                badge_line = f'<span class="cn-pill"><span class="cn-dot"></span>{p["account_type"]}</span>'
                if int(p["verified"]) == 1:
                    badge_line += f'<span class="cn-pill"><span class="cn-dot"></span>Verified</span>'
                st.markdown(badge_line, unsafe_allow_html=True)

                st.markdown(f"**{p['name']}**")
                st.caption(f"{p.get('niche','')} • {p.get('location','')} • {p.get('revenue','')}")
                bio = (p.get("bio","") or "")
                st.write(bio[:220] + ("..." if len(bio) > 220 else ""))

            with top[1]:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                msg = st.button("Message", key=f"m_{p['id']}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if msg:
                    st.session_state.compose_to = p["name"]
                    goto("messages")

            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
    if st.button("Back to home", use_container_width=True):
        goto("home")
    st.markdown('</div>', unsafe_allow_html=True)

    card_close()

# MESSAGES
elif st.session_state.screen == "messages":
    st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)
    inbox = read_inbox(user)

    left, right = st.columns([1, 1], gap="large")

    with left:
        card_open()
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

        st.write("")
        st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
        if st.button("Back to home", use_container_width=True):
            goto("home")
        st.markdown('</div>', unsafe_allow_html=True)

        card_close()

    with right:
        card_open()
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
        card_close()

# PROFILE
elif st.session_state.screen == "profile":
    st.markdown('<div class="cn-hr"></div>', unsafe_allow_html=True)
    card_open()
    st.markdown("### My profile")

    my = profiles[(profiles["name"] == user) & (profiles["account_type"] == role)]
    if my.empty:
        st.info("Profile not found. Please re-create it.")
        st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
        if st.button("Re-create profile", use_container_width=True):
            st.session_state.auth_step = "profile"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
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
        colA, colB = st.columns(2, gap="medium")
        with colA:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            if st.button("Edit profile", use_container_width=True):
                st.session_state.auth_step = "profile"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with colB:
            st.markdown('<div class="cn-ghost">', unsafe_allow_html=True)
            if st.button("Sign out", use_container_width=True):
                st.session_state.auth_step = "role"
                st.session_state.role = ""
                st.session_state.user = ""
                st.session_state.screen = "home"
                st.session_state.compose_to = ""
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    card_close()

# close wrap
st.markdown('</div>', unsafe_allow_html=True)
