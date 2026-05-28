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
/* Competitive leaderboard cards */
.lb-rank1{background:#1c1800;border-radius:12px;padding:20px 24px;margin-bottom:12px;border:1px solid rgba(249,226,175,0.35);border-left:5px solid #f9e2af;box-shadow:0 0 30px rgba(249,226,175,0.07)}
.lb-rank2{background:#0f1520;border-radius:12px;padding:20px 24px;margin-bottom:12px;border-left:5px solid #60a5fa}
.lb-rank3{background:#1a1208;border-radius:12px;padding:20px 24px;margin-bottom:12px;border-left:5px solid #cd7f32}
.lb-hunt{background:#141414;border-radius:12px;padding:20px 24px;margin-bottom:12px;border-left:5px solid #333}
.lb-last{background:#1a0000;border-radius:12px;padding:20px 24px;margin-bottom:12px;border:1px solid rgba(204,0,0,0.4);border-left:5px solid #cc0000}
.lb-ghost{background:#0f0f0f;border-radius:10px;padding:14px 22px;margin-bottom:8px;border-left:5px solid #1e1e1e}
.tag-king{display:inline-block;background:rgba(249,226,175,0.12);color:#f9e2af;padding:4px 14px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.8px;border:1px solid rgba(249,226,175,0.25)}
.tag-chase{display:inline-block;background:rgba(96,165,250,0.1);color:#60a5fa;padding:4px 14px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.8px}
.tag-hunt{display:inline-block;background:rgba(166,227,161,0.08);color:#a6e3a1;padding:4px 14px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.8px}
.tag-last{display:inline-block;background:rgba(204,0,0,0.15);color:#f38ba8;padding:4px 14px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.8px;border:1px solid rgba(204,0,0,0.3)}
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

def get_monthly(rep, month, data):
    # Results (closed deals, revenue, spread) come from Log Weekly Results entries
    entries = {w:e for w,e in data["entries"].get(rep,{}).items() if w.startswith(month)}
    # Activity metrics come from daily logs
    try:
        m_start = datetime.strptime(month + "-01", "%Y-%m-%d").date()
        next_mo = (m_start.replace(day=28) + timedelta(days=4)).replace(day=1)
        m_end   = next_mo - timedelta(days=1)
        logs    = data.get("daily_logs", {}).get(rep, {})
        act     = {k:0 for k in ["calls","talk_time","appointments","offers","contracts"]}
        days_logged = 0
        cur = m_start
        while cur <= m_end:
            e = logs.get(cur.strftime("%Y-%m-%d"))
            if e:
                for k in act: act[k] += e.get(k, 0)
                days_logged += 1
            cur += timedelta(days=1)
    except:
        act = {k:0 for k in ["calls","talk_time","appointments","offers","contracts"]}
        days_logged = 0

    if not entries and days_logged == 0: return None

    t = {k: sum(e.get(k,0) for e in entries.values()) for k in ["closed_deals","revenue","spread"]}
    t["weeks"] = len(entries)
    t.update(act)

    ap=t["appointments"]; con=t["contracts"]; cl=t["closed_deals"]
    t["offer_pct"]    = t["offers"]/ap*100  if ap>0  else 0.0
    t["appt_con_pct"] = con/ap*100          if ap>0  else 0.0
    t["con_close_pct"]= cl/con*100          if con>0 else 0.0
    t["avg_spread"]   = t["spread"]/cl      if cl>0  else 0.0
    weights = {"calls":15,"talk_time":15,"contracts":25,"closed_deals":20,"revenue":25}
    quotas  = {"calls":600,"talk_time":2400,"contracts":12,"closed_deals":6,"revenue":100000}
    t["score"] = round(sum(min(t[k]/quotas[k],1.0)*w for k,w in weights.items()), 1)
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

def get_weekly_score(wt):
    """0-100 score for a week's daily-log totals.
    Weights: calls 30 | talk time 30 | contracts 25 | appt→contract% 15"""
    calls=wt.get("calls",0); talk=wt.get("talk_time",0)
    appts=wt.get("appointments",0); cons=wt.get("contracts",0)
    acp=(cons/appts*100) if appts>0 else 0
    s=(min(calls/150,1)*30 + min(talk/600,1)*30 +
       min(cons/3,1)*25   + min(acp/20,1)*15)
    return round(s*100, 1)

def get_daily_range_totals(rep, data, start_dt, end_dt):
    """Sum daily_logs for a rep across a date range. Returns totals + day-by-day list."""
    logs = data.get("daily_logs", {}).get(rep, {})
    keys = ["calls","talk_time","appointments","offers","contracts"]
    totals = {k:0 for k in keys}
    day_entries = []
    current = start_dt
    while current <= end_dt:
        dk = current.strftime("%Y-%m-%d")
        entry = logs.get(dk)
        if entry:
            for k in keys:
                totals[k] += entry.get(k, 0)
            day_entries.append((dk, entry))
        current += timedelta(days=1)
    totals["days_logged"] = len(day_entries)
    totals["day_entries"] = day_entries
    return totals

with st.sidebar:
    st.markdown("### 🏠 MCO Sales Dashboard")
    st.markdown("---")
    page=st.radio("Navigate",["Team Overview","Daily Numbers","Daily Commitments","Individual Rep","Log Weekly Results"],label_visibility="collapsed")
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
        st.info("No reps yet. Go to **Log Weekly Results** to get started."); st.stop()

    today_str = today_key(); yesterday_str = yesterday_key()
    today_dt  = datetime.now().date()
    week_start  = today_dt - timedelta(days=today_dt.weekday())
    month_start = today_dt.replace(day=1)

    # ── Commitment alerts ──────────────────────────────────────────────────────
    no_commit=[r for r in data["reps"] if today_str not in data["commitments"].get(r,{})]
    missed_y =[r for r in data["reps"] if data["commitments"].get(r,{}).get(yesterday_str,{}).get("hit")==False]
    hit_y    =[r for r in data["reps"] if data["commitments"].get(r,{}).get(yesterday_str,{}).get("hit")==True]
    if no_commit:
        st.markdown(f"""<div class="alert-box">
        <div style="color:#f38ba8;font-weight:bold;font-size:13px">COMMITMENT ALERT — {fmt_date(today_str)}</div>
        <div style="color:#cdd6f4;font-size:16px;margin:4px 0"><b>{len(no_commit)} rep{"s" if len(no_commit)!=1 else ""} haven't submitted a commitment today</b></div>
        <div style="color:#f38ba8;font-size:13px;margin-top:4px">{"  |  ".join(no_commit)}</div>
        </div>""", unsafe_allow_html=True)
    if hit_y:
        st.markdown(f"""<div class="commit-box">
        <div style="color:#a6e3a1;font-weight:bold;font-size:13px">COMMITMENTS HIT — {fmt_date(yesterday_str)}</div>
        <div style="color:#cdd6f4;font-size:15px;margin-top:4px">{"  |  ".join(hit_y)}</div>
        </div>""", unsafe_allow_html=True)
    if missed_y:
        st.markdown(f"""<div class="alert-box">
        <div style="color:#f38ba8;font-weight:bold;font-size:13px">COMMITMENTS MISSED — {fmt_date(yesterday_str)}</div>
        <div style="color:#cdd6f4;font-size:15px;margin-top:4px">{"  |  ".join(missed_y)}</div>
        </div>""", unsafe_allow_html=True)

    # ── Competitive card renderer ──────────────────────────────────────────────
    def comp_card(rank, total, rep, score, gap, stats_html, needs_html, streak):
        medal = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"#{rank}"
        if rank == 1:
            card, tag_cls = "lb-rank1", "tag-king"
            if streak >= 5: tag_txt = f"👑 KING OF THE FLOOR &nbsp; 🔥 {streak}-DAY STREAK"
            else:           tag_txt = "👑 KING OF THE FLOOR"
            sc_col = "#f9e2af"
        elif rank == 2:
            card, tag_cls = "lb-rank2", "tag-chase"
            tag_txt = f"😤 CHASING — {gap:.1f} PTS FROM THE TOP"
            sc_col = "#60a5fa"
        elif rank == total and total >= 3:
            card, tag_cls = "lb-last", "tag-last"
            tag_txt = "🚨 LAST PLACE — The team is watching"
            sc_col = "#f38ba8"
        else:
            card, tag_cls = "lb-hunt", "tag-hunt"
            tag_txt = f"⚡ IN THE HUNT — {gap:.1f} PTS BACK"
            sc_col = "#a6e3a1"
        stk = f'&nbsp;&nbsp;<span style="color:#f9e2af;font-size:12px">🔥 {streak}d</span>' if streak>0 and rank>1 else ""
        st.markdown(f"""<div class="{card}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px">
          <div style="flex:1;min-width:0">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
              <span style="font-size:26px;line-height:1">{medal}</span>
              <span style="color:#ffffff;font-size:19px;font-weight:bold">{rep}{stk}</span>
            </div>
            <span class="{tag_cls}">{tag_txt}</span>
            <div style="margin-top:12px;font-size:13px;line-height:1.8">{stats_html}</div>
            {f'<div style="margin-top:8px;color:#666;font-size:11px;font-style:italic">{needs_html}</div>' if needs_html else ""}
          </div>
          <div style="text-align:right;flex-shrink:0">
            <div style="color:{sc_col};font-size:44px;font-weight:bold;line-height:1">{score:.0f}</div>
            <div style="color:#444;font-size:11px">/ 100</div>
          </div>
        </div>
        </div>""", unsafe_allow_html=True)

    def ghost_card(rank, rep):
        st.markdown(f"""<div class="lb-ghost">
        <span style="color:#333">#{rank}</span>&nbsp;&nbsp;
        <span style="color:#333;font-style:italic">{rep} — hasn't logged yet</span>
        </div>""", unsafe_allow_html=True)

    def needs_msg(my_dict, leader_dict, pairs):
        """pairs = list of (key, label, plural_label)"""
        parts=[]
        for key, lbl, plbl in pairs:
            g = leader_dict.get(key,0) - my_dict.get(key,0)
            if g > 0: parts.append(f"+{g:.0f} {plbl if g!=1 else lbl}")
        return "Needs to take the lead: " + " · ".join(parts[:3]) if parts else ""

    # ── THREE COMPETITIVE TABS ─────────────────────────────────────────────────
    tab_day, tab_week, tab_month = st.tabs(["🔥  TODAY", "📅  THIS WEEK", "📊  THIS MONTH"])

    # ── TODAY ──────────────────────────────────────────────────────────────────
    with tab_day:
        rows=[]
        for rep in data["reps"]:
            log=data["daily_logs"].get(rep,{}).get(today_str)
            rows.append((rep, log, get_daily_score(log) if log else -1))
        logged  =sorted([(r,l,s) for r,l,s in rows if l],key=lambda x:x[2],reverse=True)
        unlogged=[(r,l,s) for r,l,s in rows if not l]
        board=logged+unlogged; total=len(board)

        if logged:
            st.markdown('<div class="section-hdr">Team Today</div>', unsafe_allow_html=True)
            n=len(logged)
            tc1,tc2,tc3,tc4,tc5=st.columns(5)
            tc1.metric("Total Calls",    int(sum(l.get("calls",0) for _,l,_ in logged)),        f"Goal: {30*n}")
            tc2.metric("Talk Time",      f"{int(sum(l.get('talk_time',0) for _,l,_ in logged))} min", f"Goal: {120*n} min")
            tc3.metric("Appointments",   int(sum(l.get("appointments",0) for _,l,_ in logged)))
            tc4.metric("Offers",         int(sum(l.get("offers",0) for _,l,_ in logged)))
            tc5.metric("Contracts",      int(sum(l.get("contracts",0) for _,l,_ in logged)),    f"Goal: {n}/day")

        st.markdown('<div class="section-hdr">Daily Leaderboard</div>', unsafe_allow_html=True)
        leader_log  = logged[0][1] if logged else None
        leader_score= logged[0][2] if logged else 0

        for rank,(rep,log,score) in enumerate(board,1):
            streak=get_streak(rep,data)
            if not log: ghost_card(rank,rep); continue
            calls=log.get("calls",0); talk=log.get("talk_time",0)
            appts=log.get("appointments",0); offs=log.get("offers",0); cons=log.get("contracts",0)
            acp=f"{offs/appts*100:.0f}%" if appts>0 else "--"
            tc=vcolor(calls,30); tt=vcolor(talk,120)
            stats=(f'<span style="color:{tc};font-weight:bold">{int(calls)} calls</span>'
                   f' &nbsp;·&nbsp; <span style="color:{tt};font-weight:bold">{int(talk)} min</span>'
                   f' &nbsp;·&nbsp; <span style="color:{"#22c55e" if cons>=1 else "#cdd6f4"};font-weight:bold">{int(cons)} contracts</span>'
                   f' &nbsp;·&nbsp; <span style="color:#888">{int(appts)} appts &nbsp;·&nbsp; {acp} offer rate</span>')
            nm=""
            if rank>1 and leader_log:
                nm=needs_msg(log,leader_log,[("calls","call","calls"),("talk_time","min phone","min phone"),("contracts","contract","contracts")])
            comp_card(rank,total,rep,score,leader_score-score,stats,nm,streak)
        if not logged: st.info("No reps have logged numbers today yet.")

    # ── THIS WEEK ──────────────────────────────────────────────────────────────
    with tab_week:
        wrows=[]
        for rep in data["reps"]:
            wt=get_daily_range_totals(rep,data,week_start,today_dt)
            wrows.append((rep,wt if wt["days_logged"]>0 else None,
                          get_weekly_score(wt) if wt["days_logged"]>0 else -1))
        w_logged  =sorted([(r,w,s) for r,w,s in wrows if w],key=lambda x:x[2],reverse=True)
        w_unlogged=[(r,w,s) for r,w,s in wrows if not w]
        w_board=w_logged+w_unlogged; w_total=len(w_board)

        if w_logged:
            st.markdown('<div class="section-hdr">Team This Week</div>', unsafe_allow_html=True)
            n=len(w_logged)
            wc1,wc2,wc3,wc4=st.columns(4)
            tot_appts=sum(w.get("appointments",0) for _,w,_ in w_logged)
            tot_cons =sum(w.get("contracts",0) for _,w,_ in w_logged)
            wc1.metric("Total Calls",    int(sum(w.get("calls",0) for _,w,_ in w_logged)),         f"Goal: {150*n}")
            wc2.metric("Talk Time",      f"{int(sum(w.get('talk_time',0) for _,w,_ in w_logged))} min", f"Goal: {600*n} min")
            wc3.metric("Contracts",      int(tot_cons),                                              f"Goal: {3*n}")
            wc4.metric("Appt→Contract",  f"{tot_cons/tot_appts*100:.0f}%" if tot_appts>0 else "--", "Goal: 20%")

        st.markdown('<div class="section-hdr">Weekly Leaderboard</div>', unsafe_allow_html=True)
        w_leader=w_logged[0][1] if w_logged else None
        w_ls    =w_logged[0][2] if w_logged else 0

        for rank,(rep,wt,score) in enumerate(w_board,1):
            streak=get_streak(rep,data)
            if not wt: ghost_card(rank,rep); continue
            calls=wt.get("calls",0); talk=wt.get("talk_time",0)
            appts=wt.get("appointments",0); cons=wt.get("contracts",0)
            acp=(cons/appts*100) if appts>0 else 0
            tc=vcolor(calls,150); tt=vcolor(talk,600); kc=vcolor(cons,3); ac=vcolor(acp,20)
            stats=(f'<span style="color:{tc};font-weight:bold">{int(calls)} calls</span>'
                   f' &nbsp;·&nbsp; <span style="color:{tt};font-weight:bold">{int(talk)} min</span>'
                   f' &nbsp;·&nbsp; <span style="color:{kc};font-weight:bold">{int(cons)} contracts</span>'
                   f' &nbsp;·&nbsp; <span style="color:{ac};font-weight:bold">{acp:.0f}% A→C</span>')
            nm=""
            if rank>1 and w_leader:
                nm=needs_msg(wt,w_leader,[("calls","call","calls"),("talk_time","min phone","min phone"),("contracts","contract","contracts")])
            comp_card(rank,w_total,rep,score,w_ls-score,stats,nm,streak)
        if not w_logged: st.info("No reps have logged numbers this week yet.")

    # ── THIS MONTH ─────────────────────────────────────────────────────────────
    with tab_month:
        m_board=[(r,get_monthly(r,sel_month,data)) for r in data["reps"]]
        m_logged  =sorted([(r,t) for r,t in m_board if t],key=lambda x:x[1]["score"],reverse=True)
        m_unlogged=[(r,t) for r,t in m_board if not t]
        m_full=m_logged+m_unlogged; m_total=len(m_full)

        if m_logged:
            n=len(m_logged)
            st.markdown('<div class="section-hdr">Team This Month</div>', unsafe_allow_html=True)
            mc1,mc2,mc3,mc4=st.columns(4)
            tot_appts_m=sum(t["appointments"] for _,t in m_logged)
            tot_cons_m =sum(t["contracts"] for _,t in m_logged)
            mc1.metric("Total Revenue",   f"${sum(t['revenue'] for _,t in m_logged):,.0f}",     f"Goal: ${100000*n:,.0f}")
            mc2.metric("Closed Deals",    int(sum(t['closed_deals'] for _,t in m_logged)),       f"Goal: {6*n}")
            mc3.metric("Contracts",       int(tot_cons_m),                                        f"Goal: {12*n}")
            mc4.metric("Appt→Contract",   f"{tot_cons_m/tot_appts_m*100:.0f}%" if tot_appts_m>0 else "--", "Goal: 20%")

        st.markdown('<div class="section-hdr">Monthly Leaderboard</div>', unsafe_allow_html=True)
        m_leader  =m_logged[0][1] if m_logged else None
        m_ls      =m_logged[0][1]["score"] if m_logged else 0

        for rank,(rep,t) in enumerate(m_full,1):
            streak=get_streak(rep,data)
            if not t: ghost_card(rank,rep); continue
            sc=t["score"]
            calls=t.get("calls",0); cons=t.get("contracts",0)
            rev=t.get("revenue",0); acp=t.get("appt_con_pct",0); cl=t.get("closed_deals",0)
            tc=vcolor(calls,600); kc=vcolor(cons,12); rc=vcolor(rev,100000); ac=vcolor(acp,20)
            stats=(f'<span style="color:{tc};font-weight:bold">{int(calls)} calls</span>'
                   f' &nbsp;·&nbsp; <span style="color:{kc};font-weight:bold">{int(cons)} contracts</span>'
                   f' &nbsp;·&nbsp; <span style="color:{rc};font-weight:bold">${rev:,.0f} revenue</span>'
                   f' &nbsp;·&nbsp; <span style="color:#888">{int(cl)} closed &nbsp;·&nbsp; <span style="color:{ac}">{acp:.0f}% A→C</span></span>')
            nm=""
            if rank>1 and m_leader:
                nm=needs_msg(t,m_leader,[("contracts","contract","contracts"),("closed_deals","closed deal","closed deals"),("revenue","revenue","revenue")])
            comp_card(rank,m_total,rep,sc,m_ls-sc,stats,nm,streak)
        if not m_logged: st.info(f"No data logged for {month_label(sel_month)} yet.")

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
        st.markdown(f"""<div style="background:#001a00;border:1px solid #22c55e;border-radius:10px;
        padding:14px 20px;margin-bottom:18px">
        <div style="color:#a6e3a1;font-weight:bold;font-size:14px">📋 REPS — Log Your Numbers Here</div>
        <div style="color:#cdd6f4;font-size:13px;margin-top:4px">
        At the end of every day, select your name and enter your activity numbers below.
        This is the only form you need to fill out daily.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"### {fmt_date(today_key())}")
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
    rep = st.selectbox("Select Rep", data["reps"])

    today_dt    = datetime.now().date()
    week_start  = today_dt - timedelta(days=today_dt.weekday())   # Monday
    month_start = today_dt.replace(day=1)

    t      = get_monthly(rep, sel_month, data)
    streak = get_streak(rep, data)

    # ── Header ──
    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:20px;font-weight:bold;letter-spacing:1px">{rep}</div>
    <div style="color:#ffcccc;font-size:13px;margin-top:2px">{month_label(sel_month)}</div>
    </div>""", unsafe_allow_html=True)

    # ── Score card (only when monthly Log Performance data exists) ──
    if t:
        sc    = t["score"]
        grade = "A" if sc>=90 else "B" if sc>=80 else "C" if sc>=70 else "D" if sc>=60 else "F"
        sc_col= "#a6e3a1" if sc>=80 else "#f9e2af" if sc>=60 else "#f38ba8"
        gbg   = "#a6e3a1" if grade in ["A","B"] else "#f9e2af" if grade=="C" else "#f38ba8"
        st.markdown(f"""<div style="background:#1a1a1a;border-radius:12px;padding:20px;margin-bottom:16px;
        display:flex;justify-content:space-between;align-items:center;border-top:2px solid #cc0000">
        <div>
          <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px">Performance Score</div>
          <div style="color:{sc_col};font-size:50px;font-weight:bold;line-height:1.1">{sc}<span style="color:#888;font-size:20px">/100</span></div>
          <div style="color:#f9e2af;font-size:13px">{"🔥 "+str(streak)+"-day commitment streak" if streak>0 else "No active streak"}</div>
        </div>
        <div style="background:{gbg};color:#1e1e2e;width:68px;height:68px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:30px">{grade}</div>
        </div>""", unsafe_allow_html=True)
    elif streak > 0:
        st.markdown(f'<div style="color:#f9e2af;font-size:14px;margin-bottom:12px">🔥 {streak}-day commitment streak</div>', unsafe_allow_html=True)

    # ── THIS WEEK ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">This Week — Daily Pacing</div>', unsafe_allow_html=True)
    wt = get_daily_range_totals(rep, data, week_start, today_dt)
    days_elapsed = min(today_dt.weekday() + 1, 5)   # 1 (Mon) → 5 (Fri+)

    if wt["days_logged"] == 0:
        st.info(f"No daily numbers logged this week yet. Have {rep} log numbers in the Daily Numbers page.")
    else:
        wc1,wc2,wc3,wc4,wc5 = st.columns(5)
        week_metrics = [
            (wc1, "Calls",        wt["calls"],        30,  "",     True),
            (wc2, "Talk Time",    wt["talk_time"],    120, " min", True),
            (wc3, "Appointments", wt["appointments"],   0, "",     False),
            (wc4, "Offers",       wt["offers"],          0, "",     False),
            (wc5, "Contracts",    wt["contracts"],       0, "",     False),
        ]
        for col, lbl, val, daily_goal, unit, has_goal in week_metrics:
            if has_goal:
                pace = daily_goal * days_elapsed
                vc   = vcolor(val, pace)
                bd   = badge(val, pace)
                gs   = f"Pace goal: {int(pace)}{unit} &nbsp; {bd}"
            elif lbl == "Contracts":
                vc = "#22c55e" if val >= 3 else "#f9e2af" if val >= 1 else "#ffffff"
                bd = ""
                gs = "Goal: 3/week"
            else:
                vc, bd, gs = "#ffffff", "", "--"
            col.markdown(f"""<div class="metric-card">
            <div class="card-label">{lbl}</div>
            <div class="card-value" style="color:{vc}">{int(val)}{unit}</div>
            <div class="card-goal">{gs}</div></div>""", unsafe_allow_html=True)

        # Day-by-day breakdown
        st.markdown('<div class="section-hdr">Day-by-Day This Week</div>', unsafe_allow_html=True)
        st.markdown("""<div style="display:grid;grid-template-columns:130px 90px 100px 90px 90px 100px;
        gap:6px;padding:6px 14px;color:#888888;font-size:10px;text-transform:uppercase;letter-spacing:1px">
        <div>Day</div><div>Calls</div><div>Talk Time</div><div>Appts</div><div>Offers</div><div>Contracts</div>
        </div>""", unsafe_allow_html=True)
        for dk, entry in sorted(wt["day_entries"]):
            day_lbl = datetime.strptime(dk, "%Y-%m-%d").strftime("%a %b %d")
            c_v = entry.get("calls",0);       tc = vcolor(c_v, 30)
            tt_v= entry.get("talk_time",0);   tv = vcolor(tt_v, 120)
            a_v = entry.get("appointments",0)
            o_v = entry.get("offers",0)
            k_v = entry.get("contracts",0);   kc = "#22c55e" if k_v >= 1 else "#ffffff"
            st.markdown(f"""<div style="display:grid;grid-template-columns:130px 90px 100px 90px 90px 100px;
            gap:6px;padding:11px 14px;background:#1a1a1a;border-radius:8px;margin-bottom:5px;
            border-left:2px solid #333;align-items:center">
            <div style="color:#cdd6f4;font-size:13px;font-weight:bold">{day_lbl}</div>
            <div style="color:{tc};font-weight:bold">{int(c_v)}/30</div>
            <div style="color:{tv};font-weight:bold">{int(tt_v)} min</div>
            <div style="color:#ffffff">{int(a_v)}</div>
            <div style="color:#ffffff">{int(o_v)}</div>
            <div style="color:{kc};font-weight:bold">{int(k_v)}</div>
            </div>""", unsafe_allow_html=True)

    # ── THIS MONTH ─────────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">This Month — {month_label(sel_month)} Activity</div>', unsafe_allow_html=True)

    if sel_month == month_key():
        mt = get_daily_range_totals(rep, data, month_start, today_dt)
        workdays_so_far = sum(
            1 for i in range((today_dt - month_start).days + 1)
            if (month_start + timedelta(days=i)).weekday() < 5
        )
    else:
        sel_dt  = datetime.strptime(sel_month + "-01", "%Y-%m-%d").date()
        next_mo = (sel_dt.replace(day=28) + timedelta(days=4)).replace(day=1)
        sel_end = next_mo - timedelta(days=1)
        mt = get_daily_range_totals(rep, data, sel_dt, sel_end)
        workdays_so_far = sum(
            1 for i in range((sel_end - sel_dt).days + 1)
            if (sel_dt + timedelta(days=i)).weekday() < 5
        )

    if mt["days_logged"] == 0:
        st.info(f"No daily numbers logged for {month_label(sel_month)} yet.")
    else:
        mc1,mc2,mc3,mc4,mc5 = st.columns(5)
        month_metrics = [
            (mc1, "Calls",        mt["calls"],        600,  ""),
            (mc2, "Talk Time",    mt["talk_time"],    2400, " min"),
            (mc3, "Appointments", mt["appointments"],    0, ""),
            (mc4, "Offers",       mt["offers"],           0, ""),
            (mc5, "Contracts",    mt["contracts"],       12, ""),
        ]
        for col, lbl, val, goal, unit in month_metrics:
            if goal:
                vc = vcolor(val, goal); bd = badge(val, goal)
                gs = f"Goal: {goal}{unit} &nbsp; {bd}"
            else:
                vc, bd, gs = "#ffffff", "", "--"
            col.markdown(f"""<div class="metric-card">
            <div class="card-label">{lbl}</div>
            <div class="card-value" style="color:{vc}">{int(val)}{unit}</div>
            <div class="card-goal">{gs}</div></div>""", unsafe_allow_html=True)

    # ── MONTHLY RESULTS (from Log Performance — closed deals, revenue, spread) ──
    if t:
        st.markdown(f'<div class="section-hdr">Monthly Results — {month_label(sel_month)}</div>', unsafe_allow_html=True)
        results = [
            ("Closed Deals",     t["closed_deals"],  6,      "n"),
            ("Revenue",          t["revenue"],        100000, "$"),
            ("Avg Spread/Deal",  t["avg_spread"],     17500,  "$"),
            ("Offer Rate",       t["offer_pct"],      100,    "%"),
            ("Appt to Contract", t["appt_con_pct"],   20,     "%"),
            ("Contract to Close",t["con_close_pct"],  75,     "%"),
        ]
        for i in range(0, len(results), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i+j < len(results):
                    lbl,val,quota,fmt = results[i+j]
                    with col:
                        if fmt=="$":   dsp=f"${val:,.0f}";  gs=f"Goal: ${quota:,.0f}"
                        elif fmt=="%": dsp=f"{val:.1f}%";   gs=f"Goal: {quota}%"
                        else:          dsp=f"{int(val):,}"; gs=f"Goal: {int(quota):,}"
                        vc=vcolor(val,quota); bd=badge(val,quota)
                        col.markdown(f"""<div class="metric-card">
                        <div class="card-label">{lbl}</div><div class="card-value" style="color:{vc}">{dsp}</div>
                        <div class="card-goal">{gs} &nbsp; {bd}</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="background:#1a1a1a;border-radius:10px;padding:14px 18px;margin-top:8px">
        <div style="color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Closed Deals / Revenue / Spread</div>
        <div style="color:#cdd6f4;font-size:13px">Use <b>Log Weekly Results</b> (manager page) to log closed deals, revenue, and spread.
        That unlocks the full performance score and percentage metrics.</div>
        </div>""", unsafe_allow_html=True)

# ─── LOG WEEKLY RESULTS ───────────────────────────────────────────────────────
elif page=="Log Weekly Results":
    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px">Log Weekly Results</div>
    <div style="color:#ffcccc;font-size:14px;margin-top:2px">Manager use — log closed deals, revenue & spread each week</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#1a0a00;border:1px solid #cc0000;border-radius:10px;
    padding:14px 20px;margin-bottom:20px">
    <div style="color:#f9e2af;font-weight:bold;font-size:13px">FOR MANAGERS ONLY</div>
    <div style="color:#cdd6f4;font-size:13px;margin-top:4px">
    Reps log their daily numbers (calls, talk time, appointments, offers, contracts) in the
    <b>Daily Numbers</b> page — no entry needed here for those.<br><br>
    This page is for logging <b>closed deals, revenue, and spread</b> once a week.
    These numbers unlock the full performance score and percentage metrics on each rep's profile.
    </div>
    </div>""", unsafe_allow_html=True)

    # ── Add / manage reps ──
    with st.expander("Add New Rep", expanded=not bool(data["reps"])):
        nr = st.text_input("Rep Name")
        if st.button("Add Rep", type="primary"):
            if nr and nr not in data["reps"]:
                data["reps"].append(nr)
                data["entries"].setdefault(nr, {})
                save_data(data); st.success(f"{nr} added!"); st.rerun()
            elif nr in data["reps"]:
                st.warning("Rep already exists.")

    st.markdown("---")
    if not data["reps"]: st.info("Add a rep above to get started."); st.stop()

    rep  = st.selectbox("Select Rep", data["reps"], key="log_rep")
    week = st.text_input("Week of (Monday's date — YYYY-MM-DD)", value=week_key())

    st.markdown('<div class="section-hdr">Weekly Results</div>', unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1: closed  = st.number_input("Closed Deals",    min_value=0, value=0)
    with r2: revenue = st.number_input("Revenue ($)",     min_value=0, value=0)
    with r3: spread  = st.number_input("Total Spread ($)",min_value=0, value=0)

    if st.button("Save Weekly Results", type="primary"):
        try:
            datetime.strptime(week, "%Y-%m-%d")
            existing = data["entries"].setdefault(rep, {}).get(week, {})
            # Keep any existing activity fields (from old entries), only update results
            existing.update({"closed_deals": closed, "revenue": revenue, "spread": spread})
            data["entries"][rep][week] = existing
            save_data(data)
            st.success(f"Results saved for {rep} — week of {week}!")
        except ValueError:
            st.error("Invalid date format. Use YYYY-MM-DD.")

    # ── Show what's already logged this month ──
    st.markdown('<div class="section-hdr">Already Logged This Month</div>', unsafe_allow_html=True)
    month_entries = {w:e for w,e in data["entries"].get(rep,{}).items() if w.startswith(month_key())}
    if month_entries:
        for wk in sorted(month_entries.keys(), reverse=True):
            e = month_entries[wk]
            st.markdown(f"""<div style="background:#1a1a1a;border-radius:8px;padding:12px 16px;
            margin-bottom:6px;border-left:3px solid #cc0000;display:flex;justify-content:space-between;align-items:center">
            <div style="color:#cdd6f4;font-size:13px">Week of {fmt_date(wk)}</div>
            <div style="color:#888;font-size:13px">
              {int(e.get("closed_deals",0))} closed &nbsp;·&nbsp;
              ${e.get("revenue",0):,.0f} revenue &nbsp;·&nbsp;
              ${e.get("spread",0):,.0f} spread
            </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info(f"No weekly results logged yet for {month_label(month_key())}.")
