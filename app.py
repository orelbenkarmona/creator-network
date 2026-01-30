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

APP_URL = "https://creator-network-6txmkwhg8n8svvqnfmjipa.streamlit.app/"

# =========================
# STYLES (premium, light, energetic)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]  { font-family: 'Manrope', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Page background */
.stApp {
  background:
    radial-gradient(900px 600px at 12% 8%, rgba(255,61,135,.14), transparent 60%),
    radial-gradient(900px 600px at 88% 10%, rgba(20,184,166,.11), transparent 55%),
    radial-gradient(900px 600px at 60% 92%, rgba(255,176,32,.08), transparent 60%),
    linear-gradient(180deg, #f4fbff 0%, #ffffff 52%, #ffffff 100%);
}

/* Width polish */
.block-container { padding-top: 1.25rem; padding-bottom: 3rem; }

/* Card */
.cn-card{
  background: rgba(255,255,255,.82);
  border: 1px solid rgba(15,23,42,.10);
  box-shadow: 0 18px 55px rgba(15, 23, 42, .06);
  backdrop-filter: blur(10px);
  border-radius: 22px;
  padding: 18px 18px;
}

/* Subtle hover depth */
.hover-depth{
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.hover-depth:hover{
  transform: translateY(-2px);
  border-color: rgba(15,23,42,.14);
  box-shadow: 0 26px 70px rgba(15, 23, 42, .08);
}

.cn-muted { color: rgba(15, 23, 42, .64); }
.cn-title { font-weight: 800; color: #0f172a; }

/* Badges */
.cn-badge{
  display:inline-flex;
  align-items:center;
  gap:.45rem;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.78);
  font-size: 12px;
  color: rgba(15,23,42,.72);
}
.cn-badge-verify{
  border: 1px solid rgba(20,184,166,.25);
  background: rgba(20,184,166,.10);
  color: rgba(6,95,70,1);
}

/* Primary buttons */
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
  box-shadow: 0 18px 30px rgba(255,61,135,.14);
}
.cn-primary button:hover {
  filter: brightness(1.03);
  transform: translateY(-1px);
}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
  border-radius: 14px !important;
}

/* Segmented nav (radio) */
div[data-baseweb="radio"]{
  background: rgba(255,255,255,.80);
  border: 1px solid rgba(15,23,42,.08);
  box-shadow: 0 12px 40px rgba(15,23,42,.06);
  border-radius: 999px;
  padding: 8px 10px;
}
div[data-baseweb="radio"] > div {
  gap: 6px;
}
div[data-baseweb="radio"] label{
  background: transparent;
  border-radius: 999px;
  padding: 6px 12px;
  font-weight: 800;
  color: rgba(15,23,42,.65);
}
div[data-baseweb="radio"] label:hover{
  background: rgba(15,23,42,.04);
}
div[data-baseweb="radio"] input:checked + div{
  background: rgba(15,23,42,.06);
  border-radius: 999px;
}

/* Clean separators */
.cn-divider{
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(15,23,42,.10), transparent);
  margin: 16px 0;
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
# SESSION STATE
# =========================
if "auth_step" not in st.session_state:
    st.session_state.auth_step = "role"  # role -> name -> profile -> app

if "role" not in st.session_state:
    st.session_state.role = ""

if "user" not in st.session_state:
    st.session_state.user = ""

if "compose_to" not in st.session_state:
    st.session_state.compose_to = ""

if "nav" not in st.session_state:
    st.session_state.nav = "Home"

