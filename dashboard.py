import streamlit as st
import json, os, base64, requests
from datetime import datetime, timedelta

st.set_page_config(page_title="MCO Sales Dashboard", page_icon="🏠", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0d0d0d}
[data-testid="stSidebar"]{background:#111111}
.block-container{padding-top:1.5rem}
.lb-row{background:#1a1a1a;border-radius:10px;padding:14px 20px;margin-bottom:8px;border-left:3px solid #cc0000}
.metric-card{background:#1a1a1a;border-radius:12px;padding:18px 20px;margin-bottom:10px;min-height:110px;border-top:2px solid #cc0000}
.card-label{color:#888888;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.card-value{font-size:26px;font-weight:bold;margin:2px 0}
.card-goal{color:#888888;font-size:12px;margin-top:4px}
.badge-g{background:#22c55e;color:#ffffff;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:bold}
.badge-y{background:#f59e0b;color:#ffffff;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:bold}
.badge-r{background:#cc0000;color:#ffffff;padding:2px 9px;border-radius:20px;font-size:11px;font-weight:bold}
.alert-box{background:#1a0000;border:1px solid #cc0000;border-radius:10px;padding:16px 20px;margin-bottom:16px}
.commit-box{background:#001a00;border:1px solid #22c55e;border-radius:10px;padding:16px 20px;margin-bottom:16px}
.commit-card{background:#1a1a1a;border-radius:12px;padding:18px 20px;margin-bottom:12px;border-left:3px solid #cc0000}
.section-hdr{color:#888888;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;margin:18px 0 8px;font-weight:bold}
.mco-header{background:linear-gradient(90deg,#cc0000,#8b0000);padding:16px 24px;border-radius:10px;margin-bottom:20px}
#MainMenu,footer,header{visibility:hidden}
label{color:#ffffff !important}
[data-testid="stWidgetLabel"]{color:#ffffff !important}
p{color:#ffffff}
.stMarkdown p{color:#ffffff !important}
h1,h2,h3{color:#ffffff !important}
[data-testid="stSidebar"] *{color:#ffffff}
/* Fix dropdowns and inputs - dark background with white text */
[data-baseweb="select"] > div{background-color:#1a1a1a !important;color:#ffffff !important;border:1px solid #cc0000 !important}
[data-baseweb="select"] div{background-color:#1a1a1a !important;color:#ffffff !important}
[data-baseweb="select"] span{color:#ffffff !important}
[data-baseweb="popover"] li{background:#1a1a1a !important;color:#ffffff !important}
[data-baseweb="popover"] li:hover{background:#cc0000 !important}
.stTextInput input{background:#1a1a1a !important;color:#ffffff !important;border:1px solid #cc0000 !important}
.stNumberInput input{background:#1a1a1a !important;color:#ffffff !important;border:1px solid #333 !important}
</style>""", unsafe_allow_html=True)

# ── Data storage: GitHub API (cloud) or local file ────────────────────────────
USE_GITHUB = "github_token" in st.secrets if hasattr(st, "secrets") else False

DESKTOP     = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
PROJECT_DIR = os.path.join(DESKTOP, "Projects", "Rep Performance Tracker")
LOCAL_FILE  = os.path.join(PROJECT_DIR, "data.json")

def load_data():
    if USE_GITHUB:
        try:
            token = st.secrets["github_token"]
            repo  = st.secrets["github_repo"]
            url   = f"https://api.github.com/repos/{repo}/contents/data.json"
            r = requests.get(url, headers={"Authorization": f"token {token}"})
            if r.status_code == 200:
                info = r.json()
                d = json.loads(base64.b64decode(info["content"]).decode())
                d["_sha"] = info["sha"]
                if "commitments" not in d: d["commitments"] = {}
                return d
        except Exception as e:
            st.warning(f"Could not load from GitHub: {e}")
    try:
        with open(LOCAL_FILE) as f:
            d = json.load(f)
            if "commitments" not in d: d["commitments"] = {}
            return d
    except:
        return {"reps":[],"entries":{},"commitments":{}}

def save_data(d):
    if USE_GITHUB:
        try:
            token = st.secrets["github_token"]
            repo  = st.secrets["github_repo"]
            sha   = d.pop("_sha", None)
            content = base64.b64encode(json.dumps(d, indent=2).encode()).decode()
            url = f"https://api.github.com/repos/{repo}/contents/data.json"
            payload = {"message":"Update data","content":content}
            if sha: payload["sha"] = sha
            r = requests.put(url, json=payload,
                             headers={"Authorization": f"token {token}"})
            d["_sha"] = r.json().get("content",{}).get("sha", sha)
            return
        except Exception as e:
            st.warning(f"Could not save to GitHub: {e}")
    try:
        with open(LOCAL_FILE,"w") as f:
            json.dump(d, f, indent=2)
    except: pass

def today_key():     return datetime.now().strftime("%Y-%m-%d")
def yesterday_key(): return (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")
def week_key(dt=None):
    dt=dt or datetime.now()
    return (dt-timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
def month_key(dt=None): return (dt or datetime.now()).strftime("%Y-%m")
def month_label(k):     return datetime.strptime(k+"-01","%Y-%m-%d").strftime("%B %Y")
def fmt_date(k):        return datetime.strptime(k,"%Y-%m-%d").strftime("%A, %b %d")

def get_monthly(rep,month,data):
    entries={w:e for w,e in data["entries"].get(rep,{}).items() if w.startswith(month)}
    if not entries: return None
    keys=["calls","talk_time","appointments","offers","contracts","closed_deals","revenue","spread"]
    t={k:sum(e.get(k,0) for e in entries.values()) for k in keys}
    t["weeks"]=len(entries)
    ap=t["appointments"]; con=t["contracts"]; cl=t["closed_deals"]
    t["offer_pct"]    =t["offers"]/ap*100   if ap>0  else 0.0
    t["appt_con_pct"] =con/ap*100           if ap>0  else 0.0
    t["con_close_pct"]=cl/con*100           if con>0 else 0.0
    t["avg_spread"]   =t["spread"]/cl       if cl>0  else 0.0
    weights={"calls":15,"talk_time":15,"contracts":25,"closed_deals":20,"revenue":25}
    quotas ={"calls":600,"talk_time":2400,"contracts":12,"closed_deals":6,"revenue":100000}
    t["score"]=round(sum(min(t[k]/quotas[k],1.0)*w for k,w in weights.items()),1)
    return t

def get_streak(rep,data):
    commits=data.get("commitments",{}).get(rep,{})
    streak=0; check=datetime.now().date()-timedelta(days=1)
    for _ in range(90):
        if check.weekday()>=5: check-=timedelta(days=1); continue
        c=commits.get(check.strftime("%Y-%m-%d"))
        if c and c.get("hit")==True: streak+=1; check-=timedelta(days=1)
        else: break
    return streak

def badge(val,target):
    if not target: return ""
    r=val/target
    if r>=1.0:    return '<span class="badge-g">On Track</span>'
    elif r>=0.75: return '<span class="badge-y">Close</span>'
    else:         return '<span class="badge-r">Behind</span>'

def vcolor(val,target):
    if not target: return "#cdd6f4"
    r=val/target
    if r>=1.0:    return "#a6e3a1"
    elif r>=0.75: return "#f9e2af"
    else:         return "#f38ba8"

data=load_data()
if "daily_logs" not in data: data["daily_logs"]={}

DAILY_GOALS={"calls":30,"talk_time":120}

def get_daily_score(log):
    calls=log.get("calls",0); talk=log.get("talk_time",0)
    appts=log.get("appointments",0); offers=log.get("offers",0)
    offer_rate=(offers/appts*100) if appts>0 else 0
    s = min(calls/30,1)*40 + min(talk/120,1)*40 + min(offer_rate/100,1)*20
    return round(s,1)

with st.sidebar:
    st.markdown("### 🏠 MCO Sales Dashboard")
    st.markdown("---")
    page=st.radio("Navigate",["Team Overview","Daily Numbers","Daily Commitments","Individual Rep","Log Performance"],label_visibility="collapsed")
    st.markdown("---")
    all_months=set([month_key()])
    for rd in data["entries"].values():
        for w in rd: all_months.add(w[:7])
    months=sorted(all_months,reverse=True)
    sel_month=st.selectbox("Month",months,format_func=month_label)
    st.markdown("---")
    st.caption(f"Updated {datetime.now().strftime('%b %d  %I:%M %p')}")

# ─── TEAM OVERVIEW ────────────────────────────────────────────────────────────
if page=="Team Overview":
    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px">🏠 MIDWEST CASH OFFER</div>
    <div style="color:#ffcccc;font-size:14px;margin-top:2px">Sales Performance Dashboard — {month_label(sel_month)}</div>
    </div>""", unsafe_allow_html=True)
    if not data["reps"]:
        st.info("No reps yet. Go to **Log Performance** to get started."); st.stop()
    today=today_key(); yesterday=yesterday_key()
    no_commit=[r for r in data["reps"] if today not in data["commitments"].get(r,{})]
    missed_y =[r for r in data["reps"] if data["commitments"].get(r,{}).get(yesterday,{}).get("hit")==False]
    hit_y    =[r for r in data["reps"] if data["commitments"].get(r,{}).get(yesterday,{}).get("hit")==True]
    if no_commit:
        st.markdown(f"""<div class="alert-box">
        <div style="color:#f38ba8;font-weight:bold;font-size:13px">COMMITMENT ALERT — {fmt_date(today)}</div>
        <div style="color:#cdd6f4;font-size:16px;margin:4px 0"><b>{len(no_commit)} rep{"s" if len(no_commit)!=1 else ""} have not submitted a commitment today</b></div>
        <div style="color:#f38ba8;font-size:13px;margin-top:4px">{"  |  ".join(no_commit)}</div>
        </div>""",unsafe_allow_html=True)
    if hit_y:
        st.markdown(f"""<div class="commit-box">
        <div style="color:#a6e3a1;font-weight:bold;font-size:13px">COMMITMENTS HIT — {fmt_date(yesterday)}</div>
        <div style="color:#cdd6f4;font-size:15px;margin-top:4px">{"  |  ".join(hit_y)}</div>
        </div>""",unsafe_allow_html=True)
    if missed_y:
        st.markdown(f"""<div class="alert-box">
        <div style="color:#f38ba8;font-weight:bold;font-size:13px">COMMITMENTS MISSED — {fmt_date(yesterday)}</div>
        <div style="color:#cdd6f4;font-size:15px;margin-top:4px">{"  |  ".join(missed_y)}</div>
        </div>""",unsafe_allow_html=True)
    board=[(r,get_monthly(r,sel_month,data)) for r in data["reps"]]
    board=[(r,t) for r,t in board if t]; board.sort(key=lambda x:x[1]["score"],reverse=True)
    if board:
        n=len(board)
        c1,c2,c3,c4=st.columns(4)
        c1.metric("Total Revenue", f"${sum(t['revenue'] for _,t in board):,.0f}", f"Goal: ${100000*n:,.0f}")
        c2.metric("Closed Deals",  int(sum(t['closed_deals'] for _,t in board)),  f"Goal: {6*n}")
        c3.metric("Contracts",     int(sum(t['contracts'] for _,t in board)),      f"Goal: {12*n}")
        c4.metric("Avg Score",     f"{round(sum(t['score'] for _,t in board)/n,1)}/100")
    st.markdown('<div class="section-hdr">Leaderboard</div>',unsafe_allow_html=True)
    for rank,(rep,t) in enumerate(board,1):
        sc=t["score"]
        sc_col="#a6e3a1" if sc>=80 else "#f9e2af" if sc>=60 else "#f38ba8"
        grade ="A" if sc>=90 else "B" if sc>=80 else "C" if sc>=70 else "D" if sc>=60 else "F"
        gbg   ="#a6e3a1" if grade in ["A","B"] else "#f9e2af" if grade=="C" else "#f38ba8"
        icon  =":trophy:" if rank==1 else ":2nd_place_medal:" if rank==2 else ":3rd_place_medal:" if rank==3 else f"#{rank}"
        streak=get_streak(rep,data)
        tc=data["commitments"].get(rep,{}).get(today)
        cs,cc=("Committed","#a6e3a1") if tc else ("No commitment yet","#f9e2af")
        streak_tag = f'&nbsp;<span style="font-size:12px;color:#f9e2af">🔥 {streak}d</span>' if streak>0 else ""
        st.markdown(f"""<div class="lb-row" style="display:flex;align-items:center;justify-content:space-between">
        <div style="display:flex;align-items:center;gap:16px">
          <div style="font-size:22px;width:34px">{icon}</div>
          <div>
            <div style="color:#cdd6f4;font-size:16px;font-weight:bold">{rep}{streak_tag}</div>
            <div style="color:#6c7086;font-size:12px">{t["weeks"]} wk logged &nbsp;·&nbsp; {int(t["closed_deals"])} closed &nbsp;·&nbsp; ${t["revenue"]:,.0f} &nbsp;·&nbsp; <span style="color:{cc}">{cs}</span></div>
          </div>
        </div>
        <div style="display:flex;align-items:center;gap:16px">
          <div style="text-align:right"><div style="color:{sc_col};font-size:28px;font-weight:bold;line-height:1">{sc}</div><div style="color:#6c7086;font-size:11px">/ 100</div></div>
          <div style="background:{gbg};color:#1e1e2e;width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:17px">{grade}</div>
        </div></div>""",unsafe_allow_html=True)
    if not board: st.info(f"No data logged for {month_label(sel_month)} yet.")

# ─── DAILY NUMBERS ───────────────────────────────────────────────────────────
elif page=="Daily Numbers":
    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px">🏠 MIDWEST CASH OFFER</div>
    <div style="color:#ffcccc;font-size:14px;margin-top:2px">Daily Numbers — {fmt_date(today_key())}</div>
    </div>""", unsafe_allow_html=True)

    if not data["reps"]:
        st.info("No reps yet. Go to **Log Performance** to add reps first."); st.stop()

    tab1, tab2 = st.tabs(["Leaderboard", "Log Today's Numbers"])

    # ── Leaderboard ──
    with tab1:
        today = today_key()
        board = []
        for rep in data["reps"]:
            log = data["daily_logs"].get(rep,{}).get(today)
            if log:
                score = get_daily_score(log)
                board.append((rep, log, score))
            else:
                board.append((rep, None, -1))

        # Sort: logged entries by score first, then unlogged
        logged   = sorted([(r,l,s) for r,l,s in board if l], key=lambda x:x[2], reverse=True)
        unlogged = [(r,l,s) for r,l,s in board if not l]
        board    = logged + unlogged

        # Summary row at top
        if logged:
            st.markdown('<div class="section-hdr">Today\'s Team Summary</div>', unsafe_allow_html=True)
            c1,c2,c3,c4,c5 = st.columns(5)
            total_calls     = sum(l.get("calls",0) for _,l,_ in logged)
            total_talk      = sum(l.get("talk_time",0) for _,l,_ in logged)
            total_appts     = sum(l.get("appointments",0) for _,l,_ in logged)
            total_offers    = sum(l.get("offers",0) for _,l,_ in logged)
            total_contracts = sum(l.get("contracts",0) for _,l,_ in logged)
            n = len(logged)
            c1.metric("Total Calls",      int(total_calls),      f"Goal: {30*n}")
            c2.metric("Total Talk Time",  f"{int(total_talk)} min", f"Goal: {120*n} min")
            c3.metric("Appointments",     int(total_appts))
            c4.metric("Offers",           int(total_offers))
            c5.metric("Contracts",        int(total_contracts),  f"Goal: {3*n}/week")

        st.markdown('<div class="section-hdr">Daily Leaderboard</div>', unsafe_allow_html=True)

        # Header row
        st.markdown("""<div style="display:grid;grid-template-columns:40px 160px 110px 120px 100px 100px 100px 80px;
        gap:8px;padding:8px 16px;color:#888888;font-size:11px;text-transform:uppercase;letter-spacing:1px">
        <div>#</div><div>Rep</div><div>Calls</div>
        <div>Talk Time</div><div>Appts</div><div>Offers</div><div>Contracts</div><div>Score</div>
        </div>""", unsafe_allow_html=True)

        for rank,(rep,log,score) in enumerate(board,1):
            if not log:
                st.markdown(f"""<div style="display:grid;grid-template-columns:40px 160px 110px 120px 100px 100px 100px 80px;
                gap:8px;padding:12px 16px;background:#1a1a1a;border-radius:8px;margin-bottom:6px;
                border-left:3px solid #333;align-items:center">
                <div style="color:#888">#{rank}</div>
                <div style="color:#ffffff;font-weight:bold">{rep}</div>
                <div style="color:#555;font-style:italic">Not logged</div>
                <div></div><div></div><div></div><div></div><div></div>
                </div>""", unsafe_allow_html=True)
                continue

            calls     = log.get("calls",0);      tc = vcolor(calls,30)
            talk      = log.get("talk_time",0);  tt = vcolor(talk,120)
            appts     = log.get("appointments",0)
            offers    = log.get("offers",0)
            contracts = log.get("contracts",0)
            off_rate  = (offers/appts*100) if appts>0 else 0; to = vcolor(off_rate,100)
            medal     = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"#{rank}"
            sc_col    = "#22c55e" if score>=80 else "#f59e0b" if score>=60 else "#cc0000"
            con_col   = "#22c55e" if contracts>=1 else "#ffffff"

            st.markdown(f"""<div style="display:grid;grid-template-columns:40px 160px 110px 120px 100px 100px 100px 80px;
            gap:8px;padding:14px 16px;background:#1a1a1a;border-radius:8px;margin-bottom:6px;
            border-left:3px solid #cc0000;align-items:center">
            <div style="font-size:18px">{medal}</div>
            <div style="color:#ffffff;font-weight:bold;font-size:15px">{rep}</div>
            <div style="color:{tc};font-weight:bold">{int(calls)}/30</div>
            <div style="color:{tt};font-weight:bold">{int(talk)}/120m</div>
            <div style="color:#ffffff">{int(appts)}</div>
            <div style="color:{to};font-weight:bold">{int(offers)}</div>
            <div style="color:{con_col};font-weight:bold">{int(contracts)}</div>
            <div style="color:{sc_col};font-weight:bold">{score}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""<div style="color:#555;font-size:11px;margin-top:12px">
        Goals: Calls 30/day &nbsp;·&nbsp; Talk Time 120 min/day &nbsp;·&nbsp; Offer on every appointment
        </div>""", unsafe_allow_html=True)

        if not logged:
            st.info("No reps have logged numbers today yet. Ask them to log their numbers!")

    # ── Log Today's Numbers ──
    with tab2:
        st.markdown(f"### Log Numbers for {fmt_date(today_key())}")
        rep  = st.selectbox("Select Rep", data["reps"], key="daily_rep")
        existing = data["daily_logs"].get(rep,{}).get(today_key())

        if existing:
            st.success(f"Numbers already logged at {existing.get('logged_at','')}")
            ec1,ec2,ec3,ec4 = st.columns(4)
            ec1.metric("Calls",     int(existing.get("calls",0)),     delta=f"{int(existing.get('calls',0))-30} vs goal")
            ec2.metric("Talk Time", f"{int(existing.get('talk_time',0))} min", delta=f"{int(existing.get('talk_time',0))-120} vs goal")
            ec3.metric("Appointments", int(existing.get("appointments",0)))
            ec4.metric("Offers",    int(existing.get("offers",0)))
            if st.button("Update Numbers"):
                del data["daily_logs"][rep][today_key()]
                save_data(data); st.rerun()
        else:
            dc1,dc2,dc3 = st.columns(3)
            with dc1:
                d_calls = st.number_input("Calls Made",        min_value=0, value=0)
                d_talk  = st.number_input("Talk Time (min)",   min_value=0, value=0)
            with dc2:
                d_appts = st.number_input("Appointments Set",  min_value=0, value=0)
                d_offers= st.number_input("Offers Made",       min_value=0, value=0)
            with dc3:
                d_contracts = st.number_input("Contracts",     min_value=0, value=0)

            if st.button("Save Today's Numbers", type="primary"):
                data["daily_logs"].setdefault(rep,{})[today_key()] = {
                    "calls":d_calls,"talk_time":d_talk,
                    "appointments":d_appts,"offers":d_offers,
                    "contracts":d_contracts,
                    "logged_at":datetime.now().strftime("%I:%M %p")
                }
                save_data(data)
                st.success(f"Numbers saved for {rep}!")
                st.rerun()

# ─── DAILY COMMITMENTS ────────────────────────────────────────────────────────
elif page=="Daily Commitments":
    st.markdown("## Daily Commitments")
    if not data["reps"]:
        st.info("No reps yet. Go to **Log Performance** first."); st.stop()
    tab1,tab2,tab3=st.tabs(["Submit Today","Review Yesterday","History"])

    with tab1:
        st.markdown(f"### Commitment for {fmt_date(today_key())}")
        rep=st.selectbox("Select Rep",data["reps"],key="commit_rep")
        existing=data["commitments"].get(rep,{}).get(today_key())
        if existing:
            st.success(f"Commitment submitted at {existing.get('submitted_at','')}")
            st.markdown(f"""<div class="commit-card">
            <div style="color:#6c7086;font-size:11px;text-transform:uppercase">Today's Commitment</div>
            <div style="color:#cdd6f4;font-size:16px;margin:10px 0;font-style:italic">"{existing.get('text','')}"</div>
            <div style="color:#6c7086;font-size:12px">Calls: {existing.get('goal_calls',0)} &nbsp;|&nbsp; Talk Time: {existing.get('goal_talk_time',0)} min &nbsp;|&nbsp; Appts: {existing.get('goal_appts',0)} &nbsp;|&nbsp; Offers: {existing.get('goal_offers',0)}</div>
            </div>""",unsafe_allow_html=True)
            if st.button("Clear and Re-submit"):
                del data["commitments"][rep][today_key()]; save_data(data); st.rerun()
        else:
            commit_text=st.text_area("What is your commitment for today?",placeholder="I will make 30 calls, spend 2 hours on the phone, and set 2 appointments today.",height=100)
            st.markdown("**Daily targets** *(optional)*")
            gc1,gc2,gc3,gc4=st.columns(4)
            with gc1: g_calls=st.number_input("Calls goal",min_value=0,value=30)
            with gc2: g_talk =st.number_input("Talk time (min)",min_value=0,value=120)
            with gc3: g_appts=st.number_input("Appts goal",min_value=0,value=0)
            with gc4: g_off  =st.number_input("Offers goal",min_value=0,value=0)
            if st.button("Submit Commitment",type="primary"):
                if not commit_text.strip():
                    st.warning("Please write your commitment first.")
                else:
                    data["commitments"].setdefault(rep,{})[today_key()]={
                        "text":commit_text.strip(),"goal_calls":g_calls,
                        "goal_talk_time":g_talk,"goal_appts":g_appts,"goal_offers":g_off,
                        "submitted_at":datetime.now().strftime("%I:%M %p"),
                        "hit":None,"notes":"","reviewed_at":None
                    }
                    save_data(data); st.success(f"Commitment submitted for {rep}!"); st.balloons(); st.rerun()

    with tab2:
        ykey=yesterday_key()
        st.markdown(f"### Review — {fmt_date(ykey)}")
        any_c=False
        for rep in data["reps"]:
            c=data["commitments"].get(rep,{}).get(ykey)
            if not c: continue
            any_c=True
            hit_val=c.get("hit")
            if hit_val==True:   sh,cb='<span class="badge-g">HIT ✅</span>',"border-left:4px solid #a6e3a1"
            elif hit_val==False: sh,cb='<span class="badge-r">MISSED ❌</span>',"border-left:4px solid #f38ba8"
            else:                sh,cb='<span class="badge-y">Pending Review</span>',"border-left:4px solid #f9e2af"
            st.markdown(f"""<div class="commit-card" style="{cb}">
            <div style="color:#cdd6f4;font-size:15px;font-weight:bold">{rep} &nbsp; {sh}</div>
            <div style="color:#6c7086;font-size:12px;margin-top:2px">Submitted at {c.get("submitted_at","")}</div>
            <div style="color:#cdd6f4;font-size:15px;margin:10px 0;font-style:italic">"{c.get("text","")}"</div>
            <div style="color:#6c7086;font-size:12px">Goals — Calls: {c.get("goal_calls",0)} | Talk: {c.get("goal_talk_time",0)}min | Appts: {c.get("goal_appts",0)} | Offers: {c.get("goal_offers",0)}</div>
            </div>""",unsafe_allow_html=True)
            if hit_val is None:
                ca,cb2,_=st.columns([1,1,4])
                with ca:
                    if st.button("Hit ✅",key=f"hit_{rep}_{ykey}",type="primary"):
                        data["commitments"][rep][ykey]["hit"]=True
                        data["commitments"][rep][ykey]["reviewed_at"]=datetime.now().strftime("%Y-%m-%d %H:%M")
                        save_data(data); st.rerun()
                with cb2:
                    if st.button("Missed ❌",key=f"miss_{rep}_{ykey}"):
                        data["commitments"][rep][ykey]["hit"]=False
                        data["commitments"][rep][ykey]["reviewed_at"]=datetime.now().strftime("%Y-%m-%d %H:%M")
                        save_data(data); st.rerun()
            else:
                if st.button("Undo",key=f"undo_{rep}_{ykey}"):
                    data["commitments"][rep][ykey]["hit"]=None; save_data(data); st.rerun()
            st.markdown("")
        if not any_c: st.info(f"No commitments were submitted for {fmt_date(ykey)}.")

    with tab3:
        st.markdown("### Commitment History")
        all_rows=[]
        for rep in data["reps"]:
            rc=data["commitments"].get(rep,{})
            streak=get_streak(rep,data)
            total=len(rc); hits=sum(1 for c in rc.values() if c.get("hit")==True)
            pct=round(hits/total*100) if total>0 else 0
            for dk in sorted(rc.keys(),reverse=True):
                c=rc[dk]; hv=c.get("hit")
                all_rows.append({"Rep":rep,"Date":fmt_date(dk),
                    "Commitment":c.get("text","")[:60]+("..." if len(c.get("text",""))>60 else ""),
                    "Result":"Hit ✅" if hv==True else "Missed ❌" if hv==False else "Pending",
                    "Submitted":c.get("submitted_at","")})
        if all_rows:
            st.markdown('<div class="section-hdr">Streak Summary</div>',unsafe_allow_html=True)
            cols=st.columns(max(len(data["reps"]),1))
            for i,rep in enumerate(data["reps"]):
                streak=get_streak(rep,data); rc=data["commitments"].get(rep,{})
                total=len(rc); hits=sum(1 for c in rc.values() if c.get("hit")==True)
                pct=round(hits/total*100) if total>0 else 0
                with cols[i]:
                    st.markdown(f"""<div class="metric-card" style="text-align:center">
                    <div class="card-label">{rep}</div>
                    <div class="card-value" style="color:#f9e2af">{"🔥 " if streak>0 else ""}{streak}d</div>
                    <div class="card-goal">streak &nbsp;·&nbsp; {pct}% hit rate</div>
                    </div>""",unsafe_allow_html=True)
            st.markdown('<div class="section-hdr">All Commitments</div>',unsafe_allow_html=True)
            import pandas as pd
            st.dataframe(pd.DataFrame(all_rows),use_container_width=True,hide_index=True)
        else:
            st.info("No commitment history yet.")

# ─── INDIVIDUAL REP ───────────────────────────────────────────────────────────
elif page=="Individual Rep":
    if not data["reps"]: st.info("No reps yet."); st.stop()
    rep=st.selectbox("Select Rep",data["reps"]); t=get_monthly(rep,sel_month,data)
    st.markdown(f"## {rep} — {month_label(sel_month)}")
    if not t: st.info(f"No data logged for {rep} in {month_label(sel_month)}."); st.stop()
    sc=t["score"]; streak=get_streak(rep,data)
    grade="A" if sc>=90 else "B" if sc>=80 else "C" if sc>=70 else "D" if sc>=60 else "F"
    sc_col="#a6e3a1" if sc>=80 else "#f9e2af" if sc>=60 else "#f38ba8"
    gbg="#a6e3a1" if grade in ["A","B"] else "#f9e2af" if grade=="C" else "#f38ba8"
    st.markdown(f"""<div style="background:#313244;border-radius:12px;padding:20px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center">
    <div>
      <div style="color:#6c7086;font-size:11px;text-transform:uppercase;letter-spacing:1px">Performance Score</div>
      <div style="color:{sc_col};font-size:50px;font-weight:bold;line-height:1.1">{sc}<span style="color:#6c7086;font-size:20px">/100</span></div>
      <div style="color:#f9e2af;font-size:13px">{"🔥 "+str(streak)+"-day commitment streak" if streak>0 else "No active streak"}</div>
    </div>
    <div style="background:{gbg};color:#1e1e2e;width:68px;height:68px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:30px">{grade}</div>
    </div>""",unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">Metrics vs Goal</div>',unsafe_allow_html=True)
    metrics=[("Calls",t["calls"],600,"n"),("Talk Time (min)",t["talk_time"],2400,"n"),
             ("Appointments",t["appointments"],None,"n"),("Offers",t["offers"],t["appointments"],"n"),
             ("Offer Rate",t["offer_pct"],100,"%"),("Contracts",t["contracts"],12,"n"),
             ("Appt to Contract",t["appt_con_pct"],20,"%"),("Contract to Close",t["con_close_pct"],75,"%"),
             ("Closed Deals",t["closed_deals"],6,"n"),("Revenue",t["revenue"],100000,"$"),
             ("Avg Spread/Deal",t["avg_spread"],17500,"$")]
    for i in range(0,len(metrics),3):
        cols=st.columns(3)
        for j,col in enumerate(cols):
            if i+j<len(metrics):
                lbl,val,quota,fmt=metrics[i+j]
                with col:
                    if fmt=="$":   dsp=f"${val:,.0f}";  gs=f"Goal: ${quota:,.0f}" if quota else "--"
                    elif fmt=="%": dsp=f"{val:.1f}%";   gs=f"Goal: {quota}%" if quota else "--"
                    else:          dsp=f"{int(val):,}"; gs=f"Goal: {int(quota):,}" if quota else "--"
                    vc=vcolor(val,quota); bd=badge(val,quota)
                    st.markdown(f"""<div class="metric-card">
                    <div class="card-label">{lbl}</div><div class="card-value" style="color:{vc}">{dsp}</div>
                    <div class="card-goal">{gs} &nbsp; {bd}</div></div>""",unsafe_allow_html=True)

# ─── LOG PERFORMANCE ──────────────────────────────────────────────────────────
elif page=="Log Performance":
    st.markdown("## Log Weekly Performance")
    with st.expander("Add New Rep",expanded=not bool(data["reps"])):
        nr=st.text_input("Rep Name")
        if st.button("Add Rep",type="primary"):
            if nr and nr not in data["reps"]:
                data["reps"].append(nr); data["entries"].setdefault(nr,{})
                save_data(data); st.success(f"{nr} added!"); st.rerun()
            elif nr in data["reps"]: st.warning("Rep already exists.")
    st.markdown("---")
    if not data["reps"]: st.info("Add a rep first."); st.stop()
    rep=st.selectbox("Select Rep",data["reps"],key="log_rep")
    week=st.text_input("Week — Monday date (YYYY-MM-DD)",value=week_key())
    st.markdown("**Activity**")
    c1,c2,c3=st.columns(3)
    with c1: calls=st.number_input("Calls",min_value=0,value=0); talk_time=st.number_input("Talk Time (min)",min_value=0,value=0)
    with c2: appts=st.number_input("Appointments",min_value=0,value=0); offers=st.number_input("Offers",min_value=0,value=0)
    with c3: contracts=st.number_input("Contracts",min_value=0,value=0)
    st.markdown("**Results**")
    c4,c5,c6=st.columns(3)
    with c4: closed =st.number_input("Closed Deals",min_value=0,value=0)
    with c5: revenue=st.number_input("Revenue ($)",min_value=0,value=0)
    with c6: spread =st.number_input("Total Spread ($)",min_value=0,value=0)
    if st.button("Save Entry",type="primary"):
        try:
            datetime.strptime(week,"%Y-%m-%d")
            data["entries"].setdefault(rep,{})[week]={"calls":calls,"talk_time":talk_time,
                "appointments":appts,"offers":offers,"contracts":contracts,
                "closed_deals":closed,"revenue":revenue,"spread":spread}
            save_data(data); st.success(f"Saved for {rep} — week of {week}!")
        except ValueError: st.error("Invalid date. Use YYYY-MM-DD.")
