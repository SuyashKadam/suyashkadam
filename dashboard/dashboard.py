import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Suyash Kadam — AWS Architecture Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif;
  }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #21262d;
  }
  [data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
  }

  /* Main background */
  .stApp { background-color: #0a0d12; }

  /* Page header */
  .page-header {
    padding: 12px 0 28px 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 28px;
  }
  .page-header h1 {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #f0f6fc;
    margin: 0;
    letter-spacing: -0.02em;
  }
  .page-header p {
    font-size: 0.85rem;
    color: #8b949e;
    margin: 4px 0 0 0;
  }

  /* Metric cards */
  .metric-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 20px 24px;
  }
  .metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
    margin-bottom: 8px;
  }
  .metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 500;
    color: #58a6ff;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  .metric-sub {
    font-size: 0.75rem;
    color: #8b949e;
    margin-top: 6px;
  }

  /* Status pill */
  .pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .pill-green  { background: rgba(34,197,94,.12);  color: #22c55e; border: 1px solid rgba(34,197,94,.3); }
  .pill-blue   { background: rgba(88,166,255,.12); color: #58a6ff; border: 1px solid rgba(88,166,255,.3); }
  .pill-amber  { background: rgba(245,158,11,.12); color: #f59e0b; border: 1px solid rgba(245,158,11,.3); }
  .pill-red    { background: rgba(248,81,73,.12);  color: #f85149; border: 1px solid rgba(248,81,73,.3); }
  .pill-gray   { background: rgba(139,148,158,.1); color: #8b949e; border: 1px solid rgba(139,148,158,.2); }

  /* Section card */
  .section-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 16px;
  }
  .section-title {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #58a6ff;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #21262d;
  }

  /* Flow step */
  .flow-step {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px 20px;
    flex: 1;
  }
  .flow-step-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #8b949e;
    margin-bottom: 6px;
  }
  .flow-step-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #f0f6fc;
  }
  .flow-step-desc {
    font-size: 0.78rem;
    color: #8b949e;
    margin-top: 4px;
    line-height: 1.5;
  }
  .flow-arrow {
    color: #30363d;
    font-size: 1.2rem;
    align-self: center;
    padding: 0 4px;
  }

  /* Code block */
  .code-block {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #c9d1d9;
    line-height: 1.7;
    overflow-x: auto;
  }
  .code-comment { color: #8b949e; }
  .code-key     { color: #79c0ff; }
  .code-val     { color: #a5d6ff; }
  .code-str     { color: #a5d6ff; }
  .code-green   { color: #56d364; }

  /* Resource table row */
  .res-row {
    display: flex;
    align-items: center;
    padding: 11px 0;
    border-bottom: 1px solid #21262d;
    gap: 12px;
  }
  .res-row:last-child { border-bottom: none; }
  .res-icon {
    width: 32px; height: 32px;
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #58a6ff;
    font-weight: 700;
    flex-shrink: 0;
    text-align: center;
    line-height: 1.1;
  }
  .res-name  { font-size: 0.88rem; font-weight: 500; color: #f0f6fc; flex: 1; }
  .res-desc  { font-size: 0.78rem; color: #8b949e; }
  .res-right { text-align: right; flex-shrink: 0; }

  /* Alarm row */
  .alarm-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    align-items: center;
    padding: 11px 0;
    border-bottom: 1px solid #21262d;
    gap: 12px;
    font-size: 0.82rem;
  }
  .alarm-row:last-child { border-bottom: none; }
  .alarm-header {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #8b949e;
  }

  /* Divider */
  .divider { border: none; border-top: 1px solid #21262d; margin: 24px 0; }

  /* Mono text */
  .mono {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: #a5d6ff;
  }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 24px 0; border-bottom:1px solid #21262d; margin-bottom:20px;">
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.7rem; color:#8b949e;
                  text-transform:uppercase; letter-spacing:0.1em; margin-bottom:6px;">
        Project
      </div>
      <div style="font-size:1rem; font-weight:600; color:#f0f6fc; line-height:1.3;">
        Suyash Kadam<br>AWS Architecture
      </div>
      <div style="margin-top:10px;">
        <span class="pill pill-green">Live</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        [
            "Overview",
            "CI/CD Pipeline",
            "Infrastructure",
            "Auto-Scaling",
            "Monitoring & Alerts",
            "Buildspec Walkthrough",
        ],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div style="margin-top:32px; padding-top:20px; border-top:1px solid #21262d;">
      <div style="font-size:0.7rem; color:#8b949e; line-height:1.7;">
        <div style="margin-bottom:4px;"><span style="color:#58a6ff;">Region</span> us-east-1</div>
        <div style="margin-bottom:4px;"><span style="color:#58a6ff;">Cluster</span> suyashkadam-prod</div>
        <div><span style="color:#58a6ff;">Branch</span> master</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Helper ─────────────────────────────────────────────────────────────────────
def header(title, subtitle=""):
    st.markdown(f"""
    <div class="page-header">
      <h1>{title}</h1>
      {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)

def metric(label, value, sub=""):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      {"<div class='metric-sub'>" + sub + "</div>" if sub else ""}
    </div>"""

def section(title, content):
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">{title}</div>
      {content}
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "Overview":
    header(
        "AWS Architecture Overview",
        "End-to-end containerised web application on AWS — deployed, scaled, and monitored via Terraform IaC"
    )

    # Top metrics
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, lbl, val, sub in [
        (c1, "AWS Resources", "47", "created by Terraform"),
        (c2, "ECS Containers", "3 - 6", "min / max Fargate tasks"),
        (c3, "Pipeline Stages", "4", "Source, Build, Approve, Deploy"),
        (c4, "Scale Threshold", "80%", "CPU and Memory utilization"),
        (c5, "Availability Zones", "3", "us-east-1a / 1b / 1c"),
    ]:
        col.markdown(metric(lbl, val, sub), unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # Architecture flow
    section("Architecture Flow", """
    <div style="display:flex; gap:8px; align-items:stretch; flex-wrap:wrap;">

      <div class="flow-step">
        <div class="flow-step-label">Users</div>
        <div class="flow-step-title">Internet</div>
        <div class="flow-step-desc">Any browser, any location</div>
      </div>
      <div class="flow-arrow">--&gt;</div>

      <div class="flow-step" style="border-color:#f85149;">
        <div class="flow-step-label">Security</div>
        <div class="flow-step-title">AWS WAF</div>
        <div class="flow-step-desc">OWASP, SQLi, rate limit 2000/5min</div>
      </div>
      <div class="flow-arrow">--&gt;</div>

      <div class="flow-step" style="border-color:#58a6ff;">
        <div class="flow-step-label">CDN</div>
        <div class="flow-step-title">CloudFront</div>
        <div class="flow-step-desc">Global edge, HTTPS enforced</div>
      </div>
      <div class="flow-arrow">--&gt;</div>

      <div class="flow-step" style="border-color:#f59e0b;">
        <div class="flow-step-label">Load Balancer</div>
        <div class="flow-step-title">ALB (Multi-AZ)</div>
        <div class="flow-step-desc">Public subnets, /health checks</div>
      </div>
      <div class="flow-arrow">--&gt;</div>

      <div class="flow-step" style="border-color:#22c55e;">
        <div class="flow-step-label">Compute</div>
        <div class="flow-step-title">ECS Fargate</div>
        <div class="flow-step-desc">Private subnets, Nginx containers</div>
      </div>
      <div class="flow-arrow">--&gt;</div>

      <div class="flow-step">
        <div class="flow-step-label">Egress</div>
        <div class="flow-step-title">NAT Gateway</div>
        <div class="flow-step-desc">3x HA, one per AZ</div>
      </div>

    </div>
    """)

    col_l, col_r = st.columns(2)

    with col_l:
        section("Network Layout", """
        <div class="res-row">
          <div class="res-icon">VPC</div>
          <div>
            <div class="res-name">Virtual Private Cloud</div>
            <div class="res-desc">10.0.0.0/16 &mdash; isolated network boundary</div>
          </div>
          <div class="res-right"><span class="pill pill-blue">1 VPC</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">PUB</div>
          <div>
            <div class="res-name">Public Subnets</div>
            <div class="res-desc">10.0.1-3.0/24 &mdash; ALB and NAT Gateways</div>
          </div>
          <div class="res-right"><span class="pill pill-amber">3 subnets</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">PVT</div>
          <div>
            <div class="res-name">Private Subnets</div>
            <div class="res-desc">10.0.11-13.0/24 &mdash; ECS tasks only</div>
          </div>
          <div class="res-right"><span class="pill pill-green">3 subnets</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">NAT</div>
          <div>
            <div class="res-name">NAT Gateways</div>
            <div class="res-desc">One per AZ for high-availability egress</div>
          </div>
          <div class="res-right"><span class="pill pill-amber">3 gateways</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">IGW</div>
          <div>
            <div class="res-name">Internet Gateway</div>
            <div class="res-desc">Public subnet inbound/outbound</div>
          </div>
          <div class="res-right"><span class="pill pill-blue">1 IGW</span></div>
        </div>
        """)

    with col_r:
        section("Security Controls", """
        <div class="res-row">
          <div class="res-icon">WAF</div>
          <div>
            <div class="res-name">AWS WAF WebACL</div>
            <div class="res-desc">Attached to CloudFront &mdash; CLOUDFRONT scope</div>
          </div>
          <div class="res-right"><span class="pill pill-red">Active</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">CRS</div>
          <div>
            <div class="res-name">Core Rule Set</div>
            <div class="res-desc">AWSManagedRulesCommonRuleSet &mdash; OWASP Top 10</div>
          </div>
          <div class="res-right"><span class="pill pill-red">On</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">SQL</div>
          <div>
            <div class="res-name">SQL Injection Rules</div>
            <div class="res-desc">AWSManagedRulesSQLiRuleSet</div>
          </div>
          <div class="res-right"><span class="pill pill-red">On</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">RTE</div>
          <div>
            <div class="res-name">Rate Limiting</div>
            <div class="res-desc">2000 requests per 5 minutes per IP, then block</div>
          </div>
          <div class="res-right"><span class="pill pill-amber">2000/5m</span></div>
        </div>
        <div class="res-row">
          <div class="res-icon">SG</div>
          <div>
            <div class="res-name">Security Groups</div>
            <div class="res-desc">ALB: 0.0.0.0/0:80 &mdash; ECS: ALB-only ingress</div>
          </div>
          <div class="res-right"><span class="pill pill-blue">2 SGs</span></div>
        </div>
        """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CI/CD PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "CI/CD Pipeline":
    header(
        "CI/CD Pipeline",
        "AWS CodePipeline — four-stage automated delivery with mandatory manual approval before production deploy"
    )

    # Stage cards
    stages = [
        ("Source", "#58a6ff", "GitHub (CodeStar Connection)",
         ["Webhook fires on push to master", "Source artifact downloaded as ZIP", "Passed to Build stage as input"]),
        ("Build", "#a371f7", "AWS CodeBuild",
         ["ECR login (private + public)", "docker build ./app (Ubuntu 22.04 + Nginx)", "Image tagged with git commit SHA", "Pushed to ECR as :SHA and :latest", "imagedefinitions.json written as artifact"]),
        ("Approve", "#f59e0b", "Manual Approval",
         ["Pipeline pauses, no deploy yet", "SNS notification sent to email", "Reviewer checks CodeBuild logs", "Approve or Reject in AWS Console", "Rejection rolls pipeline back"]),
        ("Deploy", "#22c55e", "Amazon ECS (Rolling)",
         ["imagedefinitions.json consumed", "New task definition registered", "ECS rolling update: max 200%, min 100%", "ALB health checks gate traffic cutover", "Old tasks drained after new tasks healthy"]),
    ]

    cols = st.columns(4)
    for col, (name, color, provider, steps) in zip(cols, stages):
        steps_html = "".join(
            f'<div style="padding:4px 0; border-bottom:1px solid #21262d; font-size:0.76rem; color:#c9d1d9;">{s}</div>'
            for s in steps
        )
        col.markdown(f"""
        <div class="section-card" style="border-top:3px solid {color}; padding:20px;">
          <div style="font-size:0.68rem; font-weight:700; text-transform:uppercase;
                      letter-spacing:0.1em; color:{color}; margin-bottom:6px;">Stage</div>
          <div style="font-size:1.05rem; font-weight:600; color:#f0f6fc; margin-bottom:4px;">{name}</div>
          <div style="font-size:0.75rem; color:#8b949e; margin-bottom:14px;">{provider}</div>
          <div>{steps_html}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Pipeline flow chart
    fig = go.Figure()
    stage_labels = ["Source\n(GitHub)", "Build\n(CodeBuild)", "Approve\n(Manual)", "Deploy\n(ECS)"]
    colors_bg = ["#161b22", "#161b22", "#161b22", "#161b22"]
    colors_border = ["#58a6ff", "#a371f7", "#f59e0b", "#22c55e"]
    x_positions = [0.1, 0.35, 0.65, 0.9]

    for i, (lbl, xp, bc) in enumerate(zip(stage_labels, x_positions, colors_border)):
        fig.add_shape(type="rect", x0=xp-0.09, x1=xp+0.09, y0=0.3, y1=0.7,
                      fillcolor="#161b22", line=dict(color=bc, width=2),
                      xref="paper", yref="paper")
        fig.add_annotation(x=xp, y=0.5, text=lbl, showarrow=False,
                           font=dict(color="#f0f6fc", size=11, family="Inter"),
                           xref="paper", yref="paper", align="center")
        if i < 3:
            fig.add_annotation(
                x=xp + 0.135, y=0.5,
                ax=xp + 0.09, ay=0.5,
                xref="paper", yref="paper",
                axref="paper", ayref="paper",
                showarrow=True, arrowhead=2,
                arrowcolor="#30363d", arrowwidth=2,
                text="",
            )

    fig.update_layout(
        height=160, margin=dict(l=0, r=0, t=8, b=8),
        paper_bgcolor="#0a0d12", plot_bgcolor="#0a0d12",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    col_l, col_r = st.columns(2)
    with col_l:
        section("Deployment Strategy", """
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Type</div><div class="res-desc">ECS Rolling Update</div></div>
          <div><span class="pill pill-blue">Rolling</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Maximum Percent</div><div class="res-desc">Double capacity during deploy</div></div>
          <div class="mono">200%</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Minimum Healthy Percent</div><div class="res-desc">No reduction in live capacity</div></div>
          <div class="mono">100%</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Circuit Breaker</div><div class="res-desc">Auto-rollback on health failure</div></div>
          <div><span class="pill pill-green">Enabled</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Health Check Grace Period</div><div class="res-desc">Allow container startup time</div></div>
          <div class="mono">60s</div>
        </div>
        """)

    with col_r:
        section("Artifact Flow", """
        <div class="res-row">
          <div style="flex:1"><div class="res-name">source_output</div><div class="res-desc">GitHub ZIP handed to CodeBuild</div></div>
          <div><span class="pill pill-blue">ZIP</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">build_output</div><div class="res-desc">Contains imagedefinitions.json</div></div>
          <div><span class="pill pill-amber">JSON</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">imagedefinitions.json</div><div class="res-desc">Tells ECS which image to deploy</div></div>
          <div><span class="pill pill-green">Consumed</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Artifact Store</div><div class="res-desc">S3 bucket, versioned, 30-day expiry</div></div>
          <div><span class="pill pill-gray">S3</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Image Tags</div><div class="res-desc">:latest and :git-commit-sha</div></div>
          <div class="mono">dual tag</div>
        </div>
        """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: INFRASTRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Infrastructure":
    header(
        "Infrastructure Inventory",
        "47 AWS resources provisioned by Terraform across 7 modules — all tagged Project=suyashkadam, ManagedBy=Terraform"
    )

    resources = [
        ("VPC",          "vpc",          "10.0.0.0/16 — DNS hostnames enabled",             "Active",  "pill-green"),
        ("Internet GW",  "igw",          "Attached to VPC — public subnet egress",           "Active",  "pill-green"),
        ("Public Subnet","subnet",       "x3 — 10.0.1-3.0/24, us-east-1a/b/c",              "Active",  "pill-green"),
        ("Private Subnet","subnet",      "x3 — 10.0.11-13.0/24, ECS tasks only",             "Active",  "pill-green"),
        ("NAT Gateway",  "nat",          "x3 — one per AZ, Elastic IP attached",             "Active",  "pill-green"),
        ("Elastic IP",   "eip",          "x3 — fixed outbound IPs for NAT Gateways",         "Active",  "pill-blue"),
        ("Route Table",  "rt",           "Public: 0.0.0.0/0 -> IGW / Private: -> NAT each AZ","Active","pill-blue"),
        ("VPC Flow Logs","logs",         "ALL traffic — CloudWatch 30-day retention",         "Active",  "pill-green"),
        ("ALB",          "alb",          "Internet-facing, HTTP:80, multi-AZ, access logs S3","Active",  "pill-green"),
        ("Target Group", "tg",           "IP mode, /health, threshold 2 healthy / 3 unhealthy","Active", "pill-green"),
        ("ALB Listener", "http",         "Port 80 -> forward to target group",               "Active",  "pill-blue"),
        ("ALB SG",       "sg",           "Inbound 0.0.0.0/0:80 and :443, outbound all",      "Active",  "pill-green"),
        ("ECS Cluster",  "ecs",          "Container Insights enabled",                        "Active",  "pill-green"),
        ("ECS Service",  "svc",          "FARGATE, 3 desired, private subnets",              "Active",  "pill-green"),
        ("Task Def",     "task",         "nginx-app, 256 CPU / 512 MiB, awslogs",            "Active",  "pill-blue"),
        ("ECS SG",       "sg",           "Inbound from ALB SG only on :80",                 "Active",  "pill-green"),
        ("App Auto Scale","asg",         "CPU 80% and Memory 80% target tracking",           "Active",  "pill-green"),
        ("ECR Repo",     "ecr",          "Scan on push, AES256 encryption, lifecycle policy", "Active", "pill-green"),
        ("CloudFront",   "cf",           "PriceClass_100, HTTPS only, origin: ALB:80",       "Active",  "pill-green"),
        ("WAF WebACL",   "waf",          "CLOUDFRONT scope — 4 rule groups",                 "Active",  "pill-red"),
        ("CodeBuild",    "cb",           "LINUX_CONTAINER, privileged mode, CODEPIPELINE src","Active", "pill-green"),
        ("CodePipeline", "pipe",         "4 stages, GitHub v2 via CodeStar Connection",      "Active",  "pill-green"),
        ("CodeStar Conn","csc",          "GitHub OAuth — must be authorized in console",     "Active",  "pill-amber"),
        ("SNS Topic",    "sns",          "suyashkadam-prod-alerts — email subscription",     "Active",  "pill-green"),
        ("CW Dashboard", "cwd",          "6 widgets — CPU, Memory, Requests, Latency, Tasks","Active",  "pill-blue"),
        ("CW Alarm x5",  "alarm",        "CPU, Memory, 5xx, Latency, Unhealthy hosts",       "Active",  "pill-amber"),
        ("S3 (ALB logs)","s3",           "ALB access logs, 30-day lifecycle",                "Active",  "pill-gray"),
        ("S3 (CF logs)", "s3",           "CloudFront logs, 30-day lifecycle",                "Active",  "pill-gray"),
        ("S3 (pipeline)","s3",           "CodePipeline artifacts, versioned, 30-day expiry", "Active",  "pill-gray"),
        ("IAM Roles x4", "iam",          "ECS execution, task, CodeBuild, CodePipeline",     "Active",  "pill-blue"),
    ]

    # Module filter
    modules = ["All Modules", "vpc", "alb", "ecs", "ecr", "cloudfront", "monitoring", "codebuild", "codepipeline"]
    selected = st.selectbox("Filter by Terraform module", modules, label_visibility="collapsed")

    rows_html = ""
    for name, abbr, desc, status, pill in resources:
        rows_html += f"""
        <div class="res-row">
          <div class="res-icon">{abbr.upper()}</div>
          <div style="flex:1">
            <div class="res-name">{name}</div>
            <div class="res-desc">{desc}</div>
          </div>
          <div class="res-right"><span class="pill {pill}">{status}</span></div>
        </div>"""

    section(f"Resources ({len(resources)} shown)", rows_html)

    # Terraform modules breakdown
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    module_data = {
        "Module": ["vpc", "alb", "ecs", "ecr", "cloudfront", "monitoring", "codebuild", "codepipeline"],
        "Resources": [8, 6, 7, 3, 8, 7, 5, 6],
        "Description": [
            "VPC, subnets, NAT Gateways, route tables, flow logs",
            "ALB, target group, listener, SG, S3 access logs",
            "Cluster, service, task def, SG, auto-scaling, IAM",
            "Repository, scan policy, lifecycle policy",
            "Distribution, WAF WebACL, 4 WAF rules, CF logs S3",
            "SNS topic, email sub, dashboard, 5 CW alarms",
            "CodeBuild project, IAM role, policy, S3, log group",
            "Pipeline, CodeStar connection, IAM role, S3, EventBridge",
        ]
    }
    df = pd.DataFrame(module_data)
    fig = px.bar(
        df, x="Module", y="Resources",
        color="Resources",
        color_continuous_scale=[[0, "#21262d"], [1, "#58a6ff"]],
        text="Resources",
    )
    fig.update_traces(textposition="outside", textfont=dict(color="#8b949e", size=11))
    fig.update_layout(
        height=260,
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#8b949e", family="Inter"),
        margin=dict(l=0, r=0, t=12, b=0),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis=dict(showgrid=False, color="#8b949e", tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor="#21262d", color="#8b949e", zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: AUTO-SCALING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Auto-Scaling":
    header(
        "Auto-Scaling Configuration",
        "ECS Application Auto Scaling with target-tracking policies on CPU and Memory — min 3, max 6 Fargate tasks"
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val, sub in [
        (c1, "Minimum Tasks", "3",   "always running, 1 per AZ"),
        (c2, "Maximum Tasks", "6",   "upper bound for scale-out"),
        (c3, "Scale-Out Threshold", "80%", "CPU or Memory"),
        (c4, "Scale-Out Cooldown", "60s", "fast response to load"),
    ]:
        col.markdown(metric(lbl, val, sub), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Simulated scaling scenario
    import numpy as np
    np.random.seed(42)
    minutes = list(range(0, 61))
    cpu = [18]*10 + [25, 35, 48, 62, 74, 82, 88, 85, 84, 83, 82, 80, 79, 75, 68, 58, 48, 38, 28, 22, 20] + [18]*30
    cpu = cpu[:61]
    tasks = [3]*10 + [3, 3, 3, 3, 3, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 3, 3, 3, 3] + [3]*30
    tasks = tasks[:61]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=minutes, y=cpu,
        name="CPU Utilization (%)",
        line=dict(color="#58a6ff", width=2),
        fill="tozeroy",
        fillcolor="rgba(88,166,255,0.06)",
    ))
    fig.add_hline(y=80, line=dict(color="#f59e0b", width=1.5, dash="dash"),
                  annotation_text="Scale threshold 80%",
                  annotation_font=dict(color="#f59e0b", size=11))
    fig.add_trace(go.Scatter(
        x=minutes, y=[t * 12 for t in tasks],
        name="Running Tasks (x12 scaled)",
        line=dict(color="#22c55e", width=2, dash="dot"),
        yaxis="y2",
    ))
    fig.update_layout(
        height=300,
        paper_bgcolor="#161b22", plot_bgcolor="#161b22",
        font=dict(color="#8b949e", family="Inter"),
        margin=dict(l=0, r=0, t=16, b=0),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(22,27,34,0.8)",
            bordercolor="#30363d", borderwidth=1,
            font=dict(size=11, color="#c9d1d9"),
        ),
        xaxis=dict(
            title="Minutes", showgrid=False,
            color="#8b949e", tickfont=dict(size=10),
        ),
        yaxis=dict(
            title="CPU %", showgrid=True,
            gridcolor="#21262d", color="#8b949e",
            range=[0, 105], zeroline=False,
        ),
        yaxis2=dict(
            title="Tasks", overlaying="y", side="right",
            showgrid=False, color="#22c55e",
            tickvals=[36, 48, 60, 72],
            ticktext=["3", "4", "5", "6"],
        ),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Simulated load spike — CPU crosses 80% at minute 15, task count scales from 3 to 5, scales back in after cooldown.")

    col_l, col_r = st.columns(2)
    with col_l:
        section("CPU Tracking Policy", """
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Policy Type</div></div>
          <div class="mono">TargetTrackingScaling</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Metric</div></div>
          <div class="mono">ECSServiceAverageCPUUtilization</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Target Value</div></div>
          <div class="mono">80.0</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Scale-Out Cooldown</div></div>
          <div class="mono">60 seconds</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Scale-In Cooldown</div></div>
          <div class="mono">300 seconds</div>
        </div>
        """)

    with col_r:
        section("Memory Tracking Policy", """
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Policy Type</div></div>
          <div class="mono">TargetTrackingScaling</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Metric</div></div>
          <div class="mono">ECSServiceAverageMemoryUtilization</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Target Value</div></div>
          <div class="mono">80.0</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Scale-Out Cooldown</div></div>
          <div class="mono">60 seconds</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Scale-In Cooldown</div></div>
          <div class="mono">300 seconds</div>
        </div>
        """)

    section("Container Specification", """
    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
      <div>
        <div class="metric-label">CPU Units</div>
        <div class="mono" style="font-size:1.1rem;">256</div>
        <div class="res-desc" style="margin-top:4px;">0.25 vCPU per task</div>
      </div>
      <div>
        <div class="metric-label">Memory</div>
        <div class="mono" style="font-size:1.1rem;">512 MiB</div>
        <div class="res-desc" style="margin-top:4px;">per Fargate task</div>
      </div>
      <div>
        <div class="metric-label">OS / Platform</div>
        <div class="mono" style="font-size:1.1rem;">Ubuntu 22.04</div>
        <div class="res-desc" style="margin-top:4px;">via AWS Public ECR base image</div>
      </div>
    </div>
    """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: MONITORING & ALERTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Monitoring & Alerts":
    header(
        "Monitoring & Alerts",
        "5 CloudWatch alarms routing to SNS email — CPU, Memory, 5xx errors, P99 latency, and unhealthy host detection"
    )

    c1, c2, c3 = st.columns(3)
    c1.markdown(metric("CloudWatch Alarms", "5", "across ECS and ALB metrics"), unsafe_allow_html=True)
    c2.markdown(metric("SNS Topic", "1", "email to yogiraj123ano@gmail.com"), unsafe_allow_html=True)
    c3.markdown(metric("Dashboard Widgets", "6", "CPU, Memory, Requests, Latency, 5xx, Tasks"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    section("CloudWatch Alarms", f"""
    <div class="alarm-row alarm-header">
      <div>Alarm</div>
      <div>Metric</div>
      <div>Threshold</div>
      <div>Action</div>
    </div>
    <div class="alarm-row">
      <div><div class="res-name">CPU High</div><div class="res-desc">2 of 2 periods (60s)</div></div>
      <div class="mono" style="font-size:0.76rem;">ECS CPUUtilization</div>
      <div><span class="pill pill-amber">&gt; 80%</span></div>
      <div><span class="pill pill-red">Email + Scale</span></div>
    </div>
    <div class="alarm-row">
      <div><div class="res-name">Memory High</div><div class="res-desc">2 of 2 periods (60s)</div></div>
      <div class="mono" style="font-size:0.76rem;">ECS MemoryUtilization</div>
      <div><span class="pill pill-amber">&gt; 80%</span></div>
      <div><span class="pill pill-red">Email + Scale</span></div>
    </div>
    <div class="alarm-row">
      <div><div class="res-name">5xx Spike</div><div class="res-desc">2 of 2 periods (60s)</div></div>
      <div class="mono" style="font-size:0.76rem;">ALB HTTPCode_Target_5XX_Count</div>
      <div><span class="pill pill-amber">&gt; 10/min</span></div>
      <div><span class="pill pill-red">Email</span></div>
    </div>
    <div class="alarm-row">
      <div><div class="res-name">Unhealthy Hosts</div><div class="res-desc">1 of 1 period (60s)</div></div>
      <div class="mono" style="font-size:0.76rem;">ALB UnHealthyHostCount</div>
      <div><span class="pill pill-amber">&gt; 0</span></div>
      <div><span class="pill pill-red">Email</span></div>
    </div>
    <div class="alarm-row">
      <div><div class="res-name">P99 Latency</div><div class="res-desc">3 of 3 periods (60s)</div></div>
      <div class="mono" style="font-size:0.76rem;">ALB TargetResponseTime p99</div>
      <div><span class="pill pill-amber">&gt; 2s</span></div>
      <div><span class="pill pill-red">Email</span></div>
    </div>
    """)

    col_l, col_r = st.columns(2)

    with col_l:
        section("SNS Configuration", """
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Topic Name</div></div>
          <div class="mono">suyashkadam-prod-alerts</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Protocol</div></div>
          <div class="mono">Email</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Subscriber</div></div>
          <div class="mono">yogiraj123ano@gmail.com</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">Pipeline Failures</div></div>
          <div class="res-desc">EventBridge rule sends pipeline stage failures to SNS</div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">OK Actions</div></div>
          <div class="res-desc">Email also sent on alarm recovery (OK state)</div>
        </div>
        """)

    with col_r:
        section("CloudWatch Dashboard Widgets", """
        <div class="res-row">
          <div style="flex:1"><div class="res-name">ECS CPU Utilization</div></div>
          <div><span class="pill pill-blue">Avg / 60s</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">ECS Memory Utilization</div></div>
          <div><span class="pill pill-blue">Avg / 60s</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">ALB Request Count</div></div>
          <div><span class="pill pill-blue">Sum / 60s</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">ALB Target Response Time</div></div>
          <div><span class="pill pill-blue">p99 / 60s</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">ALB HTTP 5xx Count</div></div>
          <div><span class="pill pill-blue">Sum / 60s</span></div>
        </div>
        <div class="res-row">
          <div style="flex:1"><div class="res-name">ECS Running Task Count</div></div>
          <div><span class="pill pill-blue">Avg / 60s</span></div>
        </div>
        """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BUILDSPEC WALKTHROUGH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Buildspec Walkthrough":
    header(
        "Buildspec Walkthrough",
        "Line-by-line explanation of buildspec.yml — the CodeBuild pipeline definition that builds, tags, and delivers the Docker image"
    )

    st.markdown("""
    <div class="section-card">
      <div class="section-title">Phase: PRE_BUILD</div>
      <div class="code-block">
        <span class="code-comment"># Step 1 — Log in to ECR Private (to push the image we build)</span><br>
        <span class="code-key">aws ecr get-login-password</span> --region $AWS_DEFAULT_REGION | docker login --username AWS ...<br><br>
        <span class="code-comment"># Step 2 — Log in to ECR Public (to pull ubuntu:22.04 base image without Docker Hub rate limits)</span><br>
        <span class="code-key">aws ecr-public get-login-password</span> --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws<br><br>
        <span class="code-comment"># Step 3 — Derive a stable image tag from the git commit SHA (first 7 chars)</span><br>
        <span class="code-key">COMMIT_HASH</span>=<span class="code-val">$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)</span><br>
        <span class="code-key">IMAGE_TAG</span>=<span class="code-val">$COMMIT_HASH</span>  <span class="code-comment"># e.g. 3f64b6b</span><br><br>
        <span class="code-comment"># Step 4 — Write variables to a file because each CodeBuild phase runs a fresh shell</span><br>
        <span class="code-key">echo</span> <span class="code-str">"export IMAGE_URI=..."</span> > /tmp/env.sh
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-card">
      <div class="section-title">Phase: BUILD</div>
      <div class="code-block">
        <span class="code-comment"># Reload variables from file (required — /tmp persists across phases, shell state does not)</span><br>
        <span class="code-key">.</span> /tmp/env.sh<br><br>
        <span class="code-comment"># Build the Docker image using Ubuntu 22.04 + Nginx from AWS Public ECR</span><br>
        <span class="code-comment"># CODEBUILD_SRC_DIR is the root of the unzipped source artifact from CodePipeline</span><br>
        <span class="code-key">docker build</span> --no-cache \<br>
        &nbsp;&nbsp;-t <span class="code-val">$IMAGE_URI</span> &nbsp;&nbsp;&nbsp;&nbsp;<span class="code-comment"># :3f64b6b</span><br>
        &nbsp;&nbsp;-t <span class="code-val">$IMAGE_LATEST</span> &nbsp;&nbsp;<span class="code-comment"># :latest</span><br>
        &nbsp;&nbsp;<span class="code-val">$CODEBUILD_SRC_DIR/app</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-card">
      <div class="section-title">Phase: POST_BUILD</div>
      <div class="code-block">
        <span class="code-key">.</span> /tmp/env.sh<br><br>
        <span class="code-comment"># Push both tags to ECR</span><br>
        <span class="code-key">docker push</span> <span class="code-val">$IMAGE_URI</span><br>
        <span class="code-key">docker push</span> <span class="code-val">$IMAGE_LATEST</span><br><br>
        <span class="code-comment"># Write imagedefinitions.json — this is what CodePipeline's Deploy stage reads</span><br>
        <span class="code-comment"># It tells ECS which container name to update and with which image URI</span><br>
        <span class="code-key">echo</span> <span class="code-str">'[{"name":"nginx-app","imageUri":"&lt;ECR_URL&gt;:3f64b6b"}]'</span> > imagedefinitions.json
      </div>
    </div>
    """, unsafe_allow_html=True)

    section("Artifacts", """
    <div class="res-row">
      <div style="flex:1">
        <div class="res-name">imagedefinitions.json</div>
        <div class="res-desc">Only file CodePipeline's ECS Deploy action needs. Format: [{\"name\":\"container-name\",\"imageUri\":\"full-ecr-uri:tag\"}]</div>
      </div>
      <div><span class="pill pill-green">Required</span></div>
    </div>
    <div class="res-row">
      <div style="flex:1">
        <div class="res-name">discard-paths: yes</div>
        <div class="res-desc">File placed at artifact root, not nested under src/ path</div>
      </div>
      <div><span class="pill pill-blue">Setting</span></div>
    </div>
    """)

    section("Key Design Decisions", """
    <div class="res-row">
      <div style="flex:1">
        <div class="res-name">AWS Public ECR base image</div>
        <div class="res-desc">public.ecr.aws/ubuntu/ubuntu:22.04 — avoids Docker Hub's 100 anonymous pulls/6h rate limit which blocks CodeBuild (shared AWS IPs)</div>
      </div>
    </div>
    <div class="res-row">
      <div style="flex:1">
        <div class="res-name">POSIX dot operator instead of bash source</div>
        <div class="res-desc">CodeBuild executes commands with /bin/sh not bash. source is bash-only; . is POSIX and works in both shells</div>
      </div>
    </div>
    <div class="res-row">
      <div style="flex:1">
        <div class="res-name">Git SHA tagging</div>
        <div class="res-desc">Each image is permanently traceable to its source commit. ECR lifecycle policy retains last 10 tagged images, expires untagged after 7 days</div>
      </div>
    </div>
    <div class="res-row">
      <div style="flex:1">
        <div class="res-name">No ECS update in buildspec</div>
        <div class="res-desc">Previous approach called aws ecs update-service in post_build. Now CodePipeline's Deploy stage handles this via imagedefinitions.json — cleaner separation of concerns</div>
      </div>
    </div>
    """)
