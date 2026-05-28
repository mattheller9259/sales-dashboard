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
if "daily_logs"      not in data: data["daily_logs"]={}
if "pins"            not in data: data["pins"]={}
if "coaching_notes"  not in data: data["coaching_notes"]={}

DAILY_GOALS={"calls":30,"talk_time":120}

def get_daily_score(log):
    # Contracts carry the most weight — getting 1 deal = 45pts
    calls=log.get("calls",0); talk=log.get("talk_time",0)
    appts=log.get("appointments",0); offers=log.get("offers",0)
    contracts=log.get("contracts",0)
    offer_rate=(offers/appts*100) if appts>0 else 0
    s = (min(contracts/1,1)*45 + min(calls/30,1)*25 +
         min(talk/120,1)*20    + min(offer_rate/100,1)*10)
    return round(s,1)

def get_commit_stats(rep, data, week_start, month_start, today_dt):
    """Returns commitment hit counts for the current week and month."""
    commits = data.get("commitments", {}).get(rep, {})
    streak  = get_streak(rep, data)
    week_hits=0; week_submitted=0; week_dots=""
    cur = week_start
    while cur <= today_dt:
        if cur.weekday() < 5:
            dk = cur.strftime("%Y-%m-%d")
            c  = commits.get(dk)
            if c is not None:
                week_submitted += 1
                if   c.get("hit")==True:  week_hits+=1; week_dots+='<span style="color:#22c55e;font-size:16px" title="Hit">●</span> '
                elif c.get("hit")==False: week_dots+='<span style="color:#cc0000;font-size:16px" title="Missed">●</span> '
                else:                     week_dots+='<span style="color:#f59e0b;font-size:16px" title="Pending">●</span> '
            else:
                week_dots+='<span style="color:#2a2a2a;font-size:16px" title="Not submitted">●</span> '
        cur += timedelta(days=1)
    month_hits=0; month_submitted=0
    cur = month_start
    while cur <= today_dt:
        if cur.weekday() < 5:
            dk = cur.strftime("%Y-%m-%d")
            c  = commits.get(dk)
            if c is not None:
                month_submitted += 1
                if c.get("hit")==True: month_hits += 1
        cur += timedelta(days=1)
    hit_rate = round(month_hits/month_submitted*100) if month_submitted>0 else 0
    score    = round(hit_rate*0.7 + min(streak/30,1)*30, 1)
    return {"week_hits":week_hits,"week_submitted":week_submitted,"week_dots":week_dots,
            "month_hits":month_hits,"month_submitted":month_submitted,
            "hit_rate":hit_rate,"streak":streak,"score":score}

def get_pace_projection(rep, data, today_dt, month_start):
    """Project end-of-month totals based on current daily-log pace."""
    try:
        next_mo   = (today_dt.replace(day=28)+timedelta(days=4)).replace(day=1)
        month_end = next_mo - timedelta(days=1)
        wd_elapsed= sum(1 for i in range((today_dt-month_start).days+1)
                        if (month_start+timedelta(days=i)).weekday()<5)
        wd_total  = sum(1 for i in range((month_end-month_start).days+1)
                        if (month_start+timedelta(days=i)).weekday()<5)
        mt = get_daily_range_totals(rep, data, month_start, today_dt)
        if wd_elapsed==0 or mt["days_logged"]==0: return None
        proj={}
        for k in ["calls","talk_time","appointments","offers","contracts"]:
            proj[k]=round(mt[k]/wd_elapsed*wd_total)
        proj["wd_elapsed"]=wd_elapsed; proj["wd_total"]=wd_total
        proj["current"]={k:mt[k] for k in ["calls","talk_time","appointments","offers","contracts"]}
        return proj
    except: return None

def get_weekly_trend(rep, data, num_weeks=6):
    """Weekly call/talk/contract totals for the last N weeks."""
    today_dt = datetime.now().date()
    this_mon = today_dt - timedelta(days=today_dt.weekday())
    rows=[]
    for w in range(num_weeks-1,-1,-1):
        ws = this_mon - timedelta(weeks=w)
        we = ws + timedelta(days=4)
        wt = get_daily_range_totals(rep, data, ws, min(we, today_dt))
        if wt["calls"]>0 or wt["contracts"]>0 or wt["talk_time"]>0:
            rows.append({"Week":ws.strftime("%m/%d"),
                         "Calls":wt["calls"],"Talk Time":wt["talk_time"],
                         "Contracts":wt["contracts"],"Appts":wt["appointments"]})
    return rows

def get_weekly_score(wt):
    """0-100 score for a week's daily-log totals.
    Weights: contracts 40 | calls 25 | talk time 20 | appt→contract% 15"""
    calls=wt.get("calls",0); talk=wt.get("talk_time",0)
    appts=wt.get("appointments",0); cons=wt.get("contracts",0)
    acp=(cons/appts*100) if appts>0 else 0
    s=(min(cons/3,1)*40  + min(calls/150,1)*25 +
       min(talk/600,1)*20 + min(acp/20,1)*15)
    return round(s, 1)

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

def get_standards_compliance(rep, data, month_start, today_dt):
    logs = data.get("daily_logs", {}).get(rep, {})
    days_logged=0; calls_hit=0; talk_hit=0; both_hit=0; wd_elapsed=0
    cur = month_start
    while cur <= today_dt:
        if cur.weekday() < 5:
            wd_elapsed += 1
            log = logs.get(cur.strftime("%Y-%m-%d"))
            if log:
                days_logged += 1
                c = log.get("calls",0) >= 30
                t = log.get("talk_time",0) >= 120
                if c: calls_hit += 1
                if t: talk_hit += 1
                if c and t: both_hit += 1
        cur += timedelta(days=1)
    lp = round(days_logged/wd_elapsed*100) if wd_elapsed>0 else 0
    cp = round(calls_hit/days_logged*100)   if days_logged>0 else 0
    tp = round(talk_hit/days_logged*100)    if days_logged>0 else 0
    bp = round(both_hit/days_logged*100)    if days_logged>0 else 0
    return {"days_logged":days_logged,"wd_elapsed":wd_elapsed,
            "calls_hit":calls_hit,"talk_hit":talk_hit,"both_hit":both_hit,
            "log_pct":lp,"calls_pct":cp,"talk_pct":tp,"both_pct":bp}

def get_consecutive_miss(rep, data):
    logs = data.get("daily_logs",{}).get(rep,{})
    today_dt = datetime.now().date()
    no_log=0; below=0
    check = today_dt - timedelta(days=1)
    for _ in range(30):
        if check.weekday()>=5: check-=timedelta(days=1); continue
        log=logs.get(check.strftime("%Y-%m-%d"))
        if not log: no_log+=1; check-=timedelta(days=1)
        else: break
    check = today_dt - timedelta(days=1)
    for _ in range(30):
        if check.weekday()>=5: check-=timedelta(days=1); continue
        log=logs.get(check.strftime("%Y-%m-%d"))
        if not log or (log.get("calls",0)<30 and log.get("talk_time",0)<120):
            below+=1; check-=timedelta(days=1)
        else: break
    return {"no_log":no_log,"below_standards":below}

def get_accountability_score(rep, data, month_start, today_dt):
    comp = get_standards_compliance(rep, data, month_start, today_dt)
    week_start2 = today_dt - timedelta(days=today_dt.weekday())
    cs = get_commit_stats(rep, data, week_start2, month_start, today_dt)
    score = (min(comp["log_pct"],100)*0.25 + min(comp["calls_pct"],100)*0.25 +
             min(comp["talk_pct"],100)*0.25 + min(cs["hit_rate"],100)*0.25)
    return round(score,1)