# =========================
# UI HELPERS
# =========================
def card_start(extra=""):
    st.markdown(f'<div class="cn-card {extra}">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)

def badge_row(items):
    html = " ".join(items)
    st.markdown(html, unsafe_allow_html=True)

def app_shell(user, role):
    top = st.columns([2.3, 3.6, 1.3])

    with top[0]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="cn-card" style="width:42px;height:42px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-weight:900;">
            CN
          </div>
          <div>
            <div class="cn-title" style="font-size:16px;line-height:1.1;">{APP_NAME}</div>
            <div class="cn-muted" style="font-size:12px;margin-top:2px;">Marketplace • Messaging • Trust</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with top[1]:
        st.radio(
            label="",
            options=["Home", "Browse", "Messages", "Profile"],
            horizontal=True,
            key="nav"
        )

    with top[2]:
        card_start()
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;gap:6px;">
          <div style="font-weight:900;">{user}</div>
          <div class="cn-muted" style="font-size:12px;">{role}</div>
        </div>
        """, unsafe_allow_html=True)

        colA, colB = st.columns(2)
        with colA:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            if st.button("Open", use_container_width=True):
                st.markdown(f"[Open app]({APP_URL})")
            st.markdown('</div>', unsafe_allow_html=True)

        with colB:
            if st.button("Sign out", use_container_width=True):
                st.session_state.auth_step = "role"
                st.session_state.role = ""
                st.session_state.user = ""
                st.session_state.compose_to = ""
                st.session_state.nav = "Home"
                st.rerun()
        card_end()

    st.markdown('<div class="cn-divider"></div>', unsafe_allow_html=True)

# =========================
# ONBOARDING FLOW (guided)
# =========================
profiles = read_profiles()

if st.session_state.auth_step != "app":

    # STEP 1: ROLE
    if st.session_state.auth_step == "role":
        card_start()
        st.markdown('<div class="cn-title" style="font-size:34px;line-height:1.1;">Choose your role</div>', unsafe_allow_html=True)
        st.markdown('<div class="cn-muted" style="margin-top:8px;">This sets what you see inside the marketplace.</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;'>"
                    "<span class='cn-badge cn-badge-verify'>Trust-first</span>"
                    "<span class='cn-badge'>Structured discovery</span>"
                    "<span class='cn-badge'>Safe messaging</span>"
                    "</div>", unsafe_allow_html=True)

        st.write("")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            if st.button("I’m a Creator", use_container_width=True):
                st.session_state.role = "Creator"
                st.session_state.auth_step = "name"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            if st.button("I’m an Agency", use_container_width=True):
                st.session_state.role = "Agency"
                st.session_state.auth_step = "name"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        card_end()
        st.stop()

    # STEP 2: NAME
    if st.session_state.auth_step == "name":
        card_start()
        st.markdown(f'<div class="cn-title" style="font-size:30px;">Sign in as {st.session_state.role}</div>', unsafe_allow_html=True)
        st.markdown('<div class="cn-muted" style="margin-top:8px;">Use your professional name/brand. You can edit later.</div>', unsafe_allow_html=True)

        st.write("")
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

    # STEP 3: PROFILE
    if st.session_state.auth_step == "profile":
        role = st.session_state.role
        user = st.session_state.user

        card_start()
        st.markdown('<div class="cn-title" style="font-size:30px;">Finish your profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="cn-muted" style="margin-top:8px;">Short, clean, and high-signal. You can update anytime.</div>', unsafe_allow_html=True)
        st.write("")

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
            st.session_state.nav = "Home"
            st.rerun()

        card_end()
        st.stop()

# =========================
# MAIN APP
# =========================
role = st.session_state.role
user = st.session_state.user
profiles = read_profiles()

app_shell(user, role)

# HOME
if st.session_state.nav == "Home":
    card_start("hover-depth")
    st.markdown('<div class="cn-title" style="font-size:26px;">Your next step</div>', unsafe_allow_html=True)
    st.markdown('<div class="cn-muted" style="margin-top:6px;">Do one thing, fast. No clutter.</div>', unsafe_allow_html=True)

    st.write("")
    if role == "Creator":
        st.markdown("**Recommended:** Browse agencies, shortlist 2, message 1.")
        st.markdown("- Filter by niche and location")
        st.markdown("- Compare commission expectations")
        st.markdown("- Start messaging inside the platform")
    else:
        st.markdown("**Recommended:** Browse creators, shortlist 3, message 2.")
        st.markdown("- Filter by niche and location")
        st.markdown("- See profile signals before reaching out")
        st.markdown("- Build a clean outreach pipeline")
    card_end()

    st.write("")
    cols = st.columns(3)
    with cols[0]:
        st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
        if st.button("Browse now", use_container_width=True):
            st.session_state.nav = "Browse"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with cols[1]:
        if st.button("Go to messages", use_container_width=True):
            st.session_state.nav = "Messages"
            st.rerun()
    with cols[2]:
        if st.button("View my profile", use_container_width=True):
            st.session_state.nav = "Profile"
            st.rerun()

# BROWSE
elif st.session_state.nav == "Browse":
    target_type = "Agency" if role == "Creator" else "Creator"

    card_start()
    st.markdown(f'<div class="cn-title" style="font-size:26px;">Browse {target_type}s</div>', unsafe_allow_html=True)
    st.markdown('<div class="cn-muted" style="margin-top:6px;">Search by name, niche, or location. Keep it high-signal.</div>', unsafe_allow_html=True)
    st.write("")

    q = st.text_input("Search", placeholder="e.g., beauty, London, fitness…")
    c1, c2 = st.columns([1, 1])
    with c1:
        only_verified = st.checkbox("Verified only", value=False)
    with c2:
        sort_by = st.selectbox("Sort", ["Newest", "Name (A-Z)"])

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

    if not df.empty:
        if sort_by == "Name (A-Z)":
            df = df.sort_values("name", ascending=True)
        else:
            df = df.sort_values("created", ascending=False)

    st.markdown('<div class="cn-divider"></div>', unsafe_allow_html=True)

    if df.empty:
        st.info(f"No {target_type.lower()} profiles found yet.")
    else:
        # Grid of cards
        cols = st.columns(2)
        for i, (_, p) in enumerate(df.iterrows()):
            with cols[i % 2]:
                card_start("hover-depth")
                badges = []
                if int(p.get("verified", 0)) == 1:
                    badges.append('<span class="cn-badge cn-badge-verify">Verified</span>')
                badges.append(f'<span class="cn-badge">{p["account_type"]}</span>')
                badge_row(badges)

                st.markdown(f'<div style="margin-top:10px;font-weight:900;font-size:18px;">{p["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="cn-muted" style="margin-top:4px;font-size:13px;">'
                            f'{(p.get("niche") or "").strip()}'
                            f'{(" • " if (p.get("niche") and p.get("location")) else "")}'
                            f'{(p.get("location") or "").strip()}'
                            f'{(" • " if (p.get("revenue")) else "")}'
                            f'{(p.get("revenue") or "").strip()}'
                            f'</div>', unsafe_allow_html=True)

                bio = (p.get("bio") or "").strip()
                if bio:
                    st.markdown(f'<div style="margin-top:10px;">{bio[:160]}{"..." if len(bio) > 160 else ""}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="cn-muted" style="margin-top:10px;">No bio yet.</div>', unsafe_allow_html=True)

                st.write("")
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                msg = st.button("Message", key=f"m_{p['id']}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                if msg:
                    st.session_state.compose_to = p["name"]
                    st.session_state.nav = "Messages"
                    st.rerun()

                card_end()

    card_end()

# MESSAGES
elif st.session_state.nav == "Messages":
    inbox = read_inbox(user)

    left, right = st.columns([1.05, 1.25])

    # Conversation list
    with left:
        card_start()
        st.markdown('<div class="cn-title" style="font-size:22px;">Inbox</div>', unsafe_allow_html=True)
        st.markdown('<div class="cn-muted" style="margin-top:6px;">Latest conversations.</div>', unsafe_allow_html=True)
        st.markdown('<div class="cn-divider"></div>', unsafe_allow_html=True)

        if inbox.empty:
            st.caption("No messages yet.")
        else:
            # Build convo list
            inbox["other"] = inbox.apply(lambda r: r["receiver"] if r["sender"] == user else r["sender"], axis=1)
            convos = inbox.groupby("other", as_index=False).first()  # latest per other
            for _, r in convos.iterrows():
                other = r["other"]
                preview = (r["body"] or "")[:80]
                when = r["created"]
                selected = (st.session_state.compose_to == other)

                st.markdown(
                    f"<div class='cn-card hover-depth' style='padding:14px;border-radius:18px;margin-bottom:10px;"
                    f"border-color:{'rgba(124,58,237,.22)' if selected else 'rgba(15,23,42,.10)'};'>"
                    f"<div style='font-weight:900'>{other}</div>"
                    f"<div class='cn-muted' style='font-size:12px;margin-top:3px;'>{preview}</div>"
                    f"<div class='cn-muted' style='font-size:11px;margin-top:6px;'>{when}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                if st.button("Open", key=f"open_{other}", use_container_width=True):
                    st.session_state.compose_to = other
                    st.rerun()

        card_end()

    # Thread + compose
    with right:
        card_start()
        st.markdown('<div class="cn-title" style="font-size:22px;">Conversation</div>', unsafe_allow_html=True)

        to_default = st.session_state.compose_to or ""
        to = st.text_input("To", value=to_default, placeholder="Type a name from Browse")

        st.markdown('<div class="cn-divider"></div>', unsafe_allow_html=True)

        if to.strip():
            thread = inbox.copy()
            if not thread.empty:
                # only messages between user and 'to'
                thread = thread[((thread["sender"] == user) & (thread["receiver"] == to.strip())) |
                                ((thread["sender"] == to.strip()) & (thread["receiver"] == user))]
            else:
                thread = pd.DataFrame()

            if thread.empty:
                st.markdown('<div class="cn-muted">No messages yet. Start with a short, professional intro.</div>', unsafe_allow_html=True)
            else:
                for _, m in thread.sort_values("created", ascending=True).tail(12).iterrows():
                    mine = (m["sender"] == user)
                    align = "flex-end" if mine else "flex-start"
                    bg = "rgba(124,58,237,.10)" if mine else "rgba(15,23,42,.05)"
                    st.markdown(
                        f"<div style='display:flex;justify-content:{align};margin:10px 0;'>"
                        f"<div style='max-width:78%;background:{bg};border:1px solid rgba(15,23,42,.08);"
                        f"border-radius:16px;padding:10px 12px;'>"
                        f"<div style='font-weight:900;font-size:12px;margin-bottom:4px;'>"
                        f"{'You' if mine else m['sender']}</div>"
                        f"<div>{m['body']}</div>"
                        f"<div class='cn-muted' style='font-size:11px;margin-top:6px;'>{m['created']}</div>"
                        f"</div></div>",
                        unsafe_allow_html=True
                    )

        st.write("")
        body = st.text_area("Message", height=120, placeholder="Short intro + what you want.")

        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("Clear", use_container_width=True):
                st.session_state.compose_to = ""
                st.rerun()

        with cols[1]:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            send = st.button("Send", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if send:
            if not to.strip() or not body.strip():
                st.error("To + message are required.")
            else:
                insert_message(user, to.strip(), body.strip())
                st.success("Sent.")
                st.rerun()

        card_end()

# PROFILE
elif st.session_state.nav == "Profile":
    card_start()
    st.markdown('<div class="cn-title" style="font-size:26px;">My profile</div>', unsafe_allow_html=True)
    st.markdown('<div class="cn-muted" style="margin-top:6px;">Keep it clean. High-signal beats long text.</div>', unsafe_allow_html=True)
    st.write("")

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
        badges = []
        if int(p.get("verified", 0)) == 1:
            badges.append('<span class="cn-badge cn-badge-verify">Verified</span>')
        badges.append(f'<span class="cn-badge">{p["account_type"]}</span>')
        badge_row(badges)

        st.markdown(f"<div style='margin-top:12px;font-weight:900;font-size:22px;'>{p['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='cn-muted' style='margin-top:4px;'>"
                    f"{(p.get('niche') or '').strip()} • {(p.get('location') or '').strip()} • {(p.get('revenue') or '').strip()}"
                    f"</div>", unsafe_allow_html=True)

        st.markdown('<div class="cn-divider"></div>', unsafe_allow_html=True)
        st.markdown("**Bio**")
        st.write((p.get("bio") or "").strip() or "No bio yet.")

        st.write("")
        colA, colB = st.columns(2)
        with colA:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            if st.button("Edit profile", use_container_width=True):
                st.session_state.auth_step = "profile"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with colB:
            if st.button("Go to Browse", use_container_width=True):
                st.session_state.nav = "Browse"
                st.rerun()

    card_end()
