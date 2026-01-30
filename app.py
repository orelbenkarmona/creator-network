import re
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

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
DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "app.db"
UPLOAD_DIR = DATA_DIR / "uploads"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# STYLES (premium, light, energetic, trust)
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"]  { font-family: 'Manrope', sans-serif; }

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

/* Layout max width similar to landing page */
.cn-shell { max-width: 1180px; margin: 0 auto; }

/* Cards */
.cn-card{
  background: rgba(255,255,255,.78);
  border: 1px solid rgba(15,23,42,.10);
  box-shadow: 0 18px 60px rgba(15, 23, 42, .08);
  backdrop-filter: blur(14px);
  border-radius: 22px;
  padding: 18px 18px;
}
.cn-hero{
  background: rgba(255,255,255,.82);
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 28px;
  padding: 22px 22px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, .08);
}
.cn-muted{ color: rgba(15, 23, 42, .65); }
.cn-title{ font-weight: 800; color: #0f172a; }
.cn-subtitle{ color: rgba(15,23,42,.65); font-size: 14px; }
.cn-badges { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; }
.cn-badge{
  display:inline-flex;
  align-items:center;
  gap:8px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(15,23,42,.10);
  background: rgba(255,255,255,.72);
  font-size: 12px;
  color: rgba(15,23,42,.75);
}
.cn-badge-verify{
  border: 1px solid rgba(20,184,166,.25);
  background: rgba(20,184,166,.10);
  color: rgba(6,95,70,1);
}
.cn-badge-warn{
  border: 1px solid rgba(255,176,32,.35);
  background: rgba(255,176,32,.14);
  color: rgba(146,64,14,1);
}

/* Primary button */
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
.cn-primary button:hover { filter: brightness(1.03); transform: translateY(-1px); }

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select, .stMultiSelect div[data-baseweb="select"] {
  border-radius: 14px !important;
}

/* Stepper */
.cn-stepper {
  display:flex; gap:10px; align-items:center; flex-wrap:wrap;
  margin: 6px 0 0 0;
}
.cn-dot{
  width: 10px; height: 10px;
  border-radius: 999px;
  background: rgba(15,23,42,.16);
}
.cn-dot.on{
  background: linear-gradient(90deg, #ff3d87 0%, #7c3aed 100%);
  box-shadow: 0 10px 18px rgba(124,58,237,.18);
}
.cn-step-label{ font-size: 12px; color: rgba(15,23,42,.55); }

/* Right-side brand mark (OF-style monogram, not the real logo file) */
.cn-mark-wrap{
  background: rgba(255,255,255,.75);
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 28px;
  box-shadow: 0 24px 80px rgba(15, 23, 42, .08);
  padding: 22px;
  min-height: 260px;
  position: relative;
  overflow: hidden;
}
.cn-mark-bg{
  position:absolute;
  inset: -80px -80px auto auto;
  width: 320px; height: 320px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(255,61,135,.35), rgba(124,58,237,.18), transparent 70%);
  filter: blur(0px);
}
.cn-mark-bg2{
  position:absolute;
  inset: auto -120px -120px auto;
  width: 340px; height: 340px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(20,184,166,.24), rgba(255,176,32,.18), transparent 70%);
}
.cn-of{
  width: 82px; height: 82px;
  border-radius: 26px;
  display:flex; align-items:center; justify-content:center;
  font-weight: 900;
  font-size: 32px;
  color: white;
  background: linear-gradient(90deg, #ff3d87 0%, #7c3aed 100%);
  box-shadow: 0 26px 50px rgba(124,58,237,.18);
}
.cn-mini{
  display:flex; gap:10px; margin-top: 16px; flex-wrap:wrap;
}
.cn-mini-card{
  background: rgba(255,255,255,.82);
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 18px;
  padding: 12px 12px;
  min-width: 170px;
}
.cn-mini-title{ font-weight: 800; font-size: 13px; color: #0f172a; }
.cn-mini-sub{ font-size: 12px; color: rgba(15,23,42,.62); margin-top: 4px; }

/* Small helper text */
.cn-help{ font-size: 12px; color: rgba(15,23,42,.60); }
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

    # Single table that supports both roles (creator + agency)
    c.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_type TEXT NOT NULL,              -- Creator / Agency

        display_name TEXT NOT NULL,              -- visible name
        created TEXT NOT NULL,

        -- Shared / marketplace
        niche TEXT,
        location_current TEXT,
        location_hometown TEXT,
        bio TEXT,
        verified INTEGER DEFAULT 0,              -- platform-verified (manual review placeholder)
        selfie_uploaded INTEGER DEFAULT 0,

        -- Creator fields
        creator_personality TEXT,
        creator_platform_handle TEXT,            -- e.g. handle on external subscription platform
        creator_platform_url TEXT,               -- link to profile
        creator_autofill INTEGER DEFAULT 0,       -- user chose "autofill" option
        creator_earnings_band TEXT,               -- stated band
        creator_content_types TEXT,               -- csv
        creator_photos TEXT,                      -- csv of local saved filenames

        -- Agency fields
        agency_name TEXT,
        agency_website TEXT,
        agency_success_story TEXT,
        agency_services TEXT,                     -- csv
        agency_content_specialties TEXT,          -- csv

        agency_payment_model TEXT,                -- fee / commission / other
        agency_fee_band TEXT,                     -- band
        agency_commission_band TEXT,              -- band
        agency_payment_other TEXT                 -- free text
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        created TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def _csv_join(x):
    if not x:
        return ""
    if isinstance(x, str):
        return x
    return ",".join([str(i) for i in x])

def _csv_split(x):
    if not x:
        return []
    return [i.strip() for i in str(x).split(",") if i.strip()]

def read_profiles():
    conn = db()
    df = pd.read_sql_query("SELECT * FROM profiles ORDER BY created DESC", conn)
    conn.close()
    return df

def get_profile_by_display_name(display_name, account_type):
    conn = db()
    df = pd.read_sql_query("""
        SELECT * FROM profiles
        WHERE display_name = ? AND account_type = ?
        ORDER BY created DESC
        LIMIT 1
    """, conn, params=(display_name, account_type))
    conn.close()
    return df

def upsert_profile(payload: dict):
    conn = db()
    c = conn.cursor()

    # "identity" = display_name + type
    existing = c.execute(
        "SELECT id FROM profiles WHERE display_name = ? AND account_type = ?",
        (payload["display_name"], payload["account_type"])
    ).fetchone()

    cols = list(payload.keys())
    vals = [payload[k] for k in cols]

    if existing:
        sets = ", ".join([f"{k}=?" for k in cols if k not in ("account_type", "display_name")])
        vals2 = [payload[k] for k in cols if k not in ("account_type", "display_name")]
        vals2.append(existing[0])
        q = f"UPDATE profiles SET {sets} WHERE id=?"
        c.execute(q, vals2)
        pid = existing[0]
    else:
        placeholders = ",".join(["?"] * len(cols))
        q = f"INSERT INTO profiles ({','.join(cols)}) VALUES ({placeholders})"
        c.execute(q, vals)
        pid = c.lastrowid

    conn.commit()
    conn.close()
    return pid

def insert_message(sender_id, receiver_id, body):
    conn = db()
    conn.execute("""
    INSERT INTO messages (sender_id, receiver_id, body, created)
    VALUES (?, ?, ?, ?)
    """, (sender_id, receiver_id, body, datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()

def read_inbox(profile_id):
    conn = db()
    df = pd.read_sql_query("""
        SELECT * FROM messages
        WHERE sender_id = ? OR receiver_id = ?
        ORDER BY created DESC
    """, conn, params=(profile_id, profile_id))
    conn.close()
    return df

def get_profile_id(display_name, account_type):
    conn = db()
    row = conn.execute("""
        SELECT id FROM profiles
        WHERE display_name = ? AND account_type = ?
        ORDER BY created DESC
        LIMIT 1
    """, (display_name, account_type)).fetchone()
    conn.close()
    return row[0] if row else None

def get_profile_by_id(pid):
    conn = db()
    df = pd.read_sql_query("SELECT * FROM profiles WHERE id = ?", conn, params=(pid,))
    conn.close()
    return df

init_db()

# =========================
# VALIDATION HELPERS
# =========================
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{6,}\d)")
def contains_phone(text: str) -> bool:
    if not text:
        return False
    return bool(PHONE_RE.search(text))

URL_RE = re.compile(r"^https?://", re.I)
def looks_like_url(x: str) -> bool:
    if not x:
        return False
    return bool(URL_RE.search(x.strip()))

def save_uploaded_files(files, prefix):
    saved = []
    if not files:
        return saved
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for i, f in enumerate(files):
        # Keep extension if present
        name = f.name
        ext = ""
        if "." in name:
            ext = "." + name.split(".")[-1].lower()
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", prefix)[:24]
        out = UPLOAD_DIR / f"{safe}_{ts}_{i}{ext}"
        out.write_bytes(f.getbuffer())
        saved.append(out.name)  # store only filename
    return saved

# =========================
# UI HELPERS
# =========================
def shell_open():
    st.markdown('<div class="cn-shell">', unsafe_allow_html=True)

def shell_close():
    st.markdown('</div>', unsafe_allow_html=True)

def hero(title, subtitle, badges=None):
    badges = badges or []
    badge_html = "".join([f'<span class="cn-badge">{b}</span>' for b in badges])
    st.markdown(f"""
    <div class="cn-hero">
      <div class="cn-title" style="font-size:34px; line-height:1.1;">{title}</div>
      <div class="cn-muted" style="margin-top:8px; font-size:15px;">{subtitle}</div>
      <div class="cn-badges">{badge_html}</div>
    </div>
    """, unsafe_allow_html=True)

def card_open():
    st.markdown('<div class="cn-card">', unsafe_allow_html=True)

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)

def stepper(current_idx, labels):
    dots = []
    for i in range(len(labels)):
        cls = "cn-dot on" if i <= current_idx else "cn-dot"
        dots.append(f'<span class="{cls}"></span>')
    st.markdown(f"""
    <div class="cn-stepper">
      {''.join(dots)}
      <span class="cn-step-label">{labels[current_idx]}</span>
    </div>
    """, unsafe_allow_html=True)

def right_mark():
    st.markdown("""
    <div class="cn-mark-wrap">
      <div class="cn-mark-bg"></div>
      <div class="cn-mark-bg2"></div>

      <div style="position:relative; z-index:2;">
        <div class="cn-of">OF</div>
        <div style="margin-top: 14px; font-weight:900; font-size:18px; color:#0f172a;">
          Creator onboarding
        </div>
        <div class="cn-subtitle" style="margin-top:6px;">
          Clean. Fast. Private. Built for trust.
        </div>

        <div class="cn-mini">
          <div class="cn-mini-card">
            <div class="cn-mini-title">Profile photos</div>
            <div class="cn-mini-sub">Add 3–6 images.</div>
          </div>
          <div class="cn-mini-card">
            <div class="cn-mini-title">Personality type</div>
            <div class="cn-mini-sub">Helps teams communicate.</div>
          </div>
          <div class="cn-mini-card">
            <div class="cn-mini-title">Verification</div>
            <div class="cn-mini-sub">Selfie upload (review).</div>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

def goto(screen):
    st.session_state.screen = screen
    st.rerun()

# =========================
# SESSION STATE
# =========================
if "auth_step" not in st.session_state:
    st.session_state.auth_step = "role"

if "role" not in st.session_state:
    st.session_state.role = ""

if "display_name" not in st.session_state:
    st.session_state.display_name = ""

if "profile_id" not in st.session_state:
    st.session_state.profile_id = None

if "screen" not in st.session_state:
    st.session_state.screen = "home"  # home/browse/messages/profile

if "compose_to_id" not in st.session_state:
    st.session_state.compose_to_id = None

# Creator onboarding draft
if "c_photos" not in st.session_state:
    st.session_state.c_photos = []
if "c_personality" not in st.session_state:
    st.session_state.c_personality = ""
if "c_current" not in st.session_state:
    st.session_state.c_current = ""
if "c_hometown" not in st.session_state:
    st.session_state.c_hometown = ""
if "c_niche" not in st.session_state:
    st.session_state.c_niche = ""
if "c_content_types" not in st.session_state:
    st.session_state.c_content_types = []
if "c_platform_mode" not in st.session_state:
    st.session_state.c_platform_mode = "Manual"
if "c_platform_handle" not in st.session_state:
    st.session_state.c_platform_handle = ""
if "c_platform_url" not in st.session_state:
    st.session_state.c_platform_url = ""
if "c_earnings_band" not in st.session_state:
    st.session_state.c_earnings_band = "Prefer not to say"
if "c_bio" not in st.session_state:
    st.session_state.c_bio = ""
if "c_selfie" not in st.session_state:
    st.session_state.c_selfie = None

# Agency onboarding draft
if "a_agency_name" not in st.session_state:
    st.session_state.a_agency_name = ""
if "a_website" not in st.session_state:
    st.session_state.a_website = ""
if "a_success" not in st.session_state:
    st.session_state.a_success = ""
if "a_services" not in st.session_state:
    st.session_state.a_services = []
if "a_specialties" not in st.session_state:
    st.session_state.a_specialties = []
if "a_payment_model" not in st.session_state:
    st.session_state.a_payment_model = "Commission-based"
if "a_fee_band" not in st.session_state:
    st.session_state.a_fee_band = "Prefer not to say"
if "a_commission_band" not in st.session_state:
    st.session_state.a_commission_band = "15–20%"
if "a_payment_other" not in st.session_state:
    st.session_state.a_payment_other = ""
if "a_location" not in st.session_state:
    st.session_state.a_location = ""
if "a_niche" not in st.session_state:
    st.session_state.a_niche = ""
if "a_bio" not in st.session_state:
    st.session_state.a_bio = ""

# =========================
# CONSTANTS / OPTIONS
# =========================
PERSONALITY_TYPES = [
    "Direct (short messages, clear asks)",
    "Friendly (warm tone, supportive)",
    "Professional (formal, structured)",
    "Low-contact (minimal check-ins)",
    "High-touch (frequent updates)",
    "Prefer to discuss later"
]

CONTENT_TYPES = [
    "Lifestyle", "Fitness", "Beauty", "Fashion", "Education", "Cosplay",
    "Gaming", "ASMR", "Couples", "Comedy", "Travel", "Other"
]

AGENCY_SERVICES = [
    "Account strategy", "Content planning", "Editing/post-production",
    "Chatting/DM management", "Promotion/marketing", "Brand deals",
    "Analytics/reporting", "Photoshoot support", "Operations/admin", "Other"
]

PAYMENT_MODELS = ["Commission-based", "Monthly fee", "Yearly fee", "Hybrid", "Other"]
FEE_BANDS = ["Prefer not to say", "$0–$500", "$500–$2k", "$2k–$5k", "$5k+"]
COMMISSION_BANDS = ["10–15%", "15–20%", "20–25%", "25%+", "Other / depends"]
EARNINGS_BANDS = ["Prefer not to say", "$0–$5k", "$5k–$20k", "$20k–$50k", "$50k+"]

# =========================
# ONBOARDING (Tinder-like flow)
# =========================
shell_open()

if st.session_state.auth_step != "app":
    # ROLE CHOICE
    if st.session_state.auth_step == "role":
        hero(
            "Choose your role",
            "This sets what you see inside the marketplace.",
            ["Trust-first", "Structured discovery", "Safe messaging"]
        )

        st.write("")
        cols = st.columns([1.35, 1])
        with cols[0]:
            card_open()
            st.markdown("### Start in 10 seconds")
            st.markdown('<div class="cn-help">Pick what you are. You can switch later by signing out.</div>', unsafe_allow_html=True)
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                if st.button("I’m a Creator", use_container_width=True):
                    st.session_state.role = "Creator"
                    st.session_state.auth_step = "name"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                if st.button("I’m an Agency", use_container_width=True):
                    st.session_state.role = "Agency"
                    st.session_state.auth_step = "name"
                    st.rerun()

            st.write("")
            st.markdown("### What you get")
            st.write("- Verified-style profiles (clean + high signal)")
            st.write("- Private messaging inside the platform")
            st.write("- Browse & compare partners without chaos")
            card_close()

        with cols[1]:
            right_mark()

        shell_close()
        st.stop()

    # NAME
    if st.session_state.auth_step == "name":
        role = st.session_state.role
        hero(
            f"Sign in as {role}",
            "Use a professional display name. You can edit later.",
            ["Fast onboarding", "No clutter", "Privacy-first"]
        )
        st.write("")
        card_open()
        display_name = st.text_input("Display name", value=st.session_state.display_name, placeholder="e.g., LunaFit or Aurora Media")
        st.markdown('<div class="cn-help">Tip: creators can use a brand name. Agencies should use their agency name.</div>', unsafe_allow_html=True)
        st.write("")
        b1, b2 = st.columns([1, 1])
        with b1:
            if st.button("Back", use_container_width=True):
                st.session_state.auth_step = "role"
                st.rerun()
        with b2:
            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            go = st.button("Continue", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if go:
            if not display_name.strip():
                st.error("Display name is required.")
            else:
                st.session_state.display_name = display_name.strip()
                st.session_state.auth_step = "creator_0" if role == "Creator" else "agency_0"
                st.rerun()

        card_close()
        shell_close()
        st.stop()

    # CREATOR FLOW (0..5)
    if st.session_state.role == "Creator":
        steps = [
            "Photos",
            "Basics",
            "Location",
            "Platform link",
            "Personality",
            "Verification"
        ]

        # Step 0: Photos
        if st.session_state.auth_step == "creator_0":
            hero("Creator signup", "Upload photos first — like Tinder. 3–6 is ideal.", ["High-signal profiles"])
            stepper(0, steps)
            st.write("")
            cols = st.columns([1.35, 1])

            with cols[0]:
                card_open()
                st.markdown("### Add profile photos")
                st.markdown('<div class="cn-help">These are used in the marketplace card (not public social links).</div>', unsafe_allow_html=True)

                files = st.file_uploader(
                    "Upload 3–6 photos",
                    type=["png", "jpg", "jpeg", "webp"],
                    accept_multiple_files=True
                )

                if files:
                    if len(files) < 1:
                        st.warning("Upload at least 1 photo.")
                    elif len(files) > 8:
                        st.warning("Max 8 photos for now.")
                    else:
                        st.session_state.c_photos = files

                st.write("")
                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("Back", use_container_width=True):
                        st.session_state.auth_step = "name"
                        st.rerun()
                with b2:
                    st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                    nxt = st.button("Next", use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                if nxt:
                    if not st.session_state.c_photos:
                        st.error("Please upload at least 1 photo.")
                    else:
                        st.session_state.auth_step = "creator_1"
                        st.rerun()

                card_close()

            with cols[1]:
                right_mark()

            shell_close()
            st.stop()

        # Step 1: Basics
        if st.session_state.auth_step == "creator_1":
            hero("Creator basics", "Keep it short, clean, professional.", ["Match faster", "Less noise"])
            stepper(1, steps)
            st.write("")
            card_open()

            st.session_state.c_niche = st.text_input("Primary niche", value=st.session_state.c_niche, placeholder="fitness, lifestyle, education, beauty…")
            st.session_state.c_content_types = st.multiselect("Content type(s)", options=CONTENT_TYPES, default=st.session_state.c_content_types)
            st.session_state.c_earnings_band = st.selectbox("Estimated monthly earnings (optional)", EARNINGS_BANDS, index=EARNINGS_BANDS.index(st.session_state.c_earnings_band))
            st.session_state.c_bio = st.text_area("Short bio", value=st.session_state.c_bio, height=120, placeholder="Goals + what you want from an agency. Keep it short.")

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "creator_0"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                st.session_state.auth_step = "creator_2"
                st.rerun()

            card_close()
            shell_close()
            st.stop()

        # Step 2: Location + hometown
        if st.session_state.auth_step == "creator_2":
            hero("Location", "Agencies use this for timezone + travel logistics.", ["Better fit", "Safer comms"])
            stepper(2, steps)
            st.write("")
            card_open()

            st.session_state.c_current = st.text_input("Current location", value=st.session_state.c_current, placeholder="City, Country")
            st.session_state.c_hometown = st.text_input("Hometown", value=st.session_state.c_hometown, placeholder="City, Country (optional)")

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "creator_1"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                st.session_state.auth_step = "creator_3"
                st.rerun()

            card_close()
            shell_close()
            st.stop()

        # Step 3: Platform link (manual vs autofill idea)
        if st.session_state.auth_step == "creator_3":
            hero("Link your platform", "Optional autofill flow is a product feature — for now we store the link/handle.", ["Verification signal", "Less manual input"])
            stepper(3, steps)
            st.write("")
            card_open()

            st.session_state.c_platform_mode = st.radio(
                "How do you want to add your info?",
                ["Manual", "Link + (future) Autofill"],
                index=0 if st.session_state.c_platform_mode == "Manual" else 1,
                horizontal=True
            )

            st.session_state.c_platform_handle = st.text_input("Platform handle (optional)", value=st.session_state.c_platform_handle, placeholder="@yourhandle")
            st.session_state.c_platform_url = st.text_input("Platform profile URL (optional)", value=st.session_state.c_platform_url, placeholder="https://...")

            if st.session_state.c_platform_url and not looks_like_url(st.session_state.c_platform_url):
                st.warning("URL should start with http:// or https://")

            st.markdown('<div class="cn-help">Note: autofill/earnings pull requires an integration. We can add it later.</div>', unsafe_allow_html=True)

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "creator_2"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                st.session_state.auth_step = "creator_4"
                st.rerun()

            card_close()
            shell_close()
            st.stop()

        # Step 4: Personality type
        if st.session_state.auth_step == "creator_4":
            hero("Communication style", "Helps agencies communicate safely and correctly.", ["Fewer misunderstandings"])
            stepper(4, steps)
            st.write("")
            card_open()

            st.session_state.c_personality = st.selectbox("Personality / communication style", PERSONALITY_TYPES, index=0 if not st.session_state.c_personality else PERSONALITY_TYPES.index(st.session_state.c_personality) if st.session_state.c_personality in PERSONALITY_TYPES else 0)

            st.markdown('<div class="cn-help">This is shown to agencies to set tone + boundaries.</div>', unsafe_allow_html=True)

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "creator_3"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                st.session_state.auth_step = "creator_5"
                st.rerun()

            card_close()
            shell_close()
            st.stop()

        # Step 5: Facial/selfie verification (placeholder for review)
        if st.session_state.auth_step == "creator_5":
            hero("Verification", "Upload a selfie for verification review.", ["Trust-first", "Higher match quality"])
            stepper(5, steps)
            st.write("")
            card_open()

            selfie = st.file_uploader("Selfie verification (1 image)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=False)
            st.session_state.c_selfie = selfie

            st.write("")
            consent = st.checkbox("I confirm this selfie is mine and I consent to verification review.", value=False)

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "creator_4"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                finish = st.button("Finish & enter app", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if finish:
                if not consent:
                    st.error("Please confirm consent to continue.")
                else:
                    # Save uploads
                    photos_saved = save_uploaded_files(st.session_state.c_photos, f"creator_{st.session_state.display_name}")
                    selfie_saved = save_uploaded_files([selfie], f"selfie_{st.session_state.display_name}") if selfie else []

                    payload = {
                        "account_type": "Creator",
                        "display_name": st.session_state.display_name,
                        "created": datetime.now().isoformat(timespec="seconds"),

                        "niche": st.session_state.c_niche.strip(),
                        "location_current": st.session_state.c_current.strip(),
                        "location_hometown": st.session_state.c_hometown.strip(),
                        "bio": st.session_state.c_bio.strip(),
                        "verified": 0,
                        "selfie_uploaded": 1 if selfie_saved else 0,

                        "creator_personality": st.session_state.c_personality,
                        "creator_platform_handle": st.session_state.c_platform_handle.strip(),
                        "creator_platform_url": st.session_state.c_platform_url.strip(),
                        "creator_autofill": 1 if st.session_state.c_platform_mode != "Manual" else 0,
                        "creator_earnings_band": st.session_state.c_earnings_band,
                        "creator_content_types": _csv_join(st.session_state.c_content_types),
                        "creator_photos": _csv_join(photos_saved),

                        "agency_name": None,
                        "agency_website": None,
                        "agency_success_story": None,
                        "agency_services": None,
                        "agency_content_specialties": None,
                        "agency_payment_model": None,
                        "agency_fee_band": None,
                        "agency_commission_band": None,
                        "agency_payment_other": None
                    }

                    pid = upsert_profile(payload)
                    st.session_state.profile_id = pid
                    st.session_state.auth_step = "app"
                    st.session_state.screen = "home"
                    st.rerun()

            card_close()
            shell_close()
            st.stop()

    # AGENCY FLOW (0..3)
    if st.session_state.role == "Agency":
        steps = ["Identity", "Proof", "Services", "Payment"]

        if st.session_state.auth_step == "agency_0":
            hero("Agency signup", "Build a LinkedIn/CV style profile. Website only. No phone numbers.", ["High-quality leads"])
            stepper(0, steps)
            st.write("")
            card_open()

            st.session_state.a_agency_name = st.text_input("Agency name", value=st.session_state.a_agency_name, placeholder="Aurora Management")
            st.session_state.a_website = st.text_input("Website (required)", value=st.session_state.a_website, placeholder="https://youragency.com")
            st.session_state.a_location = st.text_input("Location", value=st.session_state.a_location, placeholder="City, Country")
            st.session_state.a_niche = st.text_input("Primary niche focus", value=st.session_state.a_niche, placeholder="fitness, beauty, lifestyle...")

            bad = False
            if not st.session_state.a_website.strip():
                st.warning("Website is required (no phone numbers).")
                bad = True
            if st.session_state.a_website and not looks_like_url(st.session_state.a_website):
                st.warning("Website should start with http:// or https://")
                bad = True

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "name"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                if bad:
                    st.error("Fix the website field to continue.")
                else:
                    st.session_state.auth_step = "agency_1"
                    st.rerun()

            card_close()
            shell_close()
            st.stop()

        if st.session_state.auth_step == "agency_1":
            hero("Early success story", "Short proof beats long marketing.", ["Signal > noise"])
            stepper(1, steps)
            st.write("")
            card_open()

            st.session_state.a_success = st.text_area(
                "One strong success story (required)",
                value=st.session_state.a_success,
                height=140,
                placeholder="Example: Took a creator from $X to $Y/month in 90 days via content strategy + messaging + ads..."
            )

            if contains_phone(st.session_state.a_success):
                st.error("Remove phone number(s). Website only.")

            st.session_state.a_bio = st.text_area(
                "Agency bio (short)",
                value=st.session_state.a_bio,
                height=120,
                placeholder="What you offer, how you work, what your standards are."
            )

            if contains_phone(st.session_state.a_bio):
                st.error("Remove phone number(s). Website only.")

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "agency_0"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                if not st.session_state.a_success.strip():
                    st.error("Success story is required.")
                elif contains_phone(st.session_state.a_success) or contains_phone(st.session_state.a_bio):
                    st.error("Remove phone number(s).")
                else:
                    st.session_state.auth_step = "agency_2"
                    st.rerun()

            card_close()
            shell_close()
            st.stop()

        if st.session_state.auth_step == "agency_2":
            hero("Services & specialties", "Tell creators exactly what you do.", ["Better matching"])
            stepper(2, steps)
            st.write("")
            card_open()

            st.session_state.a_services = st.multiselect("Services you offer", AGENCY_SERVICES, default=st.session_state.a_services)
            st.session_state.a_specialties = st.multiselect("Best content categories you manage", CONTENT_TYPES, default=st.session_state.a_specialties)

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "agency_1"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                nxt = st.button("Next", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if nxt:
                st.session_state.auth_step = "agency_3"
                st.rerun()

            card_close()
            shell_close()
            st.stop()

        if st.session_state.auth_step == "agency_3":
            hero("Payment expectations", "Creators should know how you charge — upfront.", ["Transparent terms"])
            stepper(3, steps)
            st.write("")
            card_open()

            st.session_state.a_payment_model = st.selectbox("Payment model", PAYMENT_MODELS, index=PAYMENT_MODELS.index(st.session_state.a_payment_model))

            if st.session_state.a_payment_model in ("Monthly fee", "Yearly fee", "Hybrid"):
                st.session_state.a_fee_band = st.selectbox("Fee expectation", FEE_BANDS, index=FEE_BANDS.index(st.session_state.a_fee_band))
            else:
                st.session_state.a_fee_band = "Prefer not to say"

            if st.session_state.a_payment_model in ("Commission-based", "Hybrid"):
                st.session_state.a_commission_band = st.selectbox("Commission expectation", COMMISSION_BANDS, index=COMMISSION_BANDS.index(st.session_state.a_commission_band))
            else:
                st.session_state.a_commission_band = "Other / depends"

            if st.session_state.a_payment_model == "Other":
                st.session_state.a_payment_other = st.text_area("Describe your payment structure", value=st.session_state.a_payment_other, height=120, placeholder="No phone numbers. Website only.")
                if contains_phone(st.session_state.a_payment_other):
                    st.error("Remove phone number(s). Website only.")
            else:
                st.session_state.a_payment_other = ""

            st.write("")
            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("Back", use_container_width=True):
                    st.session_state.auth_step = "agency_2"
                    st.rerun()
            with b2:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                finish = st.button("Finish & enter app", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if finish:
                if contains_phone(st.session_state.a_payment_other):
                    st.error("Remove phone number(s).")
                else:
                    payload = {
                        "account_type": "Agency",
                        "display_name": st.session_state.display_name,
                        "created": datetime.now().isoformat(timespec="seconds"),

                        "niche": st.session_state.a_niche.strip(),
                        "location_current": st.session_state.a_location.strip(),
                        "location_hometown": "",
                        "bio": st.session_state.a_bio.strip(),
                        "verified": 0,
                        "selfie_uploaded": 0,

                        "creator_personality": None,
                        "creator_platform_handle": None,
                        "creator_platform_url": None,
                        "creator_autofill": 0,
                        "creator_earnings_band": None,
                        "creator_content_types": None,
                        "creator_photos": None,

                        "agency_name": st.session_state.a_agency_name.strip() or st.session_state.display_name,
                        "agency_website": st.session_state.a_website.strip(),
                        "agency_success_story": st.session_state.a_success.strip(),
                        "agency_services": _csv_join(st.session_state.a_services),
                        "agency_content_specialties": _csv_join(st.session_state.a_specialties),

                        "agency_payment_model": st.session_state.a_payment_model,
                        "agency_fee_band": st.session_state.a_fee_band,
                        "agency_commission_band": st.session_state.a_commission_band,
                        "agency_payment_other": st.session_state.a_payment_other.strip()
                    }

                    pid = upsert_profile(payload)
                    st.session_state.profile_id = pid
                    st.session_state.auth_step = "app"
                    st.session_state.screen = "home"
                    st.rerun()

            card_close()
            shell_close()
            st.stop()

# =========================
# MAIN APP
# =========================
profiles = read_profiles()

role = st.session_state.role
display_name = st.session_state.display_name
profile_id = st.session_state.profile_id

# Safety fallback: if state lost, recover profile_id from DB
if profile_id is None and display_name and role:
    pid = get_profile_id(display_name, role)
    st.session_state.profile_id = pid
    profile_id = pid

# Header / hero
hero(
    f"Welcome, {display_name}",
    f"You are signed in as a {role}.",
    ["Marketplace", "Messaging", "Trust-first"]
)

st.write("")

# Top actions (no navbar)
a, b, c = st.columns(3)
with a:
    if st.button("Browse", use_container_width=True):
        goto("browse")
with b:
    if st.button("Messages", use_container_width=True):
        goto("messages")
with c:
    if st.button("My Profile", use_container_width=True):
        goto("profile")

# =========================
# HOME
# =========================
if st.session_state.screen == "home":
    st.write("")
    card_open()
    st.markdown("### What you can do now")

    if role == "Creator":
        st.write("- Browse agencies by services + payment model")
        st.write("- Message agencies inside the platform")
        st.write("- Keep your personal contacts private")
    else:
        st.write("- Browse creators by niche + location + personality type")
        st.write("- Message creators inside the platform")
        st.write("- Show services + terms clearly to attract better creators")

    card_close()

# =========================
# BROWSE
# =========================
elif st.session_state.screen == "browse":
    st.write("")
    card_open()

    target_type = "Agency" if role == "Creator" else "Creator"
    st.markdown(f"### Browse {target_type}s")

    q = st.text_input("Search (name, niche, location)", placeholder="e.g., beauty, London, fitness…")
    adv = st.expander("Filters")
    with adv:
        only_verified = st.checkbox("Verified only", value=False)
        if role == "Creator":
            service_filter = st.multiselect("Agency services", AGENCY_SERVICES, default=[])
            pay_filter = st.multiselect("Payment model", PAYMENT_MODELS, default=[])
        else:
            personality_filter = st.multiselect("Creator personality style", PERSONALITY_TYPES, default=[])
            content_filter = st.multiselect("Content types", CONTENT_TYPES, default=[])

    df = profiles.copy()
    df = df[df["account_type"] == target_type] if not df.empty else df

    if only_verified and not df.empty:
        df = df[df["verified"] == 1]

    if q.strip() and not df.empty:
        q2 = q.strip().lower()
        df = df[
            df["display_name"].str.lower().str.contains(q2, na=False) |
            df["niche"].str.lower().str.contains(q2, na=False) |
            df["location_current"].str.lower().str.contains(q2, na=False)
        ]

    # Role-specific filters
    if not df.empty and role == "Creator":
        if service_filter:
            df = df[df["agency_services"].fillna("").apply(lambda x: any(s in _csv_split(x) for s in service_filter))]
        if pay_filter:
            df = df[df["agency_payment_model"].fillna("").isin(pay_filter)]

    if not df.empty and role == "Agency":
        if personality_filter:
            df = df[df["creator_personality"].fillna("").isin(personality_filter)]
        if content_filter:
            df = df[df["creator_content_types"].fillna("").apply(lambda x: any(s in _csv_split(x) for s in content_filter))]

    if df.empty:
        st.info(f"No {target_type.lower()} profiles found yet.")
    else:
        # Render cards
        for _, p in df.iterrows():
            # Card wrapper
            st.markdown('<div class="cn-card" style="margin-bottom:12px;">', unsafe_allow_html=True)
            top = st.columns([3, 1])

            # Left
            with top[0]:
                badges = []
                if int(p.get("verified", 0) or 0) == 1:
                    badges.append('<span class="cn-badge cn-badge-verify">Verified</span>')
                if target_type == "Creator" and int(p.get("selfie_uploaded", 0) or 0) == 1:
                    badges.append('<span class="cn-badge">Selfie uploaded</span>')
                badges.append(f'<span class="cn-badge">{p["account_type"]}</span>')
                st.markdown("".join(badges), unsafe_allow_html=True)

                title = p.get("agency_name") if target_type == "Agency" else p.get("display_name")
                st.markdown(f"**{title or p.get('display_name','')}**")

                meta = []
                if p.get("niche"):
                    meta.append(str(p.get("niche")))
                if p.get("location_current"):
                    meta.append(str(p.get("location_current")))
                st.caption(" • ".join(meta) if meta else "")

                if target_type == "Creator":
                    # Show creator signals
                    ct = _csv_split(p.get("creator_content_types", ""))
                    if ct:
                        st.write(f"**Content:** {', '.join(ct[:6])}")
                    if p.get("creator_personality"):
                        st.write(f"**Style:** {p.get('creator_personality')}")
                    if p.get("creator_earnings_band"):
                        st.write(f"**Earnings (band):** {p.get('creator_earnings_band')}")
                else:
                    # Show agency signals
                    sv = _csv_split(p.get("agency_services", ""))
                    if sv:
                        st.write(f"**Services:** {', '.join(sv[:6])}")
                    if p.get("agency_payment_model"):
                        st.write(f"**Payment:** {p.get('agency_payment_model')}")
                    if p.get("agency_commission_band") and p.get("agency_payment_model") in ("Commission-based", "Hybrid"):
                        st.write(f"**Commission:** {p.get('agency_commission_band')}")
                    if p.get("agency_fee_band") and p.get("agency_payment_model") in ("Monthly fee", "Yearly fee", "Hybrid"):
                        st.write(f"**Fee:** {p.get('agency_fee_band')}")
                    if p.get("agency_website"):
                        st.write(f"**Website:** {p.get('agency_website')}")

                bio = (p.get("bio") or "").strip()
                if bio:
                    st.write(bio[:240] + ("..." if len(bio) > 240 else ""))

            # Right actions
            with top[1]:
                st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
                msg = st.button("Message", key=f"msg_{p['id']}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                if msg:
                    st.session_state.compose_to_id = int(p["id"])
                    goto("messages")

            st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    if st.button("Back to home", use_container_width=True):
        goto("home")

    card_close()

# =========================
# MESSAGES
# =========================
elif st.session_state.screen == "messages":
    st.write("")
    card_open()

    if not profile_id:
        st.error("Profile not found. Please sign out and sign in again.")
        card_close()
    else:
        inbox = read_inbox(profile_id)

        left, right = st.columns([1, 1])

        with left:
            st.markdown("### Compose")

            # Choose receiver
            candidates = profiles[profiles["id"] != profile_id].copy()
            display_map = []
            for _, row in candidates.iterrows():
                label = f'{row["display_name"]} ({row["account_type"]})'
                display_map.append((label, int(row["id"])))

            # Default compose target
            default_id = st.session_state.compose_to_id
            default_index = 0
            if default_id and display_map:
                for i, (_, pid) in enumerate(display_map):
                    if pid == default_id:
                        default_index = i
                        break

            if display_map:
                choice = st.selectbox("To", options=display_map, format_func=lambda x: x[0], index=default_index)
                to_id = choice[1]
            else:
                st.info("No other profiles yet.")
                to_id = None

            body = st.text_area("Message", height=140, placeholder="Short intro + what you want.")

            st.markdown('<div class="cn-primary">', unsafe_allow_html=True)
            send = st.button("Send", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if send:
                if not to_id or not body.strip():
                    st.error("Pick a receiver and write a message.")
                else:
                    insert_message(profile_id, to_id, body.strip())
                    st.session_state.compose_to_id = None
                    st.success("Sent.")
                    st.rerun()

            st.write("")
            if st.button("Back to home", use_container_width=True):
                goto("home")

        with right:
            st.markdown("### Inbox (latest)")
            if inbox.empty:
                st.caption("No messages yet.")
            else:
                # Build map id->name
                id_to_name = {int(r["id"]): f'{r["display_name"]} ({r["account_type"]})' for _, r in profiles.iterrows()}
                for _, m in inbox.head(12).iterrows():
                    sender = id_to_name.get(int(m["sender_id"]), f"User {m['sender_id']}")
                    receiver = id_to_name.get(int(m["receiver_id"]), f"User {m['receiver_id']}")
                    direction = "To" if int(m["sender_id"]) == int(profile_id) else "From"
                    other = receiver if direction == "To" else sender

                    st.markdown(f"**{direction}: {other}**")
                    st.write(m["body"])
                    st.caption(m["created"])
                    st.markdown("---")

    card_close()

# =========================
# PROFILE
# =========================
elif st.session_state.screen == "profile":
    st.write("")
    card_open()
    st.markdown("### My profile")

    if not profile_id:
        st.error("Profile not found. Please sign out and sign in again.")
    else:
        df = get_profile_by_id(profile_id)
        if df.empty:
            st.error("Profile missing. Please sign out and re-create.")
        else:
            p = df.iloc[0]
            badges = []
            if int(p.get("verified", 0) or 0) == 1:
                badges.append('<span class="cn-badge cn-badge-verify">Verified</span>')
            if int(p.get("selfie_uploaded", 0) or 0) == 1:
                badges.append('<span class="cn-badge">Selfie uploaded</span>')
            badges.append(f'<span class="cn-badge">{p.get("account_type")}</span>')
            st.markdown("".join(badges), unsafe_allow_html=True)

            st.write(f"**Display name:** {p.get('display_name','')}")
            st.write(f"**Niche:** {p.get('niche','')}")
            st.write(f"**Location:** {p.get('location_current','')}")
            if p.get("location_hometown"):
                st.write(f"**Hometown:** {p.get('location_hometown','')}")

            if p.get("account_type") == "Creator":
                if p.get("creator_personality"):
                    st.write(f"**Style:** {p.get('creator_personality')}")
                if p.get("creator_earnings_band"):
                    st.write(f"**Earnings (band):** {p.get('creator_earnings_band')}")
                if p.get("creator_platform_url"):
                    st.write(f"**Platform URL:** {p.get('creator_platform_url')}")
                if p.get("creator_platform_handle"):
                    st.write(f"**Handle:** {p.get('creator_platform_handle')}")

                photos = _csv_split(p.get("creator_photos", ""))
                if photos:
                    st.write("")
                    st.markdown("**Photos**")
                    # show as thumbnails
                    cols = st.columns(min(4, len(photos)))
                    for i, fn in enumerate(photos[:8]):
                        img_path = UPLOAD_DIR / fn
                        if img_path.exists():
                            cols[i % len(cols)].image(str(img_path), use_container_width=True)

            if p.get("account_type") == "Agency":
                st.write(f"**Agency name:** {p.get('agency_name','')}")
                st.write(f"**Website:** {p.get('agency_website','')}")
                st.write(f"**Payment:** {p.get('agency_payment_model','')}")
                if p.get("agency_fee_band"):
                    st.write(f"**Fee:** {p.get('agency_fee_band')}")
                if p.get("agency_commission_band"):
                    st.write(f"**Commission:** {p.get('agency_commission_band')}")
                if p.get("agency_services"):
                    st.write(f"**Services:** {', '.join(_csv_split(p.get('agency_services','')))}")
                if p.get("agency_content_specialties"):
                    st.write(f"**Specialties:** {', '.join(_csv_split(p.get('agency_content_specialties','')))}")
                if p.get("agency_success_story"):
                    st.write("")
                    st.markdown("**Success story**")
                    st.write(p.get("agency_success_story"))

            st.write("")
            if p.get("bio"):
                st.markdown("**Bio**")
                st.write(p.get("bio"))

            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                # Edit = restart onboarding for that role
                if st.button("Edit profile", use_container_width=True):
                    st.session_state.auth_step = "creator_0" if role == "Creator" else "agency_0"
                    st.rerun()
            with c2:
                if st.button("Sign out", use_container_width=True):
                    # reset session
                    st.session_state.auth_step = "role"
                    st.session_state.role = ""
                    st.session_state.display_name = ""
                    st.session_state.profile_id = None
                    st.session_state.screen = "home"
                    st.session_state.compose_to_id = None

                    # clear drafts
                    st.session_state.c_photos = []
                    st.session_state.c_personality = ""
                    st.session_state.c_current = ""
                    st.session_state.c_hometown = ""
                    st.session_state.c_niche = ""
                    st.session_state.c_content_types = []
                    st.session_state.c_platform_mode = "Manual"
                    st.session_state.c_platform_handle = ""
                    st.session_state.c_platform_url = ""
                    st.session_state.c_earnings_band = "Prefer not to say"
                    st.session_state.c_bio = ""
                    st.session_state.c_selfie = None

                    st.session_state.a_agency_name = ""
                    st.session_state.a_website = ""
                    st.session_state.a_success = ""
                    st.session_state.a_services = []
                    st.session_state.a_specialties = []
                    st.session_state.a_payment_model = "Commission-based"
                    st.session_state.a_fee_band = "Prefer not to say"
                    st.session_state.a_commission_band = "15–20%"
                    st.session_state.a_payment_other = ""
                    st.session_state.a_location = ""
                    st.session_state.a_niche = ""
                    st.session_state.a_bio = ""

                    st.rerun()

    card_close()

shell_close()