with st.sidebar:
    st.markdown("""<div style="background:#ffffff;border-radius:10px;padding:8px 14px;text-align:center;margin-bottom:4px">
    <img src="https://raw.githubusercontent.com/mattheller9259/sales-dashboard/main/logo.png" style="max-width:100%;height:auto;max-height:54px">
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    page=st.radio("Navigate",["Team Overview","Daily Numbers","Daily Commitments","Individual Rep","Weekly Recap","Log Weekly Results","Month-End Summary","How to Use"],label_visibility="collapsed")
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
    st.markdown("""<div style="background:linear-gradient(90deg,#0d0d0d,#1a0000,#0d0d0d);
    border:1px solid #cc0000;border-radius:12px;padding:24px;margin-bottom:16px;text-align:center">
    <div style="margin-bottom:14px">
      <div style="background:#ffffff;border-radius:8px;padding:6px 18px;display:inline-block">
        <img src="https://raw.githubusercontent.com/mattheller9259/sales-dashboard/main/logo.png" style="height:42px;display:block">
      </div>
    </div>
    <div style="color:#ffffff;font-size:48px;font-weight:900;letter-spacing:3px;line-height:1">WIN THE DAY</div>
    <div style="color:#888;font-size:13px;margin-top:8px;letter-spacing:1px">Every call. Every minute. Every day.</div>
    <div style="margin-top:16px;border-top:1px solid rgba(204,0,0,0.25);padding-top:14px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">⚡ Demand Enthusiasm</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">💪 Embrace Hard Work</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">📈 Insist on Growth</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">🤝 Live Honestly</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">🏆 Celebrate Teamwork</span>
    </div>
    </div>""", unsafe_allow_html=True)

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
        needs_div = f'<div style="margin-top:8px;color:#666;font-size:11px;font-style:italic">{needs_html}</div>' if needs_html else ""
        st.markdown(
            f'<div class="{card}"><div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px">'
            f'<div style="flex:1;min-width:0"><div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">'
            f'<span style="font-size:26px;line-height:1">{medal}</span>'
            f'<span style="color:#ffffff;font-size:19px;font-weight:bold">{rep}{stk}</span></div>'
            f'<span class="{tag_cls}">{tag_txt}</span>'
            f'<div style="margin-top:12px;font-size:13px;line-height:1.8">{stats_html}</div>'
            f'{needs_div}</div>'
            f'<div style="text-align:right;flex-shrink:0">'
            f'<div style="color:{sc_col};font-size:44px;font-weight:bold;line-height:1">{score:.0f}</div>'
            f'<div style="color:#444;font-size:11px">/ 100</div>'
            f'</div></div></div>',
            unsafe_allow_html=True)

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

    # ── Consecutive miss alerts ────────────────────────────────────────────────
    miss_alerts=[]
    for r in data["reps"]:
        cm=get_consecutive_miss(r,data)
        if cm["no_log"]>=2:
            miss_alerts.append((r,f"Has not logged numbers for <b>{cm['no_log']} consecutive days</b>","no_log"))
        elif cm["below_standards"]>=2:
            miss_alerts.append((r,f"Below standards (calls + talk time) for <b>{cm['below_standards']} consecutive days</b>","below"))
    if miss_alerts:
        rows_html="".join([f'<div style="color:#f38ba8;font-size:13px;margin-top:6px">⚠️ <b>{r}</b> — {msg}</div>' for r,msg,_ in miss_alerts])
        st.markdown(f"""<div class="alert-box">
        <div style="color:#f38ba8;font-weight:bold;font-size:14px">🚨 ACCOUNTABILITY ALERT</div>
        {rows_html}
        </div>""", unsafe_allow_html=True)

    # ── FIVE COMPETITIVE TABS ─────────────────────────────────────────────────
    tab_day, tab_week, tab_month, tab_commit, tab_standards = st.tabs(["🔥  TODAY", "📅  THIS WEEK", "📊  THIS MONTH", "🎯  COMMITMENTS", "📋  STANDARDS"])

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

    # ── COMMITMENTS ────────────────────────────────────────────────────────────
    with tab_commit:
        c_board=[]
        for rep in data["reps"]:
            cs=get_commit_stats(rep,data,week_start,month_start,today_dt)
            c_board.append((rep,cs))
        c_board.sort(key=lambda x:(x[1]["score"],x[1]["streak"]),reverse=True)
        c_total=len(c_board)

        # Team summary
        submitted=[cs for _,cs in c_board if cs["month_submitted"]>0]
        if submitted:
            st.markdown('<div class="section-hdr">Team Commitment Health</div>', unsafe_allow_html=True)
            sc1,sc2,sc3,sc4=st.columns(4)
            avg_rate=round(sum(cs["hit_rate"] for cs in submitted)/len(submitted))
            top_streak=max(cs["streak"] for cs in submitted)
            total_hits=sum(cs["month_hits"] for cs in submitted)
            total_sub =sum(cs["month_submitted"] for cs in submitted)
            sc1.metric("Avg Hit Rate",   f"{avg_rate}%",      "Goal: 80%+")
            sc2.metric("Team Hits",      f"{total_hits}/{total_sub}", "This month")
            sc3.metric("Longest Streak", f"{top_streak}d 🔥",  "Current")
            sc4.metric("Reps Tracked",   len(submitted))

        st.markdown('<div class="section-hdr">Commitment Leaderboard</div>', unsafe_allow_html=True)

        for rank,(rep,cs) in enumerate(c_board,1):
            streak=cs["streak"]
            score =cs["score"]
            leader_score=c_board[0][1]["score"]
            gap=leader_score-score

            # Tag
            if rank==1:
                card,tag_cls="lb-rank1","tag-king"
                tag_txt="🏆 MOST COMMITTED" if streak<5 else f"🏆 MOST COMMITTED &nbsp; 🔥 {streak}-DAY STREAK"
                sc_col="#f9e2af"
            elif rank==2:
                card,tag_cls="lb-rank2","tag-chase"
                tag_txt=f"💪 CONSISTENT — {gap:.1f} PTS BEHIND"
                sc_col="#60a5fa"
            elif rank==c_total and c_total>=3:
                card,tag_cls="lb-last","tag-last"
                tag_txt="⚠️ WORK ON YOUR WORD"
                sc_col="#f38ba8"
            else:
                card,tag_cls="lb-hunt","tag-hunt"
                tag_txt=f"📈 BUILDING — {gap:.1f} PTS BACK"
                sc_col="#a6e3a1"

            stk=f'&nbsp;&nbsp;<span style="color:#f9e2af;font-size:12px">🔥 {streak}d</span>' if streak>0 and rank>1 else ""
            month_bar_pct=cs["hit_rate"]
            bar_col="#22c55e" if month_bar_pct>=80 else "#f59e0b" if month_bar_pct>=50 else "#cc0000"

            # Week dots label
            week_label=""
            for i,day in enumerate(["M","T","W","T","F"]):
                week_label+=f'<span style="color:#555;font-size:10px;margin-right:1px">{day}</span>&nbsp;'

            st.markdown(f"""<div class="{card}">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px">
              <div style="flex:1;min-width:0">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
                  <span style="font-size:26px;line-height:1">{"🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"#{rank}"}</span>
                  <span style="color:#ffffff;font-size:19px;font-weight:bold">{rep}{stk}</span>
                </div>
                <span class="{tag_cls}">{tag_txt}</span>
                <div style="margin-top:14px">
                  <div style="color:#666;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">This Week</div>
                  <div>{cs["week_dots"] if cs["week_dots"] else '<span style="color:#333;font-size:13px">No commitments submitted this week</span>'}</div>
                  <div style="color:#555;font-size:11px;margin-top:4px">{cs["week_hits"]} of {cs["week_submitted"]} submitted days hit</div>
                </div>
                <div style="margin-top:12px">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                    <span style="color:#666;font-size:10px;text-transform:uppercase;letter-spacing:1px">This Month</span>
                    <span style="color:{bar_col};font-size:12px;font-weight:bold">{cs["month_hits"]}/{cs["month_submitted"]} days &nbsp;({cs["hit_rate"]}%)</span>
                  </div>
                  <div style="background:#1e1e1e;border-radius:6px;height:8px;overflow:hidden">
                    <div style="background:{bar_col};height:100%;width:{month_bar_pct}%;border-radius:6px;transition:width 0.3s"></div>
                  </div>
                </div>
              </div>
              <div style="text-align:right;flex-shrink:0;min-width:80px">
                <div style="color:{sc_col};font-size:40px;font-weight:bold;line-height:1">{cs["hit_rate"]}</div>
                <div style="color:#444;font-size:11px">% hit rate</div>
                <div style="color:#f9e2af;font-size:13px;margin-top:6px">{"🔥 "+str(streak)+"d" if streak>0 else ""}</div>
              </div>
            </div>
            </div>""", unsafe_allow_html=True)

        if not c_board: st.info("No commitment data yet. Have reps submit daily commitments.")

    # ── STANDARDS ──────────────────────────────────────────────────────────────
    with tab_standards:
        st.markdown('<div class="section-hdr">Standards & Leading Indicators — This Month</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#666;font-size:12px;margin-bottom:16px">Daily standards: 30 calls/day &nbsp;·&nbsp; 120 min talk time/day &nbsp;·&nbsp; Log every workday &nbsp;&nbsp;|&nbsp;&nbsp; Leading indicators: 12 contracts/month &nbsp;·&nbsp; 20% appt→contract</div>', unsafe_allow_html=True)

        s_board=[]
        for rep in data["reps"]:
            comp=get_standards_compliance(rep,data,month_start,today_dt)
            acct=get_accountability_score(rep,data,month_start,today_dt)
            cm=get_consecutive_miss(rep,data)
            mt=get_daily_range_totals(rep,data,month_start,today_dt)
            s_board.append((rep,comp,acct,cm,mt))
        s_board.sort(key=lambda x:x[2],reverse=True)

        for rep,comp,acct,cm,mt in s_board:
            lc=vcolor(comp["log_pct"],80);  cc=vcolor(comp["calls_pct"],80)
            tc=vcolor(comp["talk_pct"],80); bc=vcolor(comp["both_pct"],80)
            ac_col="#a6e3a1" if acct>=80 else "#f9e2af" if acct>=60 else "#f38ba8"
            flag=""
            if cm["no_log"]>=2:           flag=f'<span style="color:#f38ba8;font-size:10px"> &nbsp;⚠️ {cm["no_log"]}d no log</span>'
            elif cm["below_standards"]>=2: flag=f'<span style="color:#f9e2af;font-size:10px"> &nbsp;⚠️ {cm["below_standards"]}d below stds</span>'

            cons_m  = mt["contracts"];  appts_m = mt["appointments"]
            acp_m   = round(cons_m/appts_m*100) if appts_m>0 else 0
            cons_col= vcolor(cons_m,12); acp_col=vcolor(acp_m,20)
            cons_bar= min(round(cons_m/12*100),100)
            acp_bar = min(acp_m,100)

            st.markdown(f"""<div style="background:#1a1a1a;border-radius:12px;padding:18px 22px;margin-bottom:12px;border-left:4px solid #cc0000">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
              <div style="color:#ffffff;font-size:17px;font-weight:bold">{rep}{flag}</div>
              <div style="text-align:center">
                <div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px">Accountability Score</div>
                <div style="color:{ac_col};font-size:26px;font-weight:bold;line-height:1.1">{acct}<span style="color:#444;font-size:12px">/100</span></div>
              </div>
            </div>

            <div style="color:#555;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">Daily Activity Standards</div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:16px">
              <div style="background:#111;border-radius:8px;padding:10px;text-align:center">
                <div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Days Logged</div>
                <div style="color:{lc};font-size:20px;font-weight:bold">{comp["days_logged"]}/{comp["wd_elapsed"]}</div>
                <div style="background:#2a2a2a;border-radius:3px;height:4px;margin-top:6px"><div style="background:{lc};width:{comp["log_pct"]}%;height:100%;border-radius:3px"></div></div>
                <div style="color:#444;font-size:10px;margin-top:4px">{comp["log_pct"]}%</div>
              </div>
              <div style="background:#111;border-radius:8px;padding:10px;text-align:center">
                <div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Calls ≥ 30/day</div>
                <div style="color:{cc};font-size:20px;font-weight:bold">{comp["calls_hit"]} days</div>
                <div style="background:#2a2a2a;border-radius:3px;height:4px;margin-top:6px"><div style="background:{cc};width:{comp["calls_pct"]}%;height:100%;border-radius:3px"></div></div>
                <div style="color:#444;font-size:10px;margin-top:4px">{comp["calls_pct"]}% of logged days</div>
              </div>
              <div style="background:#111;border-radius:8px;padding:10px;text-align:center">
                <div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Talk ≥ 120 min/day</div>
                <div style="color:{tc};font-size:20px;font-weight:bold">{comp["talk_hit"]} days</div>
                <div style="background:#2a2a2a;border-radius:3px;height:4px;margin-top:6px"><div style="background:{tc};width:{comp["talk_pct"]}%;height:100%;border-radius:3px"></div></div>
                <div style="color:#444;font-size:10px;margin-top:4px">{comp["talk_pct"]}% of logged days</div>
              </div>
              <div style="background:#111;border-radius:8px;padding:10px;text-align:center">
                <div style="color:#666;font-size:9px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Both Standards Hit</div>
                <div style="color:{bc};font-size:20px;font-weight:bold">{comp["both_hit"]} days</div>
                <div style="background:#2a2a2a;border-radius:3px;height:4px;margin-top:6px"><div style="background:{bc};width:{comp["both_pct"]}%;height:100%;border-radius:3px"></div></div>
                <div style="color:#444;font-size:10px;margin-top:4px">{comp["both_pct"]}% of logged days</div>
              </div>
            </div>

            <div style="border-top:1px solid #222;padding-top:14px">
              <div style="color:#555;font-size:9px;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px">Leading Indicators</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
                <div>
                  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
                    <span style="color:#aaa;font-size:12px;font-weight:bold">📝 Contracts This Month</span>
                    <span style="color:{cons_col};font-size:16px;font-weight:bold">{int(cons_m)} <span style="color:#444;font-size:11px">/ 12 goal</span></span>
                  </div>
                  <div style="background:#2a2a2a;border-radius:5px;height:8px"><div style="background:{cons_col};width:{cons_bar}%;height:100%;border-radius:5px"></div></div>
                  <div style="color:#555;font-size:10px;margin-top:4px">{cons_bar}% to goal</div>
                </div>
                <div>
                  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
                    <span style="color:#aaa;font-size:12px;font-weight:bold">📅 Appt → Contract %</span>
                    <span style="color:{acp_col};font-size:16px;font-weight:bold">{acp_m}% <span style="color:#444;font-size:11px">goal: 20%</span></span>
                  </div>
                  <div style="background:#2a2a2a;border-radius:5px;height:8px"><div style="background:{acp_col};width:{acp_bar}%;height:100%;border-radius:5px"></div></div>
                  <div style="color:#555;font-size:10px;margin-top:4px">{int(mt["appointments"])} appts &nbsp;·&nbsp; {int(cons_m)} contracts</div>
                </div>
              </div>
            </div>
            </div>""", unsafe_allow_html=True)

        if not s_board: st.info("Add reps to get started.")
        st.markdown("""<div style="margin-top:10px;display:flex;gap:16px;flex-wrap:wrap">
        <span style="color:#a6e3a1;font-size:11px">● 80%+ On Track</span>
        <span style="color:#f9e2af;font-size:11px">● 60–79% Close</span>
        <span style="color:#f38ba8;font-size:11px">● Below 60% Behind</span>
        <span style="color:#555;font-size:11px">Accountability Score = log rate + calls compliance + talk compliance + commitment hit rate</span>
        </div>""", unsafe_allow_html=True)

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
        if data["pins"].get(rep):
            pin_input = st.text_input("Enter your PIN", type="password", max_chars=4, key="daily_pin")
            if not pin_input: st.info("Enter your 4-digit PIN to continue."); st.stop()
            if pin_input != data["pins"][rep]: st.error("Incorrect PIN. Try again."); st.stop()
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
        if data["pins"].get(rep):
            pin_c=st.text_input("Enter your PIN",type="password",max_chars=4,key="commit_pin")
            if not pin_c: st.info("Enter your 4-digit PIN to continue."); st.stop()
            if pin_c != data["pins"][rep]: st.error("Incorrect PIN. Try again."); st.stop()
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
    import plotly.graph_objects as go
    if not data["reps"]: st.info("No reps yet."); st.stop()
    rep = st.selectbox("Select Rep", data["reps"])

    today_dt    = datetime.now().date()
    week_start  = today_dt - timedelta(days=today_dt.weekday())
    month_start = today_dt.replace(day=1)

    t      = get_monthly(rep, sel_month, data)
    streak = get_streak(rep, data)

    # ── Header ──
    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:20px;font-weight:bold;letter-spacing:1px">{rep}</div>
    <div style="color:#ffcccc;font-size:13px;margin-top:2px">{month_label(sel_month)}</div>
    </div>""", unsafe_allow_html=True)

    # ── Score card ──
    acct_score = get_accountability_score(rep, data, month_start, today_dt)
    acct_col = "#a6e3a1" if acct_score>=80 else "#f9e2af" if acct_score>=60 else "#f38ba8"
    if t:
        sc=t["score"]; grade="A" if sc>=90 else "B" if sc>=80 else "C" if sc>=70 else "D" if sc>=60 else "F"
        sc_col="#a6e3a1" if sc>=80 else "#f9e2af" if sc>=60 else "#f38ba8"
        gbg="#a6e3a1" if grade in ["A","B"] else "#f9e2af" if grade=="C" else "#f38ba8"
        st.markdown(f"""<div style="background:#1a1a1a;border-radius:12px;padding:20px;margin-bottom:16px;
        display:flex;justify-content:space-between;align-items:center;border-top:2px solid #cc0000;gap:16px;flex-wrap:wrap">
        <div>
          <div style="color:#888;font-size:11px;text-transform:uppercase;letter-spacing:1px">Performance Score</div>
          <div style="color:{sc_col};font-size:50px;font-weight:bold;line-height:1.1">{sc}<span style="color:#888;font-size:20px">/100</span></div>
          <div style="color:#f9e2af;font-size:13px">{"🔥 "+str(streak)+"-day commitment streak" if streak>0 else "No active streak"}</div>
        </div>
        <div style="text-align:center">
          <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px">Accountability</div>
          <div style="color:{acct_col};font-size:36px;font-weight:bold;line-height:1">{acct_score}</div>
          <div style="color:#444;font-size:11px">/100</div>
        </div>
        <div style="background:{gbg};color:#1e1e2e;width:68px;height:68px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:30px">{grade}</div>
        </div>""", unsafe_allow_html=True)
    elif streak>0:
        st.markdown(f'<div style="color:#f9e2af;font-size:14px;margin-bottom:12px">🔥 {streak}-day commitment streak</div>', unsafe_allow_html=True)

    ir_tab1,ir_tab2,ir_tab3,ir_tab4 = st.tabs(["📊 Overview","📈 Trends","🏆 Results","📝 Notes"])

    # ── TAB 1: OVERVIEW ────────────────────────────────────────────────────────
    with ir_tab1:
        # On-Pace This Month
        proj = get_pace_projection(rep, data, today_dt, month_start)
        if proj:
            st.markdown(f'<div class="section-hdr">On Pace This Month — {proj["wd_elapsed"]} of {proj["wd_total"]} workdays elapsed</div>', unsafe_allow_html=True)
            pace_items=[
                ("Calls",       proj["current"]["calls"],       proj["calls"],       600,  ""),
                ("Talk Time",   proj["current"]["talk_time"],   proj["talk_time"],   2400, " min"),
                ("Appointments",proj["current"]["appointments"],proj["appointments"],None, ""),
                ("Offers",      proj["current"]["offers"],      proj["offers"],      None, ""),
                ("Contracts",   proj["current"]["contracts"],   proj["contracts"],   12,   ""),
            ]
            pc=st.columns(5)
            for i,(lbl,cur_v,prj_v,goal,unit) in enumerate(pace_items):
                if goal:
                    r=prj_v/goal
                    if r>=1.0:   status,sc2="ON PACE ✅","#22c55e"
                    elif r>=0.8: status,sc2="CLOSE ⚠️","#f59e0b"
                    else:        status,sc2="BEHIND 🔴","#cc0000"
                    gs=f'<span style="color:{sc2};font-size:11px;font-weight:bold">{status}</span>'
                    sub=f"Projected: {int(prj_v)}{unit} / Goal: {int(goal)}{unit}"
                else:
                    gs=""; sub=f"Projected: {int(prj_v)}{unit}"
                pc[i].markdown(f"""<div class="metric-card">
                <div class="card-label">{lbl}</div>
                <div class="card-value" style="color:#ffffff">{int(cur_v)}{unit}</div>
                <div class="card-goal">{sub}</div>
                <div style="margin-top:4px">{gs}</div></div>""", unsafe_allow_html=True)

        # This Week
        st.markdown('<div class="section-hdr">This Week — Daily Pacing</div>', unsafe_allow_html=True)
        wt=get_daily_range_totals(rep,data,week_start,today_dt)
        days_elapsed=min(today_dt.weekday()+1,5)
        if wt["days_logged"]==0:
            st.info(f"No daily numbers logged this week yet.")
        else:
            wc1,wc2,wc3,wc4,wc5=st.columns(5)
            for col,lbl,val,dg,unit,hg in [(wc1,"Calls",wt["calls"],30,"",True),(wc2,"Talk Time",wt["talk_time"],120," min",True),(wc3,"Appointments",wt["appointments"],0,"",False),(wc4,"Offers",wt["offers"],0,"",False),(wc5,"Contracts",wt["contracts"],0,"",False)]:
                if hg: pace=dg*days_elapsed; vc=vcolor(val,pace); bd=badge(val,pace); gs=f"Pace: {int(pace)}{unit} &nbsp; {bd}"
                elif lbl=="Contracts": vc="#22c55e" if val>=3 else "#f9e2af" if val>=1 else "#fff"; gs="Goal: 3/week"
                else: vc,gs="#ffffff","--"
                col.markdown(f"""<div class="metric-card"><div class="card-label">{lbl}</div>
                <div class="card-value" style="color:{vc}">{int(val)}{unit}</div>
                <div class="card-goal">{gs}</div></div>""", unsafe_allow_html=True)
            st.markdown('<div class="section-hdr">Day-by-Day This Week</div>', unsafe_allow_html=True)
            st.markdown("""<div style="display:grid;grid-template-columns:130px 90px 100px 90px 90px 100px;
            gap:6px;padding:6px 14px;color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">
            <div>Day</div><div>Calls</div><div>Talk Time</div><div>Appts</div><div>Offers</div><div>Contracts</div>
            </div>""", unsafe_allow_html=True)
            for dk,entry in sorted(wt["day_entries"]):
                dl=datetime.strptime(dk,"%Y-%m-%d").strftime("%a %b %d")
                cv=entry.get("calls",0); tv2=entry.get("talk_time",0); av=entry.get("appointments",0)
                ov=entry.get("offers",0); kv=entry.get("contracts",0)
                st.markdown(f"""<div style="display:grid;grid-template-columns:130px 90px 100px 90px 90px 100px;
                gap:6px;padding:11px 14px;background:#1a1a1a;border-radius:8px;margin-bottom:5px;border-left:2px solid #333;align-items:center">
                <div style="color:#cdd6f4;font-size:13px;font-weight:bold">{dl}</div>
                <div style="color:{vcolor(cv,30)};font-weight:bold">{int(cv)}/30</div>
                <div style="color:{vcolor(tv2,120)};font-weight:bold">{int(tv2)} min</div>
                <div style="color:#fff">{int(av)}</div><div style="color:#fff">{int(ov)}</div>
                <div style="color:{"#22c55e" if kv>=1 else "#fff"};font-weight:bold">{int(kv)}</div>
                </div>""", unsafe_allow_html=True)

        # ── Standards Compliance This Month ───────────────────────────────────
        comp = get_standards_compliance(rep, data, month_start, today_dt)
        if comp["wd_elapsed"] > 0:
            st.markdown('<div class="section-hdr">Standards Compliance This Month</div>', unsafe_allow_html=True)
            sc1,sc2,sc3,sc4 = st.columns(4)
            for col,lbl,val,goal in [(sc1,"Days Logged",f'{comp["days_logged"]}/{comp["wd_elapsed"]}',comp["log_pct"]),
                                     (sc2,"Call Standard (30+)",f'{comp["calls_hit"]} days',comp["calls_pct"]),
                                     (sc3,"Talk Standard (120+ min)",f'{comp["talk_hit"]} days',comp["talk_pct"]),
                                     (sc4,"Both Standards Hit",f'{comp["both_hit"]} days',comp["both_pct"])]:
                bar_col="#a6e3a1" if goal>=80 else "#f9e2af" if goal>=60 else "#f38ba8"
                col.markdown(f"""<div class="metric-card">
                <div class="card-label">{lbl}</div>
                <div class="card-value" style="color:{bar_col}">{val}</div>
                <div style="background:#2a2a2a;border-radius:4px;height:6px;margin-top:8px">
                  <div style="background:{bar_col};width:{goal}%;height:100%;border-radius:4px"></div>
                </div>
                <div class="card-goal" style="margin-top:4px">{goal}% compliance</div>
                </div>""", unsafe_allow_html=True)

        # ── Conversion Funnel ──────────────────────────────────────────────────
        if t or (comp["wd_elapsed"]>0 and comp["days_logged"]>0):
            month_key_cur = sel_month
            if month_key_cur == month_key():
                mt2 = get_daily_range_totals(rep, data, month_start, today_dt)
            else:
                sd2 = datetime.strptime(month_key_cur+"-01","%Y-%m-%d").date()
                se2 = (sd2.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
                mt2 = get_daily_range_totals(rep, data, sd2, se2)
            calls2=mt2["calls"]; appts2=mt2["appointments"]; offs2=mt2["offers"]
            cons2=mt2["contracts"]; closed2=t["closed_deals"] if t else 0
            if calls2>0:
                st.markdown('<div class="section-hdr">Conversion Funnel</div>', unsafe_allow_html=True)
                def funnel_pct(a,b): return f"{a/b*100:.0f}%" if b>0 else "--"
                def funnel_bar(a,b,col):
                    w=round(a/b*100) if b>0 else 0
                    return f'<div style="background:#2a2a2a;border-radius:6px;height:10px;flex:1"><div style="background:{col};width:{w}%;height:100%;border-radius:6px"></div></div>'
                stages=[
                    ("📞 Calls Made",     calls2, calls2,  "#cc0000"),
                    ("📅 Appointments",   appts2, calls2,  "#f59e0b"),
                    ("💼 Offers Made",    offs2,  appts2,  "#60a5fa"),
                    ("📝 Contracts",      cons2,  offs2,   "#a6e3a1"),
                    ("🏠 Closed Deals",   closed2,cons2,   "#22c55e"),
                ]
                for i,(lbl,val,prev,col) in enumerate(stages):
                    conv = funnel_pct(val,prev) if i>0 else "—"
                    bar  = funnel_bar(val,calls2,col)
                    st.markdown(f"""<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #1e1e1e">
                    <div style="width:160px;color:#cdd6f4;font-size:13px">{lbl}</div>
                    <div style="width:60px;color:{col};font-weight:bold;font-size:16px;text-align:right">{int(val)}</div>
                    {bar}
                    <div style="width:60px;color:#666;font-size:11px;text-align:right">{"→ "+conv if i>0 else ""}</div>
                    </div>""", unsafe_allow_html=True)

    # ── TAB 2: TRENDS ──────────────────────────────────────────────────────────
    with ir_tab2:
        trend=get_weekly_trend(rep,data,6)
        if not trend:
            st.info("No weekly data yet to show trends.")
        else:
            import pandas as pd
            df=pd.DataFrame(trend)
            st.markdown('<div class="section-hdr">Calls Per Week</div>', unsafe_allow_html=True)
            fig1=go.Figure(go.Bar(x=df["Week"],y=df["Calls"],marker_color="#cc0000",
                                  text=df["Calls"],textposition="outside",textfont_color="#ffffff"))
            fig1.add_hline(y=150,line_dash="dash",line_color="#f9e2af",annotation_text="Weekly Goal (150)",
                           annotation_font_color="#f9e2af")
            fig1.update_layout(template="plotly_dark",paper_bgcolor="#0d0d0d",plot_bgcolor="#1a1a1a",
                               height=280,margin=dict(t=20,b=20,l=0,r=0),
                               font_color="#ffffff",xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#2a2a2a"))
            st.plotly_chart(fig1,use_container_width=True)

            st.markdown('<div class="section-hdr">Talk Time Per Week (min)</div>', unsafe_allow_html=True)
            fig2=go.Figure(go.Bar(x=df["Week"],y=df["Talk Time"],marker_color="#8b0000",
                                  text=df["Talk Time"],textposition="outside",textfont_color="#ffffff"))
            fig2.add_hline(y=600,line_dash="dash",line_color="#f9e2af",annotation_text="Weekly Goal (600 min)",
                           annotation_font_color="#f9e2af")
            fig2.update_layout(template="plotly_dark",paper_bgcolor="#0d0d0d",plot_bgcolor="#1a1a1a",
                               height=280,margin=dict(t=20,b=20,l=0,r=0),
                               font_color="#ffffff",xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#2a2a2a"))
            st.plotly_chart(fig2,use_container_width=True)

            st.markdown('<div class="section-hdr">Contracts Per Week</div>', unsafe_allow_html=True)
            bar_cols=["#22c55e" if v>=3 else "#f59e0b" if v>=1 else "#cc0000" for v in df["Contracts"]]
            fig3=go.Figure(go.Bar(x=df["Week"],y=df["Contracts"],marker_color=bar_cols,
                                  text=df["Contracts"],textposition="outside",textfont_color="#ffffff"))
            fig3.add_hline(y=3,line_dash="dash",line_color="#f9e2af",annotation_text="Weekly Goal (3)",
                           annotation_font_color="#f9e2af")
            fig3.update_layout(template="plotly_dark",paper_bgcolor="#0d0d0d",plot_bgcolor="#1a1a1a",
                               height=280,margin=dict(t=20,b=20,l=0,r=0),
                               font_color="#ffffff",xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#2a2a2a"))
            st.plotly_chart(fig3,use_container_width=True)

    # ── TAB 3: RESULTS ─────────────────────────────────────────────────────────
    with ir_tab3:
        st.markdown(f'<div class="section-hdr">Activity This Month — {month_label(sel_month)}</div>', unsafe_allow_html=True)
        if sel_month==month_key():
            mt=get_daily_range_totals(rep,data,month_start,today_dt)
        else:
            sd=datetime.strptime(sel_month+"-01","%Y-%m-%d").date()
            se=(sd.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
            mt=get_daily_range_totals(rep,data,sd,se)
        if mt["days_logged"]==0:
            st.info(f"No daily numbers logged for {month_label(sel_month)} yet.")
        else:
            mc1,mc2,mc3,mc4,mc5=st.columns(5)
            for col,lbl,val,goal,unit in [(mc1,"Calls",mt["calls"],600,""),(mc2,"Talk Time",mt["talk_time"],2400," min"),(mc3,"Appointments",mt["appointments"],0,""),(mc4,"Offers",mt["offers"],0,""),(mc5,"Contracts",mt["contracts"],12,"")]:
                vc=vcolor(val,goal) if goal else "#fff"; gs=f"Goal: {goal}{unit} &nbsp; {badge(val,goal)}" if goal else "--"
                col.markdown(f"""<div class="metric-card"><div class="card-label">{lbl}</div>
                <div class="card-value" style="color:{vc}">{int(val)}{unit}</div>
                <div class="card-goal">{gs}</div></div>""", unsafe_allow_html=True)
        if t:
            st.markdown(f'<div class="section-hdr">Closed Results — {month_label(sel_month)}</div>', unsafe_allow_html=True)
            results=[("Closed Deals",t["closed_deals"],6,"n"),("Revenue",t["revenue"],100000,"$"),
                     ("Avg Spread/Deal",t["avg_spread"],17500,"$"),("Offer Rate",t["offer_pct"],100,"%"),
                     ("Appt to Contract",t["appt_con_pct"],20,"%"),("Contract to Close",t["con_close_pct"],75,"%")]
            for i in range(0,len(results),3):
                cols=st.columns(3)
                for j,col in enumerate(cols):
                    if i+j<len(results):
                        lbl2,val2,quota,fmt=results[i+j]
                        with col:
                            if fmt=="$": dsp=f"${val2:,.0f}"; gs=f"Goal: ${quota:,.0f}"
                            elif fmt=="%": dsp=f"{val2:.1f}%"; gs=f"Goal: {quota}%"
                            else: dsp=f"{int(val2):,}"; gs=f"Goal: {int(quota):,}"
                            col.markdown(f"""<div class="metric-card"><div class="card-label">{lbl2}</div>
                            <div class="card-value" style="color:{vcolor(val2,quota)}">{dsp}</div>
                            <div class="card-goal">{gs} &nbsp; {badge(val2,quota)}</div></div>""", unsafe_allow_html=True)
        else:
            st.info("Log closed deals, revenue, and spread in **Log Weekly Results** to see results here.")

    # ── TAB 4: COACHING NOTES ──────────────────────────────────────────────────
    with ir_tab4:
        notes=data["coaching_notes"].get(rep,[])
        today_dt2=datetime.now().date()

        # Due this week section
        due_soon=[n for n in notes if n.get("follow_up") and not n.get("completed") and
                  datetime.strptime(n["follow_up"],"%Y-%m-%d").date()<=today_dt2+timedelta(days=7)]
        if due_soon:
            st.markdown('<div class="section-hdr">⚠️ Action Items Due This Week</div>', unsafe_allow_html=True)
            for n in due_soon:
                fu=datetime.strptime(n["follow_up"],"%Y-%m-%d")
                overdue = fu.date()<today_dt2
                col_fu="#f38ba8" if overdue else "#f9e2af"
                lbl="OVERDUE" if overdue else f"Due {fu.strftime('%b %d')}"
                st.markdown(f"""<div style="background:#1a0a00;border-radius:8px;padding:12px 16px;
                margin-bottom:8px;border-left:4px solid {col_fu}">
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <div>
                    <div style="color:{col_fu};font-size:11px;font-weight:bold;margin-bottom:4px">{lbl} &nbsp;·&nbsp; {n.get("added_by","Manager")} &nbsp;·&nbsp; {n.get("date","")}</div>
                    <div style="color:#cdd6f4;font-size:13px">{n.get("note","")}</div>
                  </div>
                </div>
                </div>""", unsafe_allow_html=True)
                ni=notes.index(n)
                if st.button(f"Mark Complete ✅",key=f"complete_{rep}_{ni}"):
                    data["coaching_notes"][rep][ni]["completed"]=True
                    save_data(data); st.rerun()

        st.markdown('<div class="section-hdr">All Coaching Notes</div>', unsafe_allow_html=True)
        if notes:
            for idx,note in enumerate(reversed(notes[-15:])):
                ni=len(notes)-1-idx
                completed=note.get("completed",False)
                has_fu=bool(note.get("follow_up"))
                border_col="#22c55e" if completed else "#f9e2af" if has_fu else "#cc0000"
                fu_txt=""
                if has_fu:
                    fu_d=datetime.strptime(note["follow_up"],"%Y-%m-%d")
                    fu_txt=f' &nbsp;·&nbsp; <span style="color:{"#a6e3a1" if completed else "#f9e2af"}">{"✅ Done" if completed else "Follow up: "+fu_d.strftime("%b %d")}</span>'
                st.markdown(f"""<div style="background:#1a1a1a;border-radius:8px;padding:14px 18px;
                margin-bottom:8px;border-left:3px solid {border_col}">
                <div style="color:#888;font-size:11px;margin-bottom:6px">{note.get("date","")} &nbsp;·&nbsp; {note.get("added_by","Manager")}{fu_txt}</div>
                <div style="color:#cdd6f4;font-size:14px">{note.get("note","")}</div>
                </div>""", unsafe_allow_html=True)
                if has_fu and not completed:
                    if st.button("Mark Complete ✅",key=f"done_{rep}_{ni}"):
                        data["coaching_notes"][rep][ni]["completed"]=True
                        save_data(data); st.rerun()
        else:
            st.info("No coaching notes yet for this rep.")

        st.markdown('<div class="section-hdr">Add Note</div>', unsafe_allow_html=True)
        note_txt=st.text_area("Note",placeholder="e.g. Great week — offer rate improved. Work on follow-up calls.",height=100,key="note_input")
        na1,na2=st.columns(2)
        with na1: added_by=st.text_input("Your name",value="Manager",key="note_author")
        with na2: follow_up_date=st.date_input("Follow-up date (optional)",value=None,key="note_fu",help="Set a date to be reminded to follow up on this note")
        if st.button("Save Note",type="primary",key="save_note"):
            if note_txt.strip():
                new_note={"date":today_key(),"note":note_txt.strip(),
                          "added_by":added_by.strip() or "Manager","completed":False}
                if follow_up_date: new_note["follow_up"]=follow_up_date.strftime("%Y-%m-%d")
                data["coaching_notes"].setdefault(rep,[]).append(new_note)
                save_data(data); st.success("Note saved!"); st.rerun()
            else:
                st.warning("Please write a note first.")

# ─── WEEKLY RECAP ─────────────────────────────────────────────────────────────
elif page=="Weekly Recap":
    import pandas as pd
    today_dt   = datetime.now().date()
    # Default to last completed week; if Mon show last week, else show current week
    this_mon   = today_dt - timedelta(days=today_dt.weekday())
    last_mon   = this_mon - timedelta(weeks=1)
    last_fri   = last_mon + timedelta(days=4)

    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px">Weekly Recap</div>
    <div style="color:#ffcccc;font-size:14px;margin-top:2px">Monday morning review — how did the team do last week?</div>
    </div>""", unsafe_allow_html=True)

    if not data["reps"]: st.info("No reps yet."); st.stop()

    # Week selector
    wk_options={}
    for w in range(8):
        mon=this_mon-timedelta(weeks=w)
        fri=mon+timedelta(days=4)
        label=f"Week of {mon.strftime('%b %d')} – {fri.strftime('%b %d, %Y')}"
        wk_options[label]=mon
    sel_wk_label=st.selectbox("Select Week",list(wk_options.keys()),index=1)
    sel_wk_start=wk_options[sel_wk_label]
    sel_wk_end  =sel_wk_start+timedelta(days=4)

    st.markdown(f'<div class="section-hdr">Team Results — {sel_wk_label}</div>', unsafe_allow_html=True)

    # Build weekly totals per rep
    recap_rows=[]
    for rep in data["reps"]:
        wt=get_daily_range_totals(rep,data,sel_wk_start,min(sel_wk_end,today_dt))
        cs=get_commit_stats(rep,data,sel_wk_start,sel_wk_start,min(sel_wk_end,today_dt))
        recap_rows.append({"rep":rep,"wt":wt,"commits":cs})

    # Team summary
    logged_rows=[r for r in recap_rows if r["wt"]["days_logged"]>0]
    if logged_rows:
        sc1,sc2,sc3,sc4,sc5=st.columns(5)
        n=len(logged_rows)
        sc1.metric("Team Calls",    int(sum(r["wt"]["calls"] for r in logged_rows)),     f"Goal: {150*n}")
        sc2.metric("Talk Time",     f"{int(sum(r['wt']['talk_time'] for r in logged_rows))} min", f"Goal: {600*n} min")
        sc3.metric("Appointments",  int(sum(r["wt"]["appointments"] for r in logged_rows)))
        sc4.metric("Contracts",     int(sum(r["wt"]["contracts"] for r in logged_rows)), f"Goal: {3*n}")
        sc5.metric("Commitments",   f"{sum(r['commits']['week_hits'] for r in logged_rows)}/{sum(r['commits']['week_submitted'] for r in logged_rows)} hit")

    # Per-rep breakdown
    for row in recap_rows:
        rep=row["rep"]; wt=row["wt"]; cs=row["commits"]
        calls=wt["calls"]; talk=wt["talk_time"]; appts=wt["appointments"]
        cons=wt["contracts"]; offers=wt["offers"]
        acp=f"{cons/appts*100:.0f}%" if appts>0 else "--"
        logged_days=wt["days_logged"]

        def wk_badge(val,goal):
            if not goal: return ""
            r2=val/goal
            if r2>=1.0: return '<span class="badge-g">✅</span>'
            elif r2>=0.75: return '<span class="badge-y">⚠️</span>'
            else: return '<span class="badge-r">❌</span>'

        tc=vcolor(calls,150); tt=vcolor(talk,600); kc=vcolor(cons,3)
        commit_txt=f"{cs['week_hits']}/{cs['week_submitted']} days" if cs['week_submitted']>0 else "None submitted"
        commit_col="#22c55e" if cs['week_submitted']>0 and cs['week_hits']==cs['week_submitted'] else "#f9e2af" if cs['week_hits']>0 else "#888"

        st.markdown(f"""<div style="background:#1a1a1a;border-radius:12px;padding:18px 22px;margin-bottom:10px;border-left:4px solid #cc0000">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
          <div>
            <div style="color:#ffffff;font-size:17px;font-weight:bold;margin-bottom:8px">{rep}
              {"&nbsp;&nbsp;<span style='color:#888;font-size:12px'>No numbers logged this week</span>" if logged_days==0 else ""}
            </div>
            {"" if logged_days==0 else f"""
            <div style="display:flex;gap:24px;flex-wrap:wrap">
              <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Calls</div>
                <div style="color:{tc};font-size:18px;font-weight:bold">{int(calls)}<span style="color:#555;font-size:12px">/150</span> &nbsp;{wk_badge(calls,150)}</div></div>
              <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Talk Time</div>
                <div style="color:{tt};font-size:18px;font-weight:bold">{int(talk)}<span style="color:#555;font-size:12px"> min/600</span> &nbsp;{wk_badge(talk,600)}</div></div>
              <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Appts</div>
                <div style="color:#fff;font-size:18px;font-weight:bold">{int(appts)}</div></div>
              <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Offers</div>
                <div style="color:#fff;font-size:18px;font-weight:bold">{int(offers)}</div></div>
              <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Contracts</div>
                <div style="color:{kc};font-size:18px;font-weight:bold">{int(cons)}<span style="color:#555;font-size:12px">/3</span> &nbsp;{wk_badge(cons,3)}</div></div>
              <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">A→C %</div>
                <div style="color:#fff;font-size:18px;font-weight:bold">{acp}</div></div>
            </div>"""}
          </div>
          <div style="text-align:right">
            <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Commitments</div>
            <div style="color:{commit_col};font-size:16px;font-weight:bold">{commit_txt}</div>
            <div style="color:#555;font-size:11px">{logged_days} day{"s" if logged_days!=1 else ""} logged</div>
          </div>
        </div>
        </div>""", unsafe_allow_html=True)

    if not logged_rows:
        st.info(f"No numbers logged for {sel_wk_label}.")

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

    # ── PIN Management ──
    st.markdown("---")
    st.markdown('<div class="section-hdr">Rep PIN Management</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#888;font-size:12px;margin-bottom:12px">Set a 4-digit PIN for each rep. Reps will need their PIN to log daily numbers and submit commitments. Leave blank to remove PIN.</div>', unsafe_allow_html=True)
    if data["reps"]:
        for rep_name in data["reps"]:
            pc1,pc2,pc3=st.columns([3,2,1])
            with pc1:
                current_pin=data["pins"].get(rep_name,"")
                status="🔒 PIN set" if current_pin else "🔓 No PIN"
                st.markdown(f'<div style="padding:8px 0;color:#cdd6f4">{rep_name} &nbsp; <span style="color:#888;font-size:12px">{status}</span></div>', unsafe_allow_html=True)
            with pc2:
                new_pin=st.text_input(f"New PIN",max_chars=4,key=f"pin_{rep_name}",
                                      placeholder="4 digits",label_visibility="collapsed")
            with pc3:
                if st.button("Save",key=f"pin_save_{rep_name}",type="primary"):
                    if new_pin.strip():
                        if not new_pin.strip().isdigit() or len(new_pin.strip())!=4:
                            st.error("PIN must be exactly 4 digits.")
                        else:
                            data["pins"][rep_name]=new_pin.strip()
                            save_data(data); st.success(f"PIN set for {rep_name}!"); st.rerun()
                    else:
                        data["pins"].pop(rep_name,None)
                        save_data(data); st.success(f"PIN removed for {rep_name}."); st.rerun()
    else:
        st.info("Add reps above first.")

# ─── MONTH-END SUMMARY ────────────────────────────────────────────────────────
elif page=="Month-End Summary":
    import pandas as pd
    today_dt=datetime.now().date()
    month_start=today_dt.replace(day=1)
    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px">📋 Month-End Summary</div>
    <div style="color:#ffcccc;font-size:14px;margin-top:2px">{month_label(sel_month)} — Full team performance review</div>
    </div>""", unsafe_allow_html=True)
    if not data["reps"]: st.info("No reps yet."); st.stop()

    sel_ms=datetime.strptime(sel_month+"-01","%Y-%m-%d").date()
    sel_me=(sel_ms.replace(day=28)+timedelta(days=4)).replace(day=1)-timedelta(days=1)
    is_current = sel_month==month_key()
    eff_end = min(sel_me, today_dt) if is_current else sel_me

    for rep in data["reps"]:
        t=get_monthly(rep,sel_month,data)
        comp=get_standards_compliance(rep,data,sel_ms,eff_end)
        acct=get_accountability_score(rep,data,sel_ms,eff_end) if is_current else None
        streak=get_streak(rep,data)
        week_start3=today_dt-timedelta(days=today_dt.weekday())
        cs=get_commit_stats(rep,data,week_start3,sel_ms,eff_end)
        proj=get_pace_projection(rep,data,today_dt,month_start) if is_current else None

        acct_col="#a6e3a1" if (acct or 0)>=80 else "#f9e2af" if (acct or 0)>=60 else "#f38ba8"

        st.markdown(f"""<div style="background:#1a1a1a;border-radius:12px;padding:22px 24px;margin-bottom:18px;border-top:3px solid #cc0000">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:16px;margin-bottom:16px">
          <div>
            <div style="color:#ffffff;font-size:20px;font-weight:bold">{rep}</div>
            <div style="color:#888;font-size:12px;margin-top:2px">{month_label(sel_month)}</div>
          </div>
          <div style="display:flex;gap:20px;flex-wrap:wrap;text-align:center">
            {"" if acct is None else f'<div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Accountability</div><div style="color:{acct_col};font-size:28px;font-weight:bold">{acct}</div></div>'}
            <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Commit Hit Rate</div><div style="color:#{"22c55e" if cs["hit_rate"]>=80 else "f9e2af" if cs["hit_rate"]>=50 else "cc0000"};font-size:28px;font-weight:bold">{cs["hit_rate"]}%</div></div>
            <div><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Streak</div><div style="color:#f9e2af;font-size:28px;font-weight:bold">{"🔥 "+str(streak)+"d" if streak>0 else "—"}</div></div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px">
          <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
            <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Days Logged</div>
            <div style="color:{vcolor(comp["log_pct"],80)};font-size:22px;font-weight:bold">{comp["days_logged"]}/{comp["wd_elapsed"]}</div>
            <div style="color:#555;font-size:11px">{comp["log_pct"]}% logged</div>
          </div>
          <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
            <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Call Standard Hit</div>
            <div style="color:{vcolor(comp["calls_pct"],80)};font-size:22px;font-weight:bold">{comp["calls_hit"]}d</div>
            <div style="color:#555;font-size:11px">{comp["calls_pct"]}% of logged days</div>
          </div>
          <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
            <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Talk Standard Hit</div>
            <div style="color:{vcolor(comp["talk_pct"],80)};font-size:22px;font-weight:bold">{comp["talk_hit"]}d</div>
            <div style="color:#555;font-size:11px">{comp["talk_pct"]}% of logged days</div>
          </div>
          <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
            <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Both Standards</div>
            <div style="color:{vcolor(comp["both_pct"],80)};font-size:22px;font-weight:bold">{comp["both_hit"]}d</div>
            <div style="color:#555;font-size:11px">{comp["both_pct"]}% compliance</div>
          </div>
        </div>""", unsafe_allow_html=True)

        if t:
            mt3=get_daily_range_totals(rep,data,sel_ms,eff_end)
            calls3=mt3["calls"]; appts3=mt3["appointments"]; offs3=mt3["offers"]
            cons3=mt3["contracts"]; closed3=t["closed_deals"]
            rev3=t["revenue"]; spread3=t["spread"]
            st.markdown(f"""<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px">
            <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
              <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Total Calls</div>
              <div style="color:{vcolor(calls3,600)};font-size:22px;font-weight:bold">{int(calls3)}</div>
              <div style="color:#555;font-size:11px">Goal: 600</div>
            </div>
            <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
              <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Contracts</div>
              <div style="color:{vcolor(cons3,12)};font-size:22px;font-weight:bold">{int(cons3)}</div>
              <div style="color:#555;font-size:11px">Goal: 12</div>
            </div>
            <div style="background:#111;border-radius:8px;padding:12px;text-align:center">
              <div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px">Closed / Revenue</div>
              <div style="color:{vcolor(rev3,100000)};font-size:22px;font-weight:bold">{int(closed3)} / ${rev3:,.0f}</div>
              <div style="color:#555;font-size:11px">Goal: 6 / $100k</div>
            </div>
            </div>""", unsafe_allow_html=True)

            # Conversion funnel inline
            funnel_data=[(calls3,"Calls","#cc0000"),(appts3,"Appts","#f59e0b"),(offs3,"Offers","#60a5fa"),(cons3,"Contracts","#a6e3a1"),(closed3,"Closed","#22c55e")]
            fd_html='<div style="display:flex;gap:6px;align-items:flex-end;margin-bottom:6px">'
            for val,lbl,col in funnel_data:
                pct=round(val/calls3*100) if calls3>0 else 0
                h=max(pct,4)
                fd_html+=f'<div style="text-align:center;flex:1"><div style="color:{col};font-size:12px;font-weight:bold;margin-bottom:3px">{int(val)}</div><div style="background:{col};height:{h}px;border-radius:3px 3px 0 0;opacity:0.8"></div><div style="color:#555;font-size:10px;margin-top:3px">{lbl}</div></div>'
            fd_html+='</div>'
            st.markdown(f'<div style="background:#111;border-radius:8px;padding:14px;margin-bottom:14px"><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">Conversion Funnel</div>{fd_html}</div>', unsafe_allow_html=True)

        # Coaching notes for this rep
        notes=data["coaching_notes"].get(rep,[])
        open_items=[n for n in notes if n.get("follow_up") and not n.get("completed")]
        if open_items:
            items_html="".join([f'<div style="color:#f9e2af;font-size:12px;margin-top:5px">↳ {n["note"][:80]} <span style="color:#666">— Due {n["follow_up"]}</span></div>' for n in open_items[-3:]])
            st.markdown(f'<div style="background:#111;border-radius:8px;padding:12px;margin-bottom:14px"><div style="color:#888;font-size:10px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px">Open Action Items ({len(open_items)})</div>{items_html}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ─── HOW TO USE ───────────────────────────────────────────────────────────────
elif page=="How to Use":
    st.markdown("""<div style="background:linear-gradient(90deg,#0d0d0d,#1a0000,#0d0d0d);
    border:1px solid #cc0000;border-radius:12px;padding:28px 24px;margin-bottom:20px;text-align:center">
    <div style="margin-bottom:14px">
      <div style="background:#ffffff;border-radius:8px;padding:6px 18px;display:inline-block">
        <img src="https://raw.githubusercontent.com/mattheller9259/sales-dashboard/main/logo.png" style="height:42px;display:block">
      </div>
    </div>
    <div style="color:#ffffff;font-size:42px;font-weight:900;letter-spacing:3px;line-height:1">WIN THE DAY</div>
    <div style="color:#888;font-size:13px;margin-top:10px;letter-spacing:1px">Every call. Every minute. Every day.</div>
    <div style="margin-top:16px;border-top:1px solid rgba(204,0,0,0.25);padding-top:14px;display:flex;justify-content:center;gap:8px;flex-wrap:wrap">
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">⚡ Demand Enthusiasm</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">💪 Embrace Hard Work</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">📈 Insist on Growth</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">🤝 Live Honestly</span>
      <span style="background:rgba(204,0,0,0.15);border:1px solid rgba(204,0,0,0.4);color:#ffcccc;padding:5px 13px;border-radius:20px;font-size:11px;font-weight:bold;letter-spacing:0.5px">🏆 Celebrate Teamwork</span>
    </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="mco-header">
    <div style="color:#ffffff;font-size:22px;font-weight:bold;letter-spacing:1px">🏠 How to Use This Dashboard</div>
    <div style="color:#ffcccc;font-size:14px;margin-top:2px">Everything your team needs to know — bookmark this page</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#1a1a1a;border-radius:12px;padding:22px 26px;margin-bottom:16px;border-left:5px solid #22c55e">
    <div style="color:#22c55e;font-size:13px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">📋 FOR REPS — Morning Routine</div>
    <div style="color:#cdd6f4;font-size:14px;line-height:2">
    <b style="color:#ffffff">Step 1</b> &nbsp;→&nbsp; Open <b>mcosalesdashboard.streamlit.app</b><br>
    <b style="color:#ffffff">Step 2</b> &nbsp;→&nbsp; Click <b>Daily Commitments</b> in the left sidebar<br>
    <b style="color:#ffffff">Step 3</b> &nbsp;→&nbsp; Select your name and enter your PIN<br>
    <b style="color:#ffffff">Step 4</b> &nbsp;→&nbsp; Write your commitment for the day — what will you accomplish?<br>
    <b style="color:#ffffff">Step 5</b> &nbsp;→&nbsp; Hit <b>Submit Commitment</b><br>
    <b style="color:#ffffff">Step 6</b> &nbsp;→&nbsp; Check <b>Team Overview</b> to see where you rank on the leaderboard
    </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#1a1a1a;border-radius:12px;padding:22px 26px;margin-bottom:16px;border-left:5px solid #cc0000">
    <div style="color:#f38ba8;font-size:13px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">📊 FOR REPS — End of Day Routine</div>
    <div style="color:#cdd6f4;font-size:14px;line-height:2">
    <b style="color:#ffffff">Step 1</b> &nbsp;→&nbsp; Open <b>mcosalesdashboard.streamlit.app</b><br>
    <b style="color:#ffffff">Step 2</b> &nbsp;→&nbsp; Click <b>Daily Numbers</b> in the left sidebar<br>
    <b style="color:#ffffff">Step 3</b> &nbsp;→&nbsp; Click the <b>Log Today's Numbers</b> tab<br>
    <b style="color:#ffffff">Step 4</b> &nbsp;→&nbsp; Select your name and enter your PIN<br>
    <b style="color:#ffffff">Step 5</b> &nbsp;→&nbsp; Enter your numbers for the day:<br>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style="color:#888">• Calls Made &nbsp;·&nbsp; Talk Time (minutes) &nbsp;·&nbsp; Appointments Set &nbsp;·&nbsp; Offers Made &nbsp;·&nbsp; Contracts</span><br>
    <b style="color:#ffffff">Step 6</b> &nbsp;→&nbsp; Hit <b>Save Today's Numbers</b><br>
    <b style="color:#ffffff">Step 7</b> &nbsp;→&nbsp; Check the <b>Leaderboard</b> tab to see where you stand
    </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#1a1a1a;border-radius:12px;padding:22px 26px;margin-bottom:16px;border-left:5px solid #f9e2af">
    <div style="color:#f9e2af;font-size:13px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">👔 FOR MANAGERS — Daily & Weekly</div>
    <div style="color:#cdd6f4;font-size:14px;line-height:2">
    <b style="color:#ffffff">Every day</b> &nbsp;→&nbsp; Check <b>Team Overview</b> to monitor the leaderboard and commitment status<br>
    <b style="color:#ffffff">Every day</b> &nbsp;→&nbsp; Check <b>Daily Commitments → Review Yesterday</b> to mark commitments Hit ✅ or Missed ❌<br>
    <b style="color:#ffffff">Every Monday</b> &nbsp;→&nbsp; Open <b>Weekly Recap</b> for a full breakdown of last week's performance<br>
    <b style="color:#ffffff">Once a week</b> &nbsp;→&nbsp; Go to <b>Log Weekly Results</b> to enter closed deals, revenue &amp; spread<br>
    <b style="color:#ffffff">Anytime</b> &nbsp;→&nbsp; Use <b>Individual Rep</b> to see pacing, trends, and add coaching notes
    </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#1a1a1a;border-radius:12px;padding:22px 26px;margin-bottom:16px;border-left:5px solid #60a5fa">
    <div style="color:#60a5fa;font-size:13px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">📍 Page Guide — What Each Page Does</div>
    <div style="color:#cdd6f4;font-size:14px;line-height:2.2">
    <b style="color:#ffffff">Team Overview</b> &nbsp;·&nbsp; Competitive leaderboard for Today, This Week, and This Month. Shows who's #1, who's chasing, and who needs to step it up.<br>
    <b style="color:#ffffff">Daily Numbers</b> &nbsp;·&nbsp; Where reps log their end-of-day activity. Also shows today's leaderboard with calls, talk time, and contracts.<br>
    <b style="color:#ffffff">Daily Commitments</b> &nbsp;·&nbsp; Morning commitment submission. Manager reviews yesterday's commitments each day to mark Hit or Missed.<br>
    <b style="color:#ffffff">Individual Rep</b> &nbsp;·&nbsp; Deep dive on one rep — on-pace indicators, 6-week trends, monthly results, and coaching notes.<br>
    <b style="color:#ffffff">Weekly Recap</b> &nbsp;·&nbsp; Monday morning review. Every rep's full week at a glance — great for team meetings.<br>
    <b style="color:#ffffff">Log Weekly Results</b> &nbsp;·&nbsp; Manager only. Enter closed deals, revenue, and spread each week. Also where PINs are managed.
    </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""<div style="background:#1a0000;border:1px solid #cc0000;border-radius:12px;padding:18px 24px;margin-bottom:16px">
    <div style="color:#f38ba8;font-size:13px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px">⚠️ Important Notes</div>
    <div style="color:#cdd6f4;font-size:14px;line-height:2">
    • Your <b>PIN</b> is personal — do not share it with other reps<br>
    • Log your numbers <b>every day</b> — missing a day affects your weekly and monthly score<br>
    • The dashboard may take <b>30–60 seconds to load</b> if it hasn't been used recently — just wait, it will wake up<br>
    • Everyone with the link can see the full leaderboard — that's by design
    </div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div style="background:#1a1a1a;border-radius:12px;padding:18px 24px;text-align:center">
    <div style="color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">Bookmark This Link</div>
    <div style="color:#cc0000;font-size:20px;font-weight:bold">mcosalesdashboard.streamlit.app</div>
    <div style="color:#888;font-size:12px;margin-top:6px">Midwest Cash Offer — Sales Performance Dashboard</div>
    </div>""", unsafe_allow_html=True)
