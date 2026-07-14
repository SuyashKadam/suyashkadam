import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime
from collections import deque

st.set_page_config(
    page_title="Suyash AWS Architecture Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  .stApp { background: #0d1117; color: #e6edf3; }

  section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
  }
  section[data-testid="stSidebar"] * { color: #e6edf3 !important; }

  .metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 20px 24px;
    text-align: center;
  }
  .metric-value {
    font-size: 2.1rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
  }
  .metric-label {
    font-size: 0.72rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 6px;
  }
  .metric-delta {
    font-size: 0.78rem;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
  }
  .delta-up   { color: #f85149; }
  .delta-down { color: #3fb950; }
  .delta-ok   { color: #8b949e; }

  .section-header {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8b949e;
    border-bottom: 1px solid #21262d;
    padding-bottom: 8px;
    margin-bottom: 14px;
  }

  .alarm-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 14px;
    border-radius: 6px;
    margin-bottom: 5px;
    background: #161b22;
    border: 1px solid #21262d;
    font-size: 0.82rem;
  }
  .alarm-ok    { border-left: 3px solid #3fb950; }
  .alarm-warn  { border-left: 3px solid #d29922; }
  .alarm-alert { border-left: 3px solid #f85149; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .dot-ok    { background: #3fb950; }
  .dot-warn  { background: #d29922; }
  .dot-alert { background: #f85149; box-shadow: 0 0 6px #f85149; }

  .event-item {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    padding: 6px 12px;
    border-radius: 4px;
    background: #0d1117;
    border: 1px solid #21262d;
    margin-bottom: 4px;
    color: #8b949e;
  }
  .event-item .ts  { color: #58a6ff; }
  .event-scale-out .ts { color: #f85149; }
  .event-scale-in  .ts { color: #3fb950; }

  .traffic-label { font-size: 1.5rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
  .traffic-low    { color: #3fb950; }
  .traffic-medium { color: #58a6ff; }
  .traffic-high   { color: #d29922; }
  .traffic-spike  { color: #f85149; }

  .info-chip {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 14px 16px;
    text-align: center;
  }
  .chip-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em; color: #8b949e; margin-bottom: 6px; }
  .chip-value { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 600; color: #e6edf3; }
  .chip-sub   { font-size: 0.68rem; color: #8b949e; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────

MAX_POINTS = 90

def _init():
    defaults = {
        "hist_ts":       deque(maxlen=MAX_POINTS),
        "hist_rps":      deque(maxlen=MAX_POINTS),
        "hist_latency":  deque(maxlen=MAX_POINTS),
        "hist_cpu":      deque(maxlen=MAX_POINTS),
        "hist_tasks":    deque(maxlen=MAX_POINTS),
        "hist_errors":   deque(maxlen=MAX_POINTS),
        "hist_bytes":    deque(maxlen=MAX_POINTS),
        "events":        deque(maxlen=15),
        "task_count":    3,
        "traffic_level": 25,
        "last_tick":     time.time() - 999,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─── Traffic model ───────────────────────────────────────────────────────────

def generate(level: int):
    lvl = level / 100.0
    rps     = max(1,   round(10  + lvl * 990  + random.gauss(0, lvl * 40 + 1), 1))
    latency = max(8,   round(18  + lvl * 282  + random.gauss(0, lvl * 15 + 1), 1))
    cpu     = min(99, max(1, round(5 + lvl * 90 + random.gauss(0, 3), 1)))
    errors  = max(0,   round((lvl ** 2) * 5 + random.gauss(0, 0.2), 2))
    mbps    = max(0.05, round(0.1 + lvl * 49.9 + random.gauss(0, lvl * 2 + 0.05), 2))
    return rps, latency, cpu, errors, mbps

def maybe_scale(cpu: float):
    tc = st.session_state.task_count
    ts = datetime.now().strftime("%H:%M:%S")
    if cpu >= 80 and tc < 6:
        st.session_state.task_count = tc + 1
        st.session_state.events.appendleft(
            {"ts": ts, "type": "scale-out",
             "msg": f"Scale-out (CPU {cpu:.0f}%) — tasks {tc} -> {tc+1}"}
        )
    elif cpu < 40 and tc > 3:
        st.session_state.task_count = tc - 1
        st.session_state.events.appendleft(
            {"ts": ts, "type": "scale-in",
             "msg": f"Scale-in (CPU {cpu:.0f}%) — tasks {tc} -> {tc-1}"}
        )

def tick():
    rps, lat, cpu, err, mb = generate(st.session_state.traffic_level)
    maybe_scale(cpu)
    st.session_state.hist_ts.append(datetime.now())
    st.session_state.hist_rps.append(rps)
    st.session_state.hist_latency.append(lat)
    st.session_state.hist_cpu.append(cpu)
    st.session_state.hist_tasks.append(float(st.session_state.task_count))
    st.session_state.hist_errors.append(err)
    st.session_state.hist_bytes.append(mb)
    st.session_state.last_tick = time.time()

# ─── Chart helpers ───────────────────────────────────────────────────────────

BG   = "#0d1117"
GRID = "#21262d"
MUTED = "#8b949e"
FONT = "JetBrains Mono, monospace"

def _base(height):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=MUTED, family=FONT, size=9),
        height=height,
        margin=dict(l=44, r=10, t=10, b=28),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=8), color=MUTED),
        yaxis=dict(gridcolor=GRID, zeroline=False, tickfont=dict(size=8), color=MUTED),
        showlegend=False,
    )

def area(xs, ys, color, alpha, height=210, threshold=None, ysuffix=""):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(xs), y=list(ys), mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=f"rgba({_hex_rgb(color)},{alpha})",
    ))
    if threshold:
        fig.add_hline(y=threshold, line=dict(color="#f85149", width=1, dash="dot"),
                      annotation_text=f"  {threshold}", annotation_font_size=8,
                      annotation_font_color="#f85149")
    lay = _base(height)
    if ysuffix:
        lay["yaxis"]["ticksuffix"] = ysuffix
    fig.update_layout(**lay)
    return fig

def _hex_rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))

def dual(xs, y1, y2, c1, c2, l1, l2, height=230, threshold=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=list(xs), y=list(y1), mode="lines",
                             line=dict(color=c1, width=2), name=l1), secondary_y=False)
    fig.add_trace(go.Scatter(x=list(xs), y=list(y2), mode="lines",
                             line=dict(color=c2, width=2, dash="dot"), name=l2), secondary_y=True)
    if threshold:
        fig.add_hline(y=threshold, line=dict(color="#f85149", width=1, dash="dot"),
                      annotation_text="  80%", annotation_font_size=8,
                      annotation_font_color="#f85149")
    lay = _base(height)
    lay["showlegend"] = True
    lay["legend"] = dict(orientation="h", x=1, y=1.18, xanchor="right",
                         font=dict(size=8), bgcolor="rgba(0,0,0,0)")
    fig.update_layout(**lay)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(size=8),
                     color=MUTED, secondary_y=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", zeroline=False, tickfont=dict(size=8),
                     color=c2, secondary_y=True)
    return fig

# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## Traffic Control")
    st.markdown("---")

    level = st.slider("Traffic Level", 0, 100,
                      value=st.session_state.traffic_level, step=1, format="%d%%")
    st.session_state.traffic_level = level

    if   level <= 25: label, cls = "LOW",    "traffic-low"
    elif level <= 55: label, cls = "MEDIUM", "traffic-medium"
    elif level <= 80: label, cls = "HIGH",   "traffic-high"
    else:             label, cls = "SPIKE",  "traffic-spike"

    st.markdown(
        f'<div style="text-align:center;margin:12px 0 4px">'
        f'<div class="traffic-label {cls}">{label}</div>'
        f'<div style="color:#8b949e;font-size:0.73rem">{level}% load</div>'
        f'</div>', unsafe_allow_html=True
    )

    st.markdown("---")
    refresh_sec = int(st.selectbox("Refresh rate", ["2s", "5s", "10s", "30s"], index=0).rstrip("s"))

    st.markdown("---")
    st.markdown("""<div style="font-size:0.71rem;color:#8b949e;line-height:1.7">
    <b style="color:#e6edf3">Scaling rules</b><br>
    CPU &ge; 80% &rarr; scale-out (max 6 tasks)<br>
    CPU &lt; 40% &rarr; scale-in (min 3 tasks)<br><br>
    <b style="color:#e6edf3">Tip</b><br>
    Drag the slider to 85%+ to watch auto-scaling fire.
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("Reset history", use_container_width=True):
        for k in ["hist_ts","hist_rps","hist_latency","hist_cpu",
                  "hist_tasks","hist_errors","hist_bytes","events"]:
            st.session_state[k].clear()
        st.session_state.task_count = 3
        st.rerun()

# ─── Tick ────────────────────────────────────────────────────────────────────

if time.time() - st.session_state.last_tick >= refresh_sec:
    tick()

# Warm-up: ensure at least 12 points before rendering
while len(st.session_state.hist_ts) < 12:
    tick()

# Aliases
ts  = st.session_state.hist_ts
rps = st.session_state.hist_rps
lat = st.session_state.hist_latency
cpu = st.session_state.hist_cpu
tsk = st.session_state.hist_tasks
err = st.session_state.hist_errors
mb  = st.session_state.hist_bytes

cur_rps  = rps[-1];  prev_rps  = rps[-2]  if len(rps)  > 1 else rps[-1]
cur_lat  = lat[-1];  prev_lat  = lat[-2]  if len(lat)  > 1 else lat[-1]
cur_cpu  = cpu[-1];  prev_cpu  = cpu[-2]  if len(cpu)  > 1 else cpu[-1]
cur_tsk  = int(tsk[-1])
cur_err  = err[-1]
cur_mb   = mb[-1]

# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown(
    '<div style="font-size:0.7rem;color:#8b949e;text-transform:uppercase;'
    'letter-spacing:0.1em;margin-bottom:4px">Suyash Kadam · AWS Architecture</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div style="font-size:1.4rem;font-weight:700;color:#e6edf3;margin-bottom:2px">'
    'Live Traffic Dashboard</div>', unsafe_allow_html=True
)
st.markdown(
    f'<div style="font-size:0.75rem;color:#8b949e;margin-bottom:18px">'
    f'ECS Fargate &nbsp;·&nbsp; CloudFront &nbsp;·&nbsp; ALB &nbsp;·&nbsp; Auto-Scaling'
    f'&nbsp;&nbsp;|&nbsp;&nbsp;Last tick: {datetime.now().strftime("%H:%M:%S")}'
    f'</div>', unsafe_allow_html=True
)

# ─── KPI cards ───────────────────────────────────────────────────────────────

def delta(cur, prev, unit="", invert=False):
    d = cur - prev
    if abs(d) < 0.05:
        return '<div class="metric-delta delta-ok">stable</div>'
    sign = "+" if d > 0 else ""
    if invert:
        cls = "delta-down" if d > 0 else "delta-up"
    else:
        cls = "delta-up" if d > 0 else "delta-down"
    return f'<div class="metric-delta {cls}">{sign}{d:.1f}{unit}</div>'

cpu_color = "#f85149" if cur_cpu >= 80 else ("#d29922" if cur_cpu >= 60 else "#58a6ff")
tsk_color = "#f85149" if cur_tsk == 6 else ("#d29922" if cur_tsk > 3 else "#3fb950")
err_color = "#f85149" if cur_err >= 1 else "#3fb950"

k1, k2, k3, k4, k5, k6 = st.columns(6)

def kpi(col, label, value, d_html, color="#e6edf3"):
    col.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-value" style="color:{color}">{value}</div>'
        f'<div class="metric-label">{label}</div>'
        f'{d_html}</div>', unsafe_allow_html=True
    )

kpi(k1, "Requests / sec",   f"{cur_rps:,.0f}",   delta(cur_rps, prev_rps, " rps"))
kpi(k2, "P99 Latency",      f"{cur_lat:.0f} ms",  delta(cur_lat, prev_lat, " ms", invert=True))
kpi(k3, "CPU Utilization",  f"{cur_cpu:.0f}%",    delta(cur_cpu, prev_cpu, "%", invert=True), color=cpu_color)
kpi(k4, "Active ECS Tasks", str(cur_tsk),
    '<div class="metric-delta delta-ok">min 3 / max 6</div>', color=tsk_color)
kpi(k5, "Error Rate",       f"{cur_err:.2f}%",
    '<div class="metric-delta delta-ok">5xx / total</div>', color=err_color)
kpi(k6, "Throughput",       f"{cur_mb:.1f} MB/s",
    '<div class="metric-delta delta-ok">via CloudFront</div>')

st.markdown("<br>", unsafe_allow_html=True)

# ─── Charts row 1 ────────────────────────────────────────────────────────────

c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="section-header">Requests per Second</div>', unsafe_allow_html=True)
    st.plotly_chart(area(ts, rps, "#58a6ff", 0.12, ysuffix=" rps"),
                    use_container_width=True, config={"displayModeBar": False})

with c2:
    st.markdown('<div class="section-header">P99 Latency (ms)</div>', unsafe_allow_html=True)
    st.plotly_chart(area(ts, lat, "#d29922", 0.12, threshold=200, ysuffix=" ms"),
                    use_container_width=True, config={"displayModeBar": False})

# ─── Charts row 2 ────────────────────────────────────────────────────────────

c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="section-header">CPU % vs ECS Task Count</div>', unsafe_allow_html=True)
    st.plotly_chart(dual(ts, cpu, tsk, "#f85149", "#3fb950", "CPU %", "Tasks",
                         threshold=80),
                    use_container_width=True, config={"displayModeBar": False})

with c4:
    st.markdown('<div class="section-header">Throughput (MB/s) vs Error Rate (%)</div>', unsafe_allow_html=True)
    st.plotly_chart(dual(ts, mb, err, "#58a6ff", "#f85149", "MB/s", "Err %"),
                    use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)

# ─── Alarms + Events ─────────────────────────────────────────────────────────

a_col, e_col = st.columns(2)

with a_col:
    st.markdown('<div class="section-header">CloudWatch Alarms</div>', unsafe_allow_html=True)

    def alarm(name, in_alarm, near_alarm, value, unit=""):
        if in_alarm:
            cls, dot, state = "alarm-alert", "dot-alert", "ALARM"
        elif near_alarm:
            cls, dot, state = "alarm-warn", "dot-warn",  "WARNING"
        else:
            cls, dot, state = "alarm-ok",   "dot-ok",    "OK"
        st.markdown(
            f'<div class="alarm-row {cls}">'
            f'<div class="dot {dot}"></div>'
            f'<div style="flex:1">{name}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.78rem">'
            f'{value}{unit}</div>'
            f'<div style="font-size:0.68rem;color:#8b949e;width:58px;text-align:right">{state}</div>'
            f'</div>', unsafe_allow_html=True
        )

    alarm("CPU Utilization",    cur_cpu >= 80,  cur_cpu >= 60,  f"{cur_cpu:.0f}", "%")
    alarm("P99 Latency",        cur_lat >= 300, cur_lat >= 200, f"{cur_lat:.0f}", " ms")
    alarm("5xx Error Rate",     cur_err >= 1,   cur_err >= 0.5, f"{cur_err:.2f}", "%")
    alarm("Unhealthy Hosts",    cur_tsk < 3,    False,          str(cur_tsk), " tasks")
    alarm("Low Throughput",     cur_mb < 0.5 and level > 20,
                                cur_mb < 1.0 and level > 20,    f"{cur_mb:.1f}", " MB/s")

with e_col:
    st.markdown('<div class="section-header">Auto-Scaling Events</div>', unsafe_allow_html=True)
    events = list(st.session_state.events)
    if not events:
        st.markdown(
            '<div class="event-item">No scaling events yet — '
            'raise traffic to 85%+ to trigger scale-out.</div>',
            unsafe_allow_html=True
        )
    for ev in events:
        cls = "event-scale-out" if ev["type"] == "scale-out" else "event-scale-in"
        st.markdown(
            f'<div class="event-item {cls}">'
            f'<span class="ts">[{ev["ts"]}]</span> {ev["msg"]}'
            f'</div>', unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─── Infrastructure chips ────────────────────────────────────────────────────

st.markdown('<div class="section-header">Infrastructure</div>', unsafe_allow_html=True)

i1, i2, i3, i4, i5 = st.columns(5)

def chip(col, label, value, sub=""):
    col.markdown(
        f'<div class="info-chip">'
        f'<div class="chip-label">{label}</div>'
        f'<div class="chip-value">{value}</div>'
        f'{"<div class=chip-sub>" + sub + "</div>" if sub else ""}'
        f'</div>', unsafe_allow_html=True
    )

chip(i1, "Pipeline",   "4 Stages",         "Source Build Approve Deploy")
chip(i2, "ECS Tasks",  f"{cur_tsk} / 6",   "min 3, auto-scale")
chip(i3, "Network",    "Private VPC",       "NAT Gateway egress")
chip(i4, "CDN / WAF",  "CloudFront",        "OWASP + rate limit")
chip(i5, "Alerting",   "SNS Email",         "5 CloudWatch alarms")

# ─── Auto-refresh ────────────────────────────────────────────────────────────

time.sleep(refresh_sec)
st.rerun()
